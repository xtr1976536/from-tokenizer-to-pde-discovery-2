"""Fresh, bounded Cylinder acceptance; never changes formal readiness flags.

One frozen model, two training trajectories, one window per validation role.
Uses production scoring, numerical backend and SFT; tests stay locked.
"""
import argparse
from collections import Counter,deque
import json
from pathlib import Path
import signal
import time
import torch
from .acceptance import sha,write
from .contracts import InvalidCandidate
from .corpus_work.constrained_sampling import sample_batch
from .data import SimulationData
from .generator import ASTBPEGenerator
from .safe_backend import SafeBackend
from .real_chain_smoke import weights
from .scoring import reward,qualified_fit,prediction_score,penalty


def deadline(*_):
    raise InvalidCandidate('Smoke per-candidate hard deadline (120 seconds)')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--frozen',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--attempts',type=int,default=256)
    ap.add_argument('--stage-seconds',type=int,default=900)
    ap.add_argument('--split',default='811',choices=['811','622'])
    ap.add_argument('--vocab',type=int,default=192)
    ap.add_argument('--sampling-seed',type=int,default=202611160100)
    ap.add_argument('--train-windows',type=int,default=2)
    a=ap.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=False)
    cfg=json.loads(Path(__file__).with_name('config.json').read_text())
    write(out/'scope.json',dict(kind='fresh generation reduced Cylinder chain',split=a.split,vocab=a.vocab,
        training_candidates=2,validation_candidates=1,attempts_per_stage=a.attempts,
        sampling_batch=8,max_tokens=1024,random_fraction=0.,minimum_equation_r2=cfg['candidate_filter']['minimum_equation_mean_r2'],
        sft=cfg['sft'],formal_configuration_changed=False,full_search_started=False,
        production_sampling_attempts=cfg['maximum_sampling_attempts']))
    start=time.monotonic();torch.set_num_threads(4)
    torch.cuda.set_per_process_memory_fraction(.18)
    frozen=json.loads(a.frozen.read_text())
    entry=next(e for e in frozen['models'] if e['split']==a.split and e['vocab']==a.vocab)
    folder=Path(entry['folder']);assert sha(folder/'best.pt')==entry['checkpoint_sha256']
    g=ASTBPEGenerator(folder/f'ast-bpe-{a.vocab}.json',device='cuda',random_fraction=0.)
    g.load(folder/'best.pt');g.optimizer=None
    data=SimulationData(a.manifest,cfg)
    first_by_trajectory={}
    for w in data.roles['train_fit']:first_by_trajectory.setdefault(w.trajectory,w)
    train=[first_by_trajectory[k] for k in sorted(first_by_trajectory)[:a.train_windows]]
    data.roles={role:(train if role=='train_fit' else rows[:1]) for role,rows in data.roles.items()}
    scale=data.training_scale();backend=SafeBackend(**cfg['numerics'],**cfg.get('resource_limits',{}))
    signal.signal(signal.SIGALRM,deadline)
    write(out/'windows.json',{role:[w.__dict__ for w in rows] for role,rows in data.roles.items()})

    def collect(stage,count,seed,score):
        queue=deque();rows=[];rejects=Counter();attempted=0;emitted=0;stage_start=time.monotonic();fit_reject_examples=[]
        while attempted<a.attempts and len(rows)<count and time.monotonic()-stage_start<a.stage_seconds:
            if not queue:
                values=sample_batch(g.model,g.adapter,seed+emitted,batch=min(8,a.attempts-emitted),
                    max_tokens=g.max_tokens,random_fraction=0.,residual_zero_rhs=True)
                queue.extend(values);emitted+=len(values)
            attempted+=1;text=queue.popleft()
            try:
                if text is None:raise InvalidCandidate('Invalid or unterminated sample')
                signal.alarm(120)
                system=backend.parse(text)
                row=dict(text=text,structure_key=system.structure_key,anchor_indices=system.anchor_indices,
                         **score(system))
                rows.append(row)
            except InvalidCandidate as error:
                rejects[str(error)]+=1
                if 'Fit quality gate' in str(error) and len(fit_reject_examples)<8:
                    fit_reject_examples.append(dict(text=text,last_window_r2=backend.last_diagnostics.get('r2')))
            finally:signal.alarm(0)
            write(out/(stage+'-progress.json'),dict(attempts=attempted,generated=emitted,
                accepted=len(rows),rejections=dict(rejects),rows=rows,fit_reject_examples=fit_reject_examples,seconds=time.monotonic()-start))
            if attempted%8==0 or rows:print(stage,attempted,'accepted',len(rows),flush=True)
        return rows,dict(attempts=attempted,generated=emitted,accepted=len(rows),rejections=dict(rejects))

    result=dict(status='IN_PROGRESS',split=a.split,vocab=a.vocab)
    try:
        scores,stats=collect('train',2,a.sampling_seed,
            lambda system:reward(system,backend,data,train,scale,1.,cfg['sparsity_coefficient'],cfg['candidate_filter']['minimum_equation_mean_r2']))
        result['train_statistics']=stats
        if len(scores)!=2:
            result['status']='FAILED_FRESH_TRAIN_CANDIDATE_BUDGET';return
        top=sorted(scores,key=lambda row:row['reward'],reverse=True)
        before=weights(g);sft=g.sft([row['text'] for row in top],cfg['sft']);after=weights(g)
        assert before!=after and sft['epochs']==5
        g.save(out/'post-sft.pt');g.load(out/'post-sft.pt');assert weights(g)==after
        assert g.random_fraction==0.
        write(out/'sft.json',dict(top=top,sft=sft,before=before,after=after,restore_equal=True))
        result.update(sft_epochs=5,weights_changed=True,restore_equal=True)
        # A fresh queue is created: no pre-SFT generated formula enters selection.
        def select_score(system):
            fit=qualified_fit(system,backend,data,train,cfg['candidate_filter']['minimum_equation_mean_r2'])
            metrics=prediction_score(system,backend,data,'validation_select',scale)
            return dict(reward=penalty(system.term_counts,.2)*metrics['prediction_score'],
                        fit_filter=fit,selection_metrics=metrics)
        selected,stats=collect('select',1,a.sampling_seed+10**6,select_score)
        result['selection_statistics']=stats
        if not selected:
            result['status']='FAILED_FRESH_VALIDATION_CANDIDATE_BUDGET';return
        best=selected[0]
        signal.alarm(120)
        try:stop=prediction_score(backend.parse(best['text']),backend,data,'validation_stop',scale)
        finally:signal.alarm(0)
        write(out/'selected.json',dict(selected=best,stop_metrics=stop))
        result.update(status='PASS_FRESH_REDUCED_CYLINDER_CHAIN',validation_select=True,
                      validation_stop=True,stop_metrics=stop)
    except InvalidCandidate as error:
        result.update(status='FAILED_NUMERICAL_ACCEPTANCE',error=str(error))
    finally:
        signal.alarm(0)
        result.update(seconds=time.monotonic()-start,access=data.access,
            test_read=any(item['role']=='test' for item in data.access),
            train_future_read=any(item['role']=='train_fit' and item['part']=='target' for item in data.access),
            frozen_checkpoint_unchanged=sha(folder/'best.pt')==entry['checkpoint_sha256'])
        assert not result['test_read'] and not result['train_future_read'] and result['frozen_checkpoint_unchanged']
        write(out/'result.json',result);data.close();backend.close()
        print(result['status'],flush=True)


if __name__=='__main__':main()
