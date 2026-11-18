import json,math,statistics,csv,hashlib
from pathlib import Path
b=Path(__file__).resolve().parent;prior=b.parent/'stage1-v128-confirmation-20261117';rows=[];audit=[];denominators={}
for folder,v128 in [(b/'records/jobs',False),(prior/'records/jobs',True)]:
 for p in sorted(folder.glob('*/training.json')):
  d=json.loads(p.read_text());h=d['history'];s=d['settings'];c=json.loads((p.parent/'COMPLETE.json').read_text());vocab=int(d['arm'].split('_')[-1]);scale=d['scale'];split=p.parent.name.split('-')[1];selected=v128 or '-selected-' in p.parent.name
  assert len(h)==c['epochs'] and [x['epoch'] for x in h]==list(range(1,len(h)+1))
  best=min(h,key=lambda x:x['validation']['loss']);assert best['epoch']==d['best_epoch']==c['best_epoch']
  assert abs(best['validation']['loss']-d['best_validation_loss'])<1e-12
  anchor=math.inf;bad=0;bytes_seen=[]
  for x in h:
   v=x['validation']['loss'];assert math.isfinite(v) and math.isfinite(x['train']['loss'])
   if v<anchor-s['min_delta']:anchor=v;bad=0
   else:bad+=1
   # NPB denominator consistency; same rendered sequence bytes across vocabularies.
   bytes_seen.append(v*x['validation']['tokens']/x['validation']['nats_per_byte'])
  assert max(bytes_seen)-min(bytes_seen)<1e-6
  denominators.setdefault((scale,split),[]).append(bytes_seen[0])
  if selected:
   assert len(h)>=30 and len(h)<80 and bad>=15
   assert s['T_max']==20 and s['patience']==15 and s['min_delta']==1e-4
   assert all(math.isclose(x['learning_rate'],1e-6,abs_tol=1e-16) for x in h[20:])
   assert s['lr']==(1e-4 if scale==212 else 5e-5) and s['l2_matrix']==(.001 if scale==212 else 0.)
  rows.append(dict(job=p.parent.name,vocab=vocab,scale=scale,split=split,seed=s['seed'],selected=selected,epochs=len(h),best_epoch=best['epoch'],ce=best['validation']['loss'],npb=best['validation']['nats_per_byte'],train_npb=best['train']['nats_per_byte'],gap_npb=best['validation']['nats_per_byte']-best['train']['nats_per_byte'],rise_pct=100*(h[-1]['validation']['loss']/best['validation']['loss']-1),tail10_pct=100*(h[-1]['validation']['loss']/h[-10]['validation']['loss']-1)))
assert len(rows)==44 and sum(x['selected'] for x in rows)==36
for key,values in denominators.items():assert max(values)-min(values)<1e-6,(key,values)
summary=[]
for scale in [212,636]:
 for split in ['811','622']:
  for vocab in [96,128,160]:
   a=[x for x in rows if x['selected'] and (x['scale'],x['split'],x['vocab'])==(scale,split,vocab)]
   summary.append(dict(scale=scale,split=split,vocab=vocab,npb_mean=statistics.mean(x['npb'] for x in a),npb_sd=statistics.stdev(x['npb'] for x in a),gap_npb_mean=statistics.mean(x['gap_npb'] for x in a),stop_min=min(x['epochs'] for x in a),stop_max=max(x['epochs'] for x in a),best_min=min(x['best_epoch'] for x in a),best_max=max(x['best_epoch'] for x in a),max_rise_pct=max(x['rise_pct'] for x in a),max_tail10_pct=max(x['tail10_pct'] for x in a)))
with (b/'three_vocab_review.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
result=dict(status='PASS',runs_checked=44,selected_runs=36,all_selected_early_stopped=True,all_selected_completed_minimum30=True,no_selected_capped=True,metric_denominator_consistency={str(k):round(v[0]) for k,v in denominators.items()},summary=summary)
(b/'review_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
config=dict(status='RECOMMENDED_FINAL_SHARED_PRETRAINING_CONFIG_AFTER_V96_V128_V160_REVIEW',vocabularies=[96,128,160],splits=['811','622'],seeds=[525,526,527],scale_settings={'212':dict(learning_rate=1e-4,weight_decay_matrix=.001),'636':dict(learning_rate=5e-5,weight_decay_matrix=0.)},common=dict(optimizer='Adam',layers=6,batch_size=128,gradient_clip=1.,cosine_epochs=20,minimum_learning_rate=1e-6,minimum_completed_epochs=30,patience=15,min_delta=1e-4,maximum_epochs=80),schedule='step after completed epoch through epoch20; hold1e-6 from epoch21',selection='save true minimum validation CE checkpoint; reset patience only after effective improvement',positions='at least72, 636/811/v96 uses73 to avoid truncation',limitations=['shared strategy validated, not per-vocabulary global hyperparameter optimum','old-strategy controls paired only at525','212/622 generalization gap remains','no PDE downstream or test data evaluated'])
(b/'final_pretraining_config.json').write_text(json.dumps(config,indent=2))
