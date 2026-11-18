from math_tokenizer.eqgpt.author import seed_all
from math_tokenizer.eqgpt.latex_codec import structure_to_latex
import torch
def sample_and_evaluate(model,adapter,evaluator,target,limit,seed,reference=False,max_attempts=5000,random_fraction=.2):
 cycle=(seed-525)//400
 seed=seed+cycle*(5000-400)
 core=getattr(model,'core',model)
 if target<1 or max_attempts<target or limit>core.decoder.pos_emb.num_embeddings:raise ValueError('Invalid candidate budget or position capacity')
 model.eval();device=next(core.parameters()).device;rows=[]
 attempt = -1
 while True:
  attempt += 1
  if sum(r['status']=='evaluated' for r in rows)>=target:break
  if attempt>=max_attempts:raise RuntimeError(f'Candidate cap reached: {target=} {max_attempts=}')
  seed_all(seed+attempt);rng=torch.Generator(device=device).manual_seed(seed+attempt);prefix=[adapter.bos];payload=[];reason='token_limit'
  for _ in range(limit):
   inputs=torch.tensor([prefix],dtype=torch.long,device=device)
   with torch.no_grad():logits,_=core(inputs)
   probs=logits.reshape(1,len(prefix),adapter.vocab_size)[0,-1].softmax(-1)
   allowed=torch.ones(adapter.vocab_size,dtype=torch.bool,device=device)
   if reference:
    allowed=evaluator.mask.to(device)!=0
    if len(prefix)%2==0:allowed[0]=False;allowed[5:]=False
    else:allowed[:6]=False
   probs=probs*allowed;mass=probs.sum()
   if not torch.isfinite(mass) or mass<=0:raise FloatingPointError('No finite permitted probability mass')
   probs=probs/mass
   if torch.rand((),device=device,generator=rng).item()<1-random_fraction:token=int(torch.multinomial(probs,1,generator=rng))
   else:
    valid=torch.nonzero(probs!=0 if reference else allowed).flatten();token=int(valid[torch.randint(len(valid),(1,),device=device,generator=rng)].item())
   payload.append(token);prefix.append(token)
   if token==adapter.eos:reason='eos';break
   if token in (adapter.pad,adapter.bos):reason='unexpected_control';break
  row=dict(attempt=attempt,reference=reference,ids=prefix if reference else payload,stopped=reason=='eos',
   stop_reason=reason,sampling_policy='successful_candidate_budget_v2',random_fraction=random_fraction,generated_tokens=len(payload),sampling_seed=seed+attempt)
  if reference:row.update(raw_gre=prefix.copy(),gre=prefix.copy(),text=structure_to_latex(prefix))
  else:
   try:row['text']=adapter.decode(payload[:-1] if reason=='eos' else payload)
   except (UnicodeDecodeError,ValueError,IndexError):row.update(text=None,decode_error=True)
  row=evaluator.evaluate(row);row.update(attempt=attempt,successful_candidate_target=target,attempt_cap=max_attempts);rows.append(row)
 print('CANDIDATE_BUDGET',dict(target=target,attempts=len(rows),evaluated=sum(r['status']=='evaluated' for r in rows),cap=max_attempts),flush=True)
 return rows
