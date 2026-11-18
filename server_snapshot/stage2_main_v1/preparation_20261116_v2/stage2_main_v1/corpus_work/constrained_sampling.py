"""Byte-level task mask for LaTeX AST-BPE; no GRE and no target PDE templates."""
from dataclasses import dataclass,replace
from functools import lru_cache
try:from .task_gate import validate
except ImportError:from task_gate import validate
MACROS=('partial','Delta','nabla','cdot','frac','sin','cos','tan','sinh','cosh','tanh','exp','log','ln','sqrt','abs')
@dataclass(frozen=True)
class State:
 residual_zero_rhs:bool=False
 equations_done:int=0
 equalities:int=0
 content_left:bool=False
 content_right:bool=False
 slash:bool=False
 macro:str=''
 stack:str=''
 fields:int=0
 axes:int=0

def finish_macro(s):
 if s.macro not in MACROS:return None
 return replace(s,macro='',axes=s.axes|3 if s.macro in ('Delta','nabla') else s.axes)
@lru_cache(maxsize=100000)
def advance(s,raw):
 try:text=raw.decode('ascii')
 except UnicodeDecodeError:return None
 for c in text:
  if s.macro:
   if c.isalpha():
    prefix=s.macro+c
    if not any(m.startswith(prefix) for m in MACROS):return None
    s=replace(s,macro=prefix);continue
   s=finish_macro(s)
   if s is None:return None
  if s.slash:
   if c=='\\':
    if s.stack or s.equalities!=1 or not s.content_left or not s.content_right or s.equations_done>=2:return None
    s=replace(s,equations_done=s.equations_done+1,equalities=0,content_left=False,content_right=False,slash=False);continue
   if s.residual_zero_rhs and s.equalities:return None
   if c.isalpha() and any(m.startswith(c) for m in MACROS):s=replace(s,slash=False,macro=c);continue
   return None
  if c=='\\':s=replace(s,slash=True);continue
  if c in ' \n\t':continue
  if s.residual_zero_rhs and s.equalities and c not in '0':return None
  if c in '({[':
   if len(s.stack)>=24:return None
   s=replace(s,stack=s.stack+c);continue
  if c in ')}]':
   if not s.stack or {'}':'{',')':'(',']':'['}[c]!=s.stack[-1]:return None
   s=replace(s,stack=s.stack[:-1]);continue
  if c=='=':
   if s.stack or s.equalities or not s.content_left:return None
   s=replace(s,equalities=1);continue
  if s.residual_zero_rhs and s.equalities and not s.stack:
   if c=='0' and not s.content_right:
    s=replace(s,content_right=True);continue
   return None
  if c in 'uvpxyt' or c.isdigit():
   f={'u':1,'v':2,'p':4}.get(c,0);axes={'x':1,'y':2}.get(c,0)
   s=replace(s,fields=s.fields|f,axes=s.axes|axes,
             content_left=s.content_left or s.equalities==0,content_right=s.content_right or s.equalities==1);continue
  if c in '+-*/^_.':continue
  return None
 return s

def can_end(s,text):
 if s.macro:s=finish_macro(s)
 if s is None or s.slash or s.stack or s.equations_done!=2 or s.equalities!=1 or s.fields!=7 or s.axes!=3:return False
 try:validate(text)
 except (ValueError,TypeError,IndexError,RecursionError):return False
 return True

def sample_batch(model,adapter,seed,batch=8,max_tokens=160,random_fraction=0.,return_records=False,residual_zero_rhs=False):
 """Returns valid strings or None at budget exhaustion, never a hand-coded PDE.
 Only task constraints are masked; exact generation attempts/rejects remain auditable.
 """
 import torch
 if not 0<=random_fraction<=1:raise ValueError('Invalid mixture')
 device=next(model.parameters()).device;V=len(adapter.tokenizer.vocab)+3
 limit=min(max_tokens,model.stage2_config['positions']-1)
 prefix=torch.full((batch,1),adapter.bos,dtype=torch.long,device=device)
 states=[State(residual_zero_rhs=residual_zero_rhs) for _ in range(batch)];done=[False]*batch;result=[None]*batch;tokens=[[] for _ in range(batch)]
 reasons=['token_limit']*batch
 rng=torch.Generator(device=device).manual_seed(seed);model.eval()
 with torch.inference_mode():
  for _ in range(limit):
   logits,_=model(prefix);logits=logits.reshape(batch,prefix.shape[1],V)[:,-1]
   chosen=[]
   for i,s in enumerate(states):
    if done[i]:chosen.append(adapter.pad);continue
    valid=[];transitions={}
    for tid,raw in enumerate(adapter.tokenizer.vocab,3):
     nxt=advance(s,bytes(raw))
     if nxt is not None:valid.append(tid);transitions[tid]=nxt
    text=adapter.decode(tokens[i]) if tokens[i] else ''
    if can_end(s,text):valid.append(adapter.eos)
    if not valid:done[i]=True;reasons[i]='no_legal_next_token';chosen.append(adapter.pad);continue
    ids=torch.tensor(valid,device=device);p=logits[i,ids].softmax(-1)
    p=(1-random_fraction)*p+random_fraction/len(valid)
    tid=int(ids[torch.multinomial(p,1,generator=rng)])
    if tid==adapter.eos:result[i]=text;done[i]=True;reasons[i]='valid_eos'
    else:tokens[i].append(tid);states[i]=transitions[tid]
    chosen.append(adapter.pad if done[i] else tid)
   prefix=torch.cat([prefix,torch.tensor(chosen,device=device)[:,None]],dim=1)
   if all(done):break
 if return_records:
  return [dict(text=result[i],raw_text=adapter.decode(tokens[i]) if tokens[i] else '',reason=reasons[i],generated_tokens=len(tokens[i]),equations_done=states[i].equations_done,stack_depth=len(states[i].stack),fields_mask=states[i].fields) for i in range(batch)]
 return result
