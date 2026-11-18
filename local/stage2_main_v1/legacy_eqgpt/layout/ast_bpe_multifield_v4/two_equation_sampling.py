"""Count-only byte automaton: exactly one LaTeX equation separator.
No restriction on variables, terms, operators, equality, or PDE structure.
Handles merged BPE tokens and separators crossing token boundaries.
"""
import torch

def build_tables(adapter):
 vocab=adapter.tokenizer.vocab;V=len(vocab)+3
 nxt=torch.full((8,V),-1,dtype=torch.long)
 for state in range(8):
  for tid,raw in enumerate(vocab,3):
   count=state//4;slash=(state//2)%2;content=bool(state%2);ok=True
   for b in raw:
    if b==92:
     if slash:
      if count or not content:ok=False;break
      count=1;slash=0;content=False
     else:slash=1
    else:
     slash=0
     if b not in (9,10,13,32):content=True
   if ok:nxt[state,tid]=count*4+slash*2+int(content)
 dist=torch.full((8,),1000,dtype=torch.long)
 for s in range(8):
  if s//4==1 and s%2:dist[s]=1
 for _ in range(8):
  for s in range(8):
   targets=nxt[s][nxt[s]>=0]
   if len(targets):dist[s]=min(int(dist[s]),1+int(dist[targets].min()))
 assert int(dist[0])<1000
 return nxt,dist

def sample_batch(model,adapter,seed,batch=64,max_tokens=80):
 max_tokens=min(max_tokens,model.stage2_config['positions']-1);device=next(model.parameters()).device
 key=tuple(adapter.tokenizer.vocab)
 if getattr(adapter,'_twoeq_key',None)!=key:adapter._twoeq_tables=build_tables(adapter);adapter._twoeq_key=key
 transitions,distance=[x.to(device) for x in adapter._twoeq_tables];V=transitions.shape[1]
 state=torch.zeros(batch,dtype=torch.long,device=device);done=torch.zeros(batch,dtype=torch.bool,device=device);lengths=torch.zeros_like(state)
 prefix=torch.full((batch,1),adapter.bos,dtype=torch.long,device=device);rng=torch.Generator(device=device).manual_seed(seed);model.eval()
 with torch.inference_mode():
  for step in range(max_tokens):
   logits,_=model(prefix);logits=logits.reshape(batch,prefix.shape[1],V)[:,-1].clone();nexts=transitions[state];remain=max_tokens-step
   valid=(nexts>=0)&(distance[nexts.clamp(min=0)]<=remain-1)
   valid[:,adapter.eos]=(state//4==1)&(state%2==1)
   valid[done]=False;valid[done,adapter.pad]=True
   logits.masked_fill_(~valid,-torch.inf)
   token=torch.multinomial(logits.softmax(-1),1,generator=rng).squeeze(1)
   finished=(~done)&(token==adapter.eos);lengths=torch.where(finished,torch.full_like(lengths,prefix.shape[1]-1),lengths)
   state=torch.where((~done)&(~finished),nexts.gather(1,token[:,None]).squeeze(1).clamp(min=0),state)
   done|=finished;prefix=torch.cat([prefix,token.masked_fill(done,adapter.pad)[:,None]],1)
   if bool(done.all()):break
 assert bool(done.all()),'Count-constrained decoding must terminate within context budget'
 rows=prefix[:,1:].cpu().tolist();lens=lengths.cpu().tolist();result=[]
 for row,n in zip(rows,lens):
  try:text=adapter.decode(row[:n])
  except (ValueError,UnicodeDecodeError,KeyError):result.append(None);continue
  assert len(text.split(chr(92)*2))==2
  result.append(text)
 return result
