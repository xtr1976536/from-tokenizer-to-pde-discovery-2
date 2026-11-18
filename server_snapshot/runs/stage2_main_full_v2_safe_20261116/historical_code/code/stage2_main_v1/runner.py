"""Batch-online search/SFT, independent epoch validation, frozen test barrier.

The three-field direct-LaTeX adapter is optional until a trained checkpoint and
the data-specific acceptance checks are frozen.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import random
import time
from .contracts import InvalidCandidate, check_capabilities
from .data import sha256
from .scoring import reward, prediction_score, penalty,qualified_fit


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
    temporary.replace(path)


def fingerprint(config, data):
    root=Path(__file__).parent
    files=set(root.glob('*.py'))|set((root/'corpus_work').glob('*.py'))
    files.update(root/'legacy_eqgpt/layout'/p for p in ('ast_bpe_multifield_v1/model.py','ast_bpe_multifield_v1/ast_runtime.py','ast_bpe_multifield_v2/coefficient_free.py','分词器-pde发现/eqgpt_original/code/gpt_model.py'))
    sources = {str(p.relative_to(root)):sha256(p) for p in sorted(files)}
    raw = json.dumps({'config': config, 'manifest': sha256(data.path), 'sources':sources}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def window_batches(windows, size, seed):
    """Shuffle each trajectory, then interleave; every window appears once."""
    rng = random.Random(seed); groups = {}
    for w in windows: groups.setdefault(w.trajectory, []).append(w)
    for rows in groups.values(): rng.shuffle(rows)
    ordered = []
    while groups:
        ids = list(groups); rng.shuffle(ids)
        for name in ids:
            ordered.append(groups[name].pop())
            if not groups[name]: del groups[name]
    return [ordered[i:i+size] for i in range(0,len(ordered),size)]


def candidates(generator, numerics, count, attempts_limit, seed, score, progress=None):
    accepted = []; rejects = Counter(); structures = set(); attempted = 0; parsed = 0
    started=time.monotonic()
    def report(**details):
        if progress is not None:
            progress(dict(attempts=attempted,successful=len(accepted),target=count,parsed=parsed,
                unique_structures=len(structures),rejections=dict(rejects),seconds=time.monotonic()-started,**details))
    report()
    while len(accepted) < count and attempted < attempts_limit:
        attempted += 1
        try:
            report(candidate_phase='generating',candidate_seed=seed+attempted)
            text = generator.sample(seed+attempted)
            if not text: raise InvalidCandidate('invalid_or_unterminated_text')
            report(candidate_phase='parsing',candidate_seed=seed+attempted,candidate_text=text)
            system = numerics.parse(text); parsed += 1
            report(candidate_phase='scoring',candidate_seed=seed+attempted,candidate_text=text)
            row = dict(score(system), text=text, structure_key=numerics.structure_key(system))
            if not math.isfinite(row['reward']): raise InvalidCandidate('nonfinite_reward')
            accepted.append(row); structures.add(row['structure_key'])
        except InvalidCandidate as e:
            rejects[str(e)] += 1
        if attempted%10==0 or len(accepted)==count:report()
    stats = {'attempts': attempted, 'successful': len(accepted), 'invalid': attempted-len(accepted),
             'unique_structures': len(structures), 'parsed': parsed,
             'integration_pass_rate_among_parsed': len(accepted)/parsed if parsed else 0,
             'rejections': dict(rejects)}
    if len(accepted) != count:
        raise CandidateBudgetIncomplete(stats)
    return accepted, stats


class CandidateBudgetIncomplete(RuntimeError):
    def __init__(self, stats):
        super().__init__('Successful candidate budget incomplete; no formula fallback')
        self.stats = stats


def run(config, data, generator, numerics, output, weight, resume=False):
    if weight not in config['reward_lambdas']: raise ValueError('Unplanned reward lambda')
    if not all(config['readiness'].values()): raise ValueError('Readiness audits incomplete')
    if config['baseline'].get('required_for_model_run',False) and not config['baseline']['checkpoint_selection_audited']:
        raise ValueError('Baseline checkpoint comparison not frozen')
    check_capabilities(generator, numerics, config)
    out = Path(output)
    identity = fingerprint(config, data)
    if not resume:
        out.mkdir(parents=True, exist_ok=False)
        write(out/'config.json',config)
        state = {'identity': identity, 'weight': weight, 'epoch': 0, 'next_batch': 0,
                 'bad_epochs': 0, 'reference_rmse': None, 'best_rmse': None,
                 'best_epoch': None, 'best_text': None, 'finished': False}
    else:
        state = json.loads((out/'resume.json').read_text())
        if state['identity'] != identity or state['weight'] != weight:
            raise ValueError('Resume configuration/data/weight mismatch')
        generator.load(str(out/state['generator_checkpoint']))
        if state['finished']:
            write_frozen(out, state, identity, weight)
            return state
    scale = data.training_scale()
    if hasattr(numerics,'on_progress'):
        numerics.on_progress=lambda details:write(out/'numerics_progress.json',details)
    write(out/'normalization.json', {'mean':data.training_mean().tolist(),'scale':scale.tolist(), 'source':'unique train_fit visible frames only','prediction_score_version':'train_fit_zscore_energy_v2'})

    def save_state():
        # A new checkpoint is written before committing resume.json, so a failed
        # save never pairs old counters with partially updated generator weights.
        relative = f"checkpoints/epoch{state['epoch']:03d}_next{state['next_batch']:06d}.bin"
        (out/'checkpoints').mkdir(exist_ok=True)
        generator.save(str(out/relative)); state['generator_checkpoint'] = relative
        write(out/'resume.json', state)
        retention=config.get('checkpoint_retention')
        if retention is not None:
            # Only this run's superseded resume checkpoints; best models remain.
            keep=max(2,int(retention))
            paths=sorted((out/'checkpoints').glob('epoch*_next*.bin'),key=lambda p:p.stat().st_mtime)
            for old in paths[:-keep]:
                if old!=out/relative:old.unlink()

    if not resume: save_state()
    for epoch in range(state['epoch'], config['maximum_outer_epochs']):
        batches = window_batches(data.roles['train_fit'], config['batch_size'], config['seed']+epoch)
        for index in range(state['next_batch'],len(batches)):
            seed = config['seed'] + (epoch*len(batches)+index)*config['maximum_sampling_attempts']
            try:
                rows, stats = candidates(generator,numerics,config['successful_candidates_per_batch'],
                    config['maximum_sampling_attempts'],seed,
                    lambda s: reward(s,numerics,data,batches[index],scale,weight,config['sparsity_coefficient'],config['candidate_filter']['minimum_equation_mean_r2']),
                    progress=lambda stats:write(out/'progress.json',dict(stage='train_candidates',epoch=epoch+1,batch=index+1,batches=len(batches),**stats)))
            except CandidateBudgetIncomplete as e:
                write(out/f'failures/epoch{epoch+1}_batch{index+1}.json',e.stats); raise
            top = sorted(rows,key=lambda x:x['reward'],reverse=True)[:config['top_k']]
            write(out/'progress.json',dict(stage='sft',epoch=epoch+1,batch=index+1,batches=len(batches),successful=len(rows),sft_epochs=config['sft']['epochs']))
            # No pooling of scores/Top10 across different window batches.
            sft = generator.sft([r['text'] for r in top],config['sft'])
            if (sft.get('epochs') != config['sft']['epochs'] or sft.get('early_stopping') is not False
                    or sft.get('settings') != config['sft']):
                raise RuntimeError('SFT plugin did not honor fixed cosine/no-early-stop settings')
            write(out/f'batches/epoch{epoch+1:03d}_batch{index+1:06d}.json',
                  {'windows':[w.__dict__ for w in batches[index]], 'statistics':stats, 'top10':top,'sft':sft})
            state.update(epoch=epoch,next_batch=index+1); save_state()
        def select_score(system):
            fit=qualified_fit(system,numerics,data,batches[0],config['candidate_filter']['minimum_equation_mean_r2'])
            result = prediction_score(system,numerics,data,'validation_select',scale)
            return {'reward':penalty(numerics.term_counts(system),config['sparsity_coefficient'])*result['prediction_score'],
                    'selection_metrics':result,'fit_filter':fit}
        try:
            rows,stats = candidates(generator,numerics,config['selection_candidates'],
                config['maximum_sampling_attempts'],config['seed']+10**12+epoch*config['maximum_sampling_attempts'],select_score,
                progress=lambda stats:write(out/'progress.json',dict(stage='validation_candidates',epoch=epoch+1,**stats)))
        except CandidateBudgetIncomplete as e:
            write(out/f'failures/epoch{epoch+1}_selection.json',e.stats); raise
        selected = max(rows,key=lambda r:r['reward'])
        # Only one selected shared structure is evaluated on the stopping set.
        metrics = prediction_score(numerics.parse(selected['text']),numerics,data,'validation_stop',scale)
        current = metrics['normalized_joint_rmse']
        if state['best_rmse'] is None or current < state['best_rmse']:
            state.update(best_rmse=current,best_epoch=epoch+1,best_text=selected['text'])
            generator.save(str(out/f'best_epoch{epoch+1:03d}.bin'))
            state['best_generator_checkpoint'] = f'best_epoch{epoch+1:03d}.bin'
        # Reference only moves after >=1% cumulative improvement; best save is
        # independent, so even subthreshold improvements retain the true best.
        reference = state['reference_rmse']
        if reference is None or (reference > 0 and current <= reference*(1-config['relative_min_improvement'])):
            state.update(reference_rmse=current,bad_epochs=0)
        else: state['bad_epochs'] += 1
        write(out/f'validation/epoch{epoch+1:03d}.json',
              {'selection_candidates':rows,'statistics':stats,'selected':selected,'stop_metrics':metrics})
        state.update(epoch=epoch+1,next_batch=0)
        if state['bad_epochs'] >= config['early_stop_patience']:
            state['finished'] = True
        if state['epoch'] == config['maximum_outer_epochs']: state['finished'] = True
        save_state(); write(out/'access_log.json',data.access)
        if state['finished']: break
    write_frozen(out, state, identity, weight)
    return state


def write_frozen(out, state, identity, weight):
    write(out/'frozen_model.json', {'identity':identity,'lambda':weight,'structure':state['best_text'],
          'best_epoch':state['best_epoch'],'validation_stop_rmse':state['best_rmse'],
          'generator_checkpoint':state['best_generator_checkpoint'],
          'test_used_for_selection':False,'test_coefficients':'fit each visible 20-frame prefix'})



def evaluate_frozen(config,data,numerics,output):
    """Separate explicit entry; training itself never invokes test evaluation."""
    out = Path(output); frozen = json.loads((out/'frozen_model.json').read_text())
    state = json.loads((out/'resume.json').read_text())
    if not state['finished'] or frozen['identity'] != fingerprint(config,data):
        raise ValueError('Model and settings must be frozen before test')
    if (out/'test_metrics.json').exists(): raise ValueError('Test has already been evaluated')
    data.test_unlocked = True
    result = prediction_score(numerics.parse(frozen['structure']),numerics,data,'test',data.training_scale())
    write(out/'test_metrics.json',result); write(out/'test_access_log.json',data.access)
    return result
