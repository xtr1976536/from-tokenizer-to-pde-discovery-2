"""Paired fixed-corpus training; vocabulary is sole A/B difference."""
import sys,json,time,argparse,math,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'ast_bpe_multifield_v1'),str(ROOT/'ast_bpe_multifield_v2')]
import numpy as np,torch
from model import build,save

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--output',required=True);ap.add_argument('--epochs',type=int,default=200);ap.add_argument('--smoke',action='store_true');ap.add_argument('--device',default='cpu');a=ap.parse_args()
 torch.set_num_threads(2)
 if a.device=='cuda':
  assert os.environ.get('CUDA_VISIBLE_DEVICES')=='2'
  torch.cuda.set_per_process_memory_fraction(.12)
 base=Path(a.base);out=Path(a.output);out.mkdir(exist_ok=False,parents=True)
 reports=[]
 for mode in ['base_vocab','augmented_vocab']:
  folder=out/mode;folder.mkdir();rows=[json.loads(l) for l in (base/mode/'encoded.jsonl').open()];train=[r for r in rows if r['split']=='train'];val=[r for r in rows if r['split']=='validation'];m=build(300,72,a.device,seed=525,smoke=a.smoke);opt=torch.optim.Adam(m.parameters(),lr=1e-4);rng=np.random.default_rng(525);history=[];best=float('inf');state=None;start=time.monotonic()
  def batches(rs):
   for i in range(0,len(rs),128):
    ss=[r['tokens'] for r in rs[i:i+128]];x=torch.zeros((len(ss),max(map(len,ss))),dtype=torch.long,device=a.device)
    for j,s in enumerate(ss):x[j,:len(s)]=torch.tensor(s,device=a.device)
    yield x[:,:-1],x[:,1:]
  for epoch in range(a.epochs):
   m.train();total=0.;n=0
   for x,y in batches([train[i] for i in rng.permutation(len(train))]):
    opt.zero_grad();logits,_=m(x);loss=torch.nn.functional.cross_entropy(logits.reshape(-1,300),y.reshape(-1),ignore_index=0);loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1.);opt.step();total+=float(loss.detach())*int((y!=0).sum());n+=int((y!=0).sum())
   m.eval();v=0.;vn=0
   with torch.no_grad():
    for x,y in batches(val):
     logits,_=m(x);v+=float(torch.nn.functional.cross_entropy(logits.reshape(-1,300),y.reshape(-1),ignore_index=0,reduction='sum'));vn+=int((y!=0).sum())
   ce=v/vn;chars=sum(len(r['text'].encode()) for r in val);row=dict(epoch=epoch+1,train_token_ce=total/n,val_token_ce=ce,val_nats_per_byte=v/chars);history.append(row)
   # Nats/byte comparable across tokenizers; checkpoint selected within each mode.
   if v/chars<best:
    best=v/chars;best_epoch=epoch+1;state={k:t.detach().cpu().clone() for k,t in m.state_dict().items()}
   if (epoch+1)%10==0:print(mode,row,flush=True)
  m.load_state_dict(state);metadata=dict(history=history,best_epoch=best_epoch,best_nats_per_byte=best,epochs=a.epochs,training_sequences=len(train),validation_sequences=len(val),scope='smoke paired diagnostic' if a.smoke else 'production paired pretraining',source_data='external equation corpus only',mode=mode,seconds=time.monotonic()-start)
  metadata['tokenizer_sha256']=hashlib.sha256((base/mode/'tokenizer300.json').read_bytes()).hexdigest();metadata['encoded_sha256']=hashlib.sha256((base/mode/'encoded.jsonl').read_bytes()).hexdigest()
  save(m,folder/'model.pt',**metadata);(folder/'training.json').write_text(json.dumps(metadata,indent=2));reports.append(metadata);(out/'comparison.json').write_text(json.dumps(reports,indent=2));print('FINISHED',mode,best,flush=True)
if __name__=='__main__':main()
