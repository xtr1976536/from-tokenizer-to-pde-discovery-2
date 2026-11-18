"""Pretraining only: grouped holdout, train-only vocabulary, validation selection."""
import argparse, json, hashlib, random, time, os, fcntl
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import DataLoader
from math_tokenizer.corpus import ROOT
from math_tokenizer.eqgpt.author import seed_all, training_namespace
from math_tokenizer.eqgpt.models import build_models
from math_tokenizer.eqgpt.compact_alphabet import train_compact, CompactAlphabet
from math_tokenizer.eqgpt.latex_tokenizers import LatexAdapter
from math_tokenizer.eqgpt.tokenizer_adapters import Adapter
from math_tokenizer.eqgpt.latex_codec import structure_to_latex, LatexParser, key
from math_tokenizer.eqgpt.study3_corpus import paired_rows
from math_tokenizer.eqgpt.round1_runtime import atomic_save
from math_tokenizer.eqgpt.cached_batches import cache_batches

def dump(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(d,ensure_ascii=False,indent=2));q.replace(p)

@torch.no_grad()
def evaluate(model, batches):
    model.eval();total=correct=count=0
    for x,y in batches:
        logits,_=model(x);y=y.reshape(-1);mask=y!=0
        total+=nn.functional.cross_entropy(logits,y,ignore_index=0,reduction='sum').item()
        correct+=((logits.argmax(-1)==y)&mask).sum().item();count+=mask.sum().item()
    return dict(loss=total/count,accuracy=correct/count,tokens=count)

def run(a):
    assert a.prepare_only or torch.cuda.device_count()==1, 'Expose exactly one admitted GPU'
    torch.set_num_threads(4);seed_all(a.seed)
    if not a.prepare_only:torch.cuda.set_per_process_memory_fraction(float(os.environ.get('STAGE1_WORKER_CAP_GIB','8'))*1024**3/torch.cuda.get_device_properties(0).total_memory)
    out=ROOT/'restarts/stage01_20261113/stage1'/str(a.scale);out.mkdir(parents=True,exist_ok=True)
    sources=[json.loads(l) for l in (ROOT/f'restarts/stage01_20261113/stage1/corpora/{a.scale}/sources.jsonl').read_text().splitlines()]
    groups={}
    for r in sources:
        k=repr(key(LatexParser(structure_to_latex(r['gre_ids'])).parse()))
        groups.setdefault(k,[]).append(r)
    keys=sorted(groups);random.Random(525).shuffle(keys)
    target=round(len(sources)*.1);held=set();n=0
    for k in keys:
        if abs(n+len(groups[k])-target)<abs(n-target):held.add(k);n+=len(groups[k])
    train=[r for k in keys if k not in held for r in groups[k]]
    val=[r for k in keys if k in held for r in groups[k]]
    split=dict(seed=525,grouping='canonical AST, commutative add/mul',train=[r['source_id'] for r in train],validation=[r['source_id'] for r in val],source_sha256=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest())
    if (out/'split.json').exists():
        assert json.loads((out/'split.json').read_text())==split
    else:dump(out/'split.json',split)
    assert not set(split['train'])&set(split['validation']) and train and val
    tr=[v for r in train for v in paired_rows(r)];va=[v for r in val for v in paired_rows(r)]
    texts=[structure_to_latex(r['gre_ids']) for r in train]
    if a.arm=='eqgpt_reference':adapter=Adapter('eqgpt')
    else:
        size=int(a.arm.rsplit('_',1)[1]);p=out/'tokenizers'/f'{size}.model.json';p.parent.mkdir(exist_ok=True)
        # Fixed declared alphabet from the existing protocol, not held-out content.
        alphabet=json.loads((ROOT/'restarts/stage01_20261113/stage1/assets/legacy_alphabet_212.json').read_text())['alphabet']
        with (p.parent/f'{size}.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if not p.exists():train_compact('ast_bpe',texts,size,alphabet).save(p)
        adapter=LatexAdapter('ast_bpe',CompactAlphabet.load(p));assert adapter.vocab_size==size
    encode=lambda rows:[adapter.sequence(r['gre_ids'] if a.arm=='eqgpt_reference' else r['latex']) for r in rows]
    ts,vs=encode(tr),encode(va);assert max(map(len,ts+vs))<=72
    assert all(adapter.decode(adapter.sequence(r['latex'])[1:-1])==r['latex'] for r in tr+va) if a.arm!='eqgpt_reference' else True
    if a.prepare_only:
        print('PREFLIGHT_PASS',a.scale,a.arm,len(train),len(val),max(map(len,ts+vs)),flush=True);return
    env=training_namespace('cuda')
    def batches(seqs):
        ds=env['MyDataSet'](seqs)
        return cache_batches(DataLoader(ds,batch_size=128,collate_fn=ds.padding_batch,shuffle=False),'cuda')
    tb,vb=batches(ts),batches(vs)
    model=build_models({a.arm:adapter},72,a.seed,'cuda',n_layers=6)[0][a.arm]
    folder=(out/'smoke' if a.smoke else out)/a.arm/str(a.seed);folder.mkdir(parents=True,exist_ok=True)
    if (folder/'COMPLETE.json').exists():return
    opt=torch.optim.Adam(model.parameters(),lr=1e-4);criterion=nn.CrossEntropyLoss(ignore_index=0)
    scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=200,eta_min=1e-6)
    validation_source_bytes=sum(len(r['latex'].encode()) for r in va)
    train_source_bytes=sum(len(r['latex'].encode()) for r in tr)
    history=[];best=float('inf');best_epoch=0;first=1;early_best=float('inf');bad_epochs=0;epoch=0
    if (folder/'progress.pt').exists():
        checkpoint=torch.load(folder/'progress.pt',map_location='cpu',weights_only=True)
        model.load_state_dict(checkpoint['model']);opt.load_state_dict(checkpoint['optimizer']);scheduler.load_state_dict(checkpoint['scheduler'])
        history=checkpoint['history'];best=checkpoint['best'];best_epoch=checkpoint['best_epoch'];first=len(history)+1
        torch.set_rng_state(checkpoint['rng']);torch.cuda.set_rng_state_all(checkpoint['cuda_rng'])
        early_best=checkpoint['early_best'];bad_epochs=checkpoint['bad_epochs'];epoch=first-1
    for epoch in range(first,3 if a.smoke else 201):
        if bad_epochs>=15:break
        start=time.time();epoch_lr=opt.param_groups[0]['lr'];loss=env['train_step'](model,tb,opt,criterion,1,print_every=None)
        metrics=evaluate(model,vb);assert torch.isfinite(torch.tensor([loss,metrics['loss']])).all()
        metrics['nats_per_byte']=metrics['loss']*metrics['tokens']/validation_source_bytes
        metrics['nats_per_byte_definition']='summed teacher-forced NLL including EOS / rendered LaTeX UTF8 bytes excluding controls'
        train_metrics=evaluate(model,tb)
        train_metrics['nats_per_byte']=train_metrics['loss']*train_metrics['tokens']/train_source_bytes
        history.append(dict(epoch=epoch,learning_rate=epoch_lr,train_loss=loss,train=train_metrics,validation=metrics,seconds=time.time()-start))
        if metrics['loss']<best:
            best=metrics['loss'];best_epoch=epoch;atomic_save(model.state_dict(),folder/'best.pt')
        if metrics['loss']<early_best-1e-5:early_best=metrics['loss'];bad_epochs=0
        else:bad_epochs+=1
        scheduler.step()
        dump(folder/'training.json',dict(scale=a.scale,arm=a.arm,train_sources=len(train),validation_sources=len(val),train_samples=len(ts),validation_samples=len(vs),best_epoch=best_epoch,best_validation_loss=best,history=history,settings=dict(layers=6,positions=72,batch=128,lr=1e-4,clip=1,seed=a.seed,early_stopping=True,patience=15,min_delta=1e-5,schedule='cosine',eta_min=1e-6,T_max=200,max_epochs=200)))
        print(a.scale,a.arm,epoch,loss,metrics['loss'],best_epoch,flush=True)
        atomic_save(dict(model=model.state_dict(),optimizer=opt.state_dict(),scheduler=scheduler.state_dict(),history=history,best=best,best_epoch=best_epoch,early_best=early_best,bad_epochs=bad_epochs,rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),folder/'progress.pt')
        if bad_epochs>=15:break
    dump(folder/'COMPLETE.json',dict(best_epoch=best_epoch,best_validation_loss=best,epochs=epoch,smoke=a.smoke,stopped_by='smoke_limit' if a.smoke else ('early_stopping' if epoch<200 else 'max_epochs'),selection='best validation token cross entropy; frozen before downstream testing'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scale',type=int,required=True);p.add_argument('--arm',required=True);p.add_argument('--prepare-only',action='store_true');p.add_argument('--smoke',action='store_true');p.add_argument('--seed',type=int,choices=[525,526,527],required=True);run(p.parse_args())
