"""Unchanged EqGPT decoder forward, compact300, unconstrained80/20 sampling."""
import hashlib,json,sys,time
from pathlib import Path
import numpy as np
import torch

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'ast_bpe_multifield_v1'))
sys.path.insert(0,str(ROOT.parent/'ast_bpe_multifield_v2'))
from model import build,save,load
from compact_tokenizer import CompactASTBPE
from pipeline import ASTAdapter,select_top,continue_training
from runtime import parse_system,reward,validate_generated_text
sys.path.insert(0,str(ROOT))
from validated_reward import score as validated_score

CORPUS=ROOT.parent/'ast_bpe_multifield_v2/data/corpus/multifield200/coefficient_free'

def batches(rows,size):
    for start in range(0,len(rows),size):
        seqs=[r['tokens'] for r in rows[start:start+size]]
        a=torch.zeros(len(seqs),max(map(len,seqs)),dtype=torch.long)
        for i,s in enumerate(seqs):a[i,:len(s)]=torch.tensor(s)
        yield a[:,:-1],a[:,1:]

def pretrain(out,epochs=200,production=False,device='cpu',batch_size=None,learning_rate=None):
    torch.set_num_threads(2)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[json.loads(l) for l in (CORPUS/'encoded.jsonl').open()]
    train=[r for r in rows if r['split']=='train'];val=[r for r in rows if r['split']=='validation']
    adapter=ASTAdapter(CompactASTBPE.load(CORPUS/'tokenizer300.json'))
    model=build(300,72 if production else 128,device,smoke=not production)
    size=batch_size or (128 if production else 16)
    lr=learning_rate or (1e-4 if production else .002)
    optimizer=torch.optim.Adam(model.parameters(),lr=lr)
    best=float('inf');best_epoch=None;best_state=None
    history=[];started=time.time();rng=np.random.default_rng(525)
    for epoch in range(epochs):
        model.train();losses=[]
        shuffled=[train[i] for i in rng.permutation(len(train))]
        for x,y in batches(shuffled,size):
            x=x.to(device);y=y.to(device)
            optimizer.zero_grad(set_to_none=True);logits,_=model(x)
            loss=torch.nn.functional.cross_entropy(logits.reshape(-1,300),y.reshape(-1),ignore_index=0)
            if not torch.isfinite(loss):raise FloatingPointError('Nonfinite generator loss')
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1);optimizer.step();losses.append(float(loss.detach()))
        model.eval()
        with torch.no_grad():
            total_loss=0.;total_tokens=0
            for x,y in batches(val,size):
                x=x.to(device);y=y.to(device);logits,_=model(x)
                total_loss+=float(torch.nn.functional.cross_entropy(logits.reshape(-1,300),y.reshape(-1),ignore_index=0,reduction='sum'));total_tokens+=int((y!=0).sum())
        validation_loss=total_loss/total_tokens
        history.append(dict(epoch=epoch+1,train_loss=float(np.mean(losses)),validation_loss=validation_loss))
        if validation_loss<best-1e-5:
            best=validation_loss;best_epoch=epoch+1
            best_state={name:value.detach().cpu().clone() for name,value in model.state_dict().items()}
        if (epoch+1)%20==0:print('PRETRAIN',history[-1],flush=True)
    model.load_state_dict(best_state)
    metadata=dict(tokenizer_sha256=hashlib.sha256((CORPUS/'tokenizer300.json').read_bytes()).hexdigest(),corpus_sha256=hashlib.sha256((CORPUS/'equations.jsonl').read_bytes()).hexdigest(),
                  encoded_sha256=hashlib.sha256((CORPUS/'encoded.jsonl').read_bytes()).hexdigest(),splits_sha256=hashlib.sha256((CORPUS/'splits.json').read_bytes()).hexdigest(),
                  tokenizer_backend_sha256=hashlib.sha256((CORPUS/'tokenizer300.backend.json').read_bytes()).hexdigest(),
                  data_role='external equation-text pretraining only',seed=525,history=history,elapsed_seconds=time.time()-started,
                  best_epoch=best_epoch,best_validation_loss=best,selection='minimum token-weighted validation CE, no downstream test selection',
                  maximum_epochs=epochs,batch_size=size,learning_rate=lr,scope='production architecture' if production else 'small CPU integration model')
    save(model,out/'model.pt',**metadata);(out/'training.json').write_text(json.dumps(metadata,indent=2))
    return model,adapter

def sample_batch(model,adapter,seed,batch=64,max_tokens=80):
    max_tokens=min(max_tokens,model.stage2_config['positions']-1)
    device=next(model.parameters()).device
    generator=torch.Generator(device=device).manual_seed(seed)
    prefixes=torch.full((batch,1),adapter.bos,dtype=torch.long,device=device);done=torch.zeros(batch,dtype=torch.bool,device=device);valid=torch.ones(batch,dtype=torch.bool,device=device);sequences=[None]*batch
    model.eval()
    with torch.no_grad():
        for step in range(max_tokens):
            logits,_=model(prefixes);p=logits.reshape(batch,prefixes.shape[1],300)[:,-1].softmax(-1)
            p=p  # Learned-distribution stochastic sampling; uniform exploration disabled
            tokens=torch.multinomial(p,1,generator=generator).squeeze(1)
            for i in torch.nonzero(~done).flatten().tolist():
                token=int(tokens[i])
                if token in (adapter.eos,adapter.pad,adapter.bos):
                    valid[i]=token==adapter.eos;done[i]=True
                    if valid[i]:sequences[i]=prefixes[i,1:].tolist()
            tokens[done]=adapter.pad
            prefixes=torch.cat([prefixes,tokens[:,None]],dim=1)
            if done.all():break
    result=[]
    for seq in sequences:
        if seq is None:result.append(None)
        else:
            try:result.append(adapter.decode(seq))
            except (ValueError,KeyError,UnicodeDecodeError):result.append(None)
    return result

def search(model,adapter,data,out,cycles=5,budget=400,max_batches=5000,validation=None,balance=.5,scorer=None,sft_epochs=5):
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    optimizer=torch.optim.Adam(model.parameters(),lr=1e-5)
    top=[];systems={};history=[];all_rows=[];started=time.time()
    for cycle in range(cycles):
        scored=[];reject={};attempts=0
        for batch_index in range(max_batches):
            texts=sample_batch(model,adapter,525+cycle*1000000+batch_index)
            for text in texts:
                attempts+=1
                try:
                    if text is None:raise ValueError('Invalid or unterminated token sequence')
                    validate_generated_text(text)
                    system=parse_system(text)
                    result=scorer(system) if scorer is not None else (reward(system,data) if validation is None else validated_score(system,data,validation,balance=balance))
                    if not np.isfinite(result['reward']):raise ValueError('Nonfinite score')
                    row=dict(text=text,**result);scored.append(row);systems[text]=system
                except (ValueError,KeyError,TypeError,FloatingPointError,OverflowError,np.linalg.LinAlgError) as exc:
                    reason=str(exc);reject[reason]=reject.get(reason,0)+1
                if len(scored)==budget:break
            if len(scored)==budget:break
            if (batch_index+1)%20==0:print('SAMPLING',cycle+1,'batches',batch_index+1,'success',len(scored),flush=True)
        if len(scored)!=budget:
            (out/'failure.json').write_text(json.dumps(dict(cycle=cycle+1,successful=len(scored),attempts=attempts,rejections=reject),indent=2))
            raise RuntimeError('Successful-system budget incomplete; no hand-coded candidate substitution')
        top=select_top(top+scored)
        losses=continue_training(model,adapter,dict(top10=top),optimizer,model.stage2_config['positions'],epochs=sft_epochs)
        history.append(dict(cycle=cycle+1,success=len(scored),unique_systems=len({r['text'] for r in scored}),attempts=attempts,rejections=reject,sft_losses=losses,best_reward=top[0]['reward']))
        all_rows.extend(scored);(out/'progress.json').write_text(json.dumps(history,indent=2))
        print('SEARCH',cycle+1,'success',budget,'attempts',attempts,'best',top[0]['reward'],flush=True)
    result=dict(status='COMPLETE',cycles=cycles,budget_per_cycle=budget,history=history,top10=top,top1=top[0],model_generated=True,candidate_substitution=False,elapsed_seconds=time.time()-started)
    (out/'result.json').write_text(json.dumps(result,indent=2));(out/'candidates.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in all_rows))
    return systems[top[0]['text']],result

if __name__=='__main__':pretrain(ROOT/'runs/pretrain_cpu')
