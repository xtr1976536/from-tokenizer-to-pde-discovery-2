"""Direct-LaTeX three-field AST-BPE generator using Stage1 GPT architecture."""
from pathlib import Path
import sys,json,random,math,copy
from hashlib import sha256
import numpy as np
import torch
from .legacy_eqgpt.layout.ast_bpe_multifield_v1.model import build
sys.path.insert(0,str(Path(__file__).parent/'corpus_work'))
from .corpus_work.curation import ROOT
sys.path.insert(0,str(ROOT/'math_tokenizer_project_release/src'))
from .corpus_work.compact_ast_bpe import CompactAlphabet
from .corpus_work.constrained_sampling import sample_batch

DEFAULT_PRETRAIN=dict(maximum_epochs=80,cosine_epochs=30,learning_rate=1e-4,minimum_learning_rate=1e-6,
    patience=15,min_delta=1e-4,minimum_epochs=25,weight_decay=1e-2,batch_size=128,token_budget=8192,gradient_clip=1.)


class Adapter:
    pad=0;eos=1;bos=2
    def __init__(self,path):
        self.path=Path(path);self.tokenizer=CompactAlphabet.load(self.path)
        self.vocab_size=len(self.tokenizer.vocab)+3
        self.hash=sha256(json.dumps([b.hex() for b in self.tokenizer.vocab]).encode()).hexdigest()
    def encode(self,text):return [self.bos]+[i+3 for i in self.tokenizer.encode(text)]+[self.eos]
    def decode(self,ids):
        if any(i<3 or i>=self.vocab_size for i in ids):raise ValueError('Control token inside text')
        return self.tokenizer.decode([i-3 for i in ids])


def cosine_lr(epoch,initial,minimum,period):
    if period<=0 or not 0<minimum<=initial:raise ValueError('Invalid cosine schedule')
    return minimum+.5*(initial-minimum)*(1+math.cos(math.pi*min(epoch/period,1.)))


def optimizer_for(model,lr,weight_decay):
    # Adam's coupled weight_decay is the gradient of the L2 penalty; exclude
    # one-dimensional bias/normalization parameters. This is not AdamW.
    decay=[p for p in model.parameters() if p.requires_grad and p.ndim>=2]
    plain=[p for p in model.parameters() if p.requires_grad and p.ndim<2]
    return torch.optim.Adam([dict(params=decay,weight_decay=weight_decay),dict(params=plain,weight_decay=0.)],lr=lr)


class ASTBPEGenerator:
    fields=('u','v','p');equation_count=3;spatial_dimensions=2
    def __init__(self,tokenizer_path,device='cpu',seed=525,positions=2048,smoke=False,max_tokens=1024,random_fraction=0.):
        self.adapter=Adapter(tokenizer_path);self.device=torch.device(device);self.seed=seed
        self.model=build(self.adapter.vocab_size,positions,device,seed,smoke)
        self.max_tokens=min(max_tokens,positions-1);self.random_fraction=random_fraction
        self.steps=0;self.optimizer=None;self.training_state={};self.last_sampling={}
    def sample(self,seed):
        result=sample_batch(self.model,self.adapter,seed,batch=1,max_tokens=self.max_tokens,random_fraction=self.random_fraction,residual_zero_rhs=True)[0]
        self.last_sampling=dict(seed=seed,valid=result is not None,max_tokens=self.max_tokens)
        return result
    def _batches(self,texts,settings,shuffle=False,seed=525):
        sequences=[self.adapter.encode(t) for t in texts]
        if any(len(s)>self.model.stage2_config['positions'] for s in sequences):raise ValueError('Formula exceeds model context; truncation forbidden')
        order=list(range(len(sequences)))
        if shuffle:random.Random(seed).shuffle(order)
        batch=[];length=0
        def tensor(rows):
            a=torch.zeros((len(rows),max(map(len,rows))),dtype=torch.long,device=self.device)
            for i,s in enumerate(rows):a[i,:len(s)]=torch.tensor(s,device=self.device)
            return a[:,:-1],a[:,1:]
        for i in order:
            s=sequences[i];proposed=max(length,len(s))
            if batch and (len(batch)>=settings['batch_size'] or proposed*(len(batch)+1)>settings['token_budget']):
                yield tensor(batch);batch=[];length=0
            batch.append(s);length=max(length,len(s))
        if batch:yield tensor(batch)
    def _epoch(self,texts,settings,train,epoch):
        self.model.train(train);total=0.;tokens=0
        with torch.set_grad_enabled(train):
            for x,y in self._batches(texts,settings,train,self.seed+epoch):
                logits,_=self.model(x);count=int((y!=0).sum())
                loss=torch.nn.functional.cross_entropy(logits.reshape(-1,self.adapter.vocab_size),y.reshape(-1),ignore_index=0,reduction='sum')
                if not torch.isfinite(loss):raise FloatingPointError('Nonfinite token loss')
                if train:
                    self.optimizer.zero_grad(set_to_none=True);(loss/count).backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(),settings['gradient_clip']);self.optimizer.step();self.steps+=1
                total+=float(loss.detach());tokens+=count
        if not tokens:raise ValueError('Empty formula split')
        return dict(token_cross_entropy=total/tokens,nats_per_byte=total/sum(len(t.encode()) for t in texts),tokens=tokens)
    def pretrain(self,train_texts,validation_texts,output,settings=None,resume=False):
        cfg={**DEFAULT_PRETRAIN,**(settings or {})};out=Path(output);out.mkdir(parents=True,exist_ok=True)
        train_hash=sha256(json.dumps(train_texts).encode()).hexdigest();validation_hash=sha256(json.dumps(validation_texts).encode()).hexdigest()
        if set(train_texts)&set(validation_texts):raise ValueError('Identical train/validation formula leakage')
        self.optimizer=optimizer_for(self.model,cfg['learning_rate'],cfg['weight_decay'])
        state=dict(history=[],best_loss=float('inf'),early_reference=float('inf'),bad_epochs=0,best_epoch=0,
                   settings=cfg,train_sha256=train_hash,validation_sha256=validation_hash)
        progress=out/'progress.pt'
        if resume:
            self.load(progress);state=self.training_state
            if state['settings']!=cfg or state['train_sha256']!=train_hash or state['validation_sha256']!=validation_hash:raise ValueError('Resume data/settings mismatch')
        elif progress.exists() or (out/'best.pt').exists():raise FileExistsError('Existing pretrain output; choose resume or new directory')
        for epoch in range(len(state['history']),cfg['maximum_epochs']):
            if len(state['history'])>=cfg['minimum_epochs'] and state['bad_epochs']>=cfg['patience']:break
            lr=cosine_lr(epoch,cfg['learning_rate'],cfg['minimum_learning_rate'],cfg['cosine_epochs'])
            for group in self.optimizer.param_groups:group['lr']=lr
            train=self._epoch(train_texts,cfg,True,epoch);val=self._epoch(validation_texts,cfg,False,epoch)
            state['history'].append(dict(epoch=epoch+1,learning_rate=lr,train=train,validation=val))
            value=val['token_cross_entropy'];improved=value<state['best_loss']
            if improved:state['best_loss']=value;state['best_epoch']=epoch+1
            if value<state['early_reference']-cfg['min_delta']:state['early_reference']=value;state['bad_epochs']=0
            else:state['bad_epochs']+=1
            self.training_state=state
            if improved:self.save(out/'best.pt')
            self.save(progress)
            (out/'training.json').write_text(json.dumps(state,indent=2)+'\n')
        # Model chosen by validation only. Final test metrics are not read here.
        final_state=copy.deepcopy(state);self.load(out/'best.pt');self.training_state=final_state
        (out/'COMPLETE.json').write_text(json.dumps(dict(best_epoch=state['best_epoch'],epochs=len(state['history']),
            selection='minimum validation token CE',test_read=False,settings=cfg),indent=2)+'\n')
        return final_state
    def sft(self,texts,settings):
        if not texts:raise ValueError('No selected candidates for SFT')
        cfg={**DEFAULT_PRETRAIN,**settings};cfg['weight_decay']=settings.get('weight_decay',0.);epochs=int(settings['epochs'])
        if settings.get('early_stopping',False):raise ValueError('Online SFT does not use early stopping')
        self.optimizer=optimizer_for(self.model,cfg['learning_rate'],cfg['weight_decay'])
        history=[]
        for epoch in range(epochs):
            lr=cosine_lr(epoch,cfg['learning_rate'],cfg['minimum_learning_rate'],epochs)
            for group in self.optimizer.param_groups:group['lr']=lr
            history.append(self._epoch(texts,cfg,True,epoch))
        return dict(epochs=epochs,early_stopping=False,settings=settings,history=history)
    def save(self,path):
        payload=dict(format='stage2-direct-latex-generator-v1',config=self.model.stage2_config,
            tokenizer_hash=self.adapter.hash,tokenizer_path=str(self.adapter.path),model=self.model.state_dict(),
            optimizer=self.optimizer.state_dict() if self.optimizer else None,steps=self.steps,seed=self.seed,training_state=self.training_state,
            optimizer_groups=[{k:v for k,v in g.items() if k!='params'} for g in self.optimizer.param_groups] if self.optimizer else None,
            random_fraction=self.random_fraction,max_tokens=self.max_tokens,
            rng=dict(torch=torch.get_rng_state(),python=random.getstate(),numpy=(np.random.get_state()[0],np.random.get_state()[1].tolist(),*np.random.get_state()[2:]),
                     cuda=torch.cuda.get_rng_state(self.device) if self.device.type=='cuda' else None))
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');torch.save(payload,tmp);tmp.replace(path)
    def load(self,path):
        payload=torch.load(path,map_location='cpu',weights_only=True)
        if payload['format']!='stage2-direct-latex-generator-v1' or payload['tokenizer_hash']!=self.adapter.hash or payload['config']!=self.model.stage2_config:raise ValueError('Checkpoint architecture/tokenizer mismatch')
        self.model.load_state_dict(payload['model']);self.steps=payload['steps'];self.seed=payload.get('seed',self.seed);self.training_state=payload['training_state']
        # Sampling policy belongs to this execution, not the old checkpoint.
        # A saved 20% mixture must not silently override a model-only request.
        self.max_tokens=payload['max_tokens']
        if payload['optimizer'] is not None:
            self.optimizer=optimizer_for(self.model,1e-4,0.)
            self.optimizer.load_state_dict(payload['optimizer'])
            for state in self.optimizer.state.values():
                for key,value in state.items():
                    if torch.is_tensor(value):state[key]=value.to(self.device)
        torch.set_rng_state(payload['rng']['torch']);random.setstate(payload['rng']['python'])
        n=payload['rng']['numpy'];np.random.set_state((n[0],np.asarray(n[1],dtype=np.uint32),*n[2:]))
        if payload['rng']['cuda'] is not None and self.device.type=='cuda':torch.cuda.set_rng_state(payload['rng']['cuda'],self.device)


def factory(config):
    from .safe_backend import SafeBackend
    settings=config.get('generator',{})
    if not settings.get('checkpoint'):raise ValueError('A selected pretrained checkpoint is required before online search')
    generator=ASTBPEGenerator(settings['tokenizer'],device=settings.get('device','cpu'),positions=settings.get('positions',2048),
        seed=config.get('seed',525),smoke=settings.get('smoke',False),max_tokens=settings.get('max_tokens',1024),random_fraction=settings.get('random_fraction',0.))
    generator.load(settings['checkpoint'])
    if generator.steps==0:raise ValueError('Untrained checkpoint cannot start a formal search')
    return generator,SafeBackend(**config.get('numerics',{}),**config.get('resource_limits',{}))
