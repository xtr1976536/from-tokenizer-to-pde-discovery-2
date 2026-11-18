"""Estimate a fixed screening threshold on train-only, deterministic samples.

Reproduces the 512-attempt vocab320 smoke stream, retaining ALL fit details.
The quantile is across candidates, using each candidate's weakest equation.
"""
import argparse,json,signal,time
from pathlib import Path
from collections import Counter
import numpy as np
import torch
from .acceptance import write,sha
from .generator import ASTBPEGenerator
from .data import SimulationData
from .implicit_backend import ImplicitBackend
from .corpus_work.constrained_sampling import sample_batch
from .contracts import InvalidCandidate
from .scoring import fit_details


def deadline(*_):raise InvalidCandidate('Calibration hard deadline (45 seconds)')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--frozen',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--attempts',type=int,default=512)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    cfg=json.loads(Path(__file__).with_name('config.json').read_text())
    torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.18)
    freeze=json.loads(a.frozen.read_text())
    entry=next(e for e in freeze['models'] if e['split']=='811' and e['vocab']==320)
    folder=Path(entry['folder']);g=ASTBPEGenerator(folder/'ast-bpe-320.json',device='cuda',random_fraction=0.)
    g.load(folder/'best.pt');g.optimizer=None
    data=SimulationData(a.manifest,cfg);by={}
    for w in data.roles['train_fit']:by.setdefault(w.trajectory,w)
    windows=[by[name] for name in sorted(by)[:2]]
    backend=ImplicitBackend(**cfg['numerics']);records=[];rejections=Counter();start=time.monotonic()
    signal.signal(signal.SIGALRM,deadline)
    for emitted in range(0,a.attempts,8):
        values=sample_batch(g.model,g.adapter,202611160100+emitted,batch=min(8,a.attempts-emitted),
            max_tokens=g.max_tokens,random_fraction=0.,residual_zero_rhs=True)
        for text in values:
            rec=dict(index=len(records),text=text,status='INVALID')
            try:
                if text is None:raise InvalidCandidate('Invalid or unterminated sample')
                signal.alarm(45);system=backend.parse(text)
                details=fit_details(system,backend,data,windows)
                rec.update(status='FIT_PASS',anchor_indices=system.anchor_indices,**details,
                    minimum_equation_r2=min(details['r2_per_equation']))
            except InvalidCandidate as error:
                rec['error']=str(error);rejections[str(error)]+=1
            finally:signal.alarm(0)
            records.append(rec)
        write(a.output/'progress.json',dict(attempts=len(records),records=records,
            rejections=dict(rejections),seconds=time.monotonic()-start))
        print('calibration',len(records),'fit',sum(r['status']=='FIT_PASS' for r in records),flush=True)
    valid=[r for r in records if r['status']=='FIT_PASS']
    scores=np.array([r['minimum_equation_r2'] for r in valid])
    if len(scores)<20:raise RuntimeError('Insufficient finite three-equation fits for threshold calibration')
    threshold=float(np.quantile(scores,.4))
    table=[]
    for t in sorted(set([threshold,0.,.001,.005,.01,.03,.05,.1,.3])):
        n=int(np.sum(scores>t));table.append(dict(threshold=t,retained=n,
            fit_rejection_fraction=1-n/len(scores),total_rejection_fraction=1-n/len(records)))
    result=dict(status='CALIBRATED_TRAIN_ONLY',attempts=len(records),fit_candidates=len(valid),
        fixed_threshold=threshold,statistic='minimum of three batch-mean equation R2',
        target_rejection_fraction_among_finite_fits=.4,
        actual_rejection_fraction_among_finite_fits=float(np.mean(scores<=threshold)),
        quantiles={str(q):float(np.quantile(scores,q)) for q in [0,.1,.25,.4,.5,.6,.75,.9,1.]},
        threshold_comparison=table,records=records,windows=[w.__dict__ for w in windows],
        seconds=time.monotonic()-start,test_read=False,validation_read=False,
        checkpoint_unchanged=sha(folder/'best.pt')==entry['checkpoint_sha256'])
    write(a.output/'result.json',result);data.close();print('THRESHOLD',threshold,flush=True)


if __name__=='__main__':main()
