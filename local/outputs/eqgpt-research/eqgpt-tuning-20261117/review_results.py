import json,math,csv,statistics
from pathlib import Path
b=Path(__file__).resolve().parent;rows=[];histories={};replays=[]
for p in sorted((b/'records/jobs').glob('*/training.json')):
 d=json.loads(p.read_text());h=d['history'];s=d['settings'];c=json.loads((p.parent/'COMPLETE.json').read_text());v=[x['validation']['loss'] for x in h];best=min(h,key=lambda x:x['validation']['loss']);n=len(h);baseline='-baseline-' in p.parent.name
 assert n==c['epochs'] and best['epoch']==c['best_epoch']==d['best_epoch'] and math.isclose(min(v),d['best_validation_loss'])
 assert all(math.isfinite(x['validation']['loss']) and math.isfinite(x['train']['loss']) for x in h)
 anchor=math.inf;bad=0
 for x in h:
  loss=x['validation']['loss']
  if loss<anchor-s['min_delta']:anchor=loss;bad=0
  else:bad+=1
 assert n==s['max_epochs'] or bad>=s['patience']
 if not baseline:
  assert n>=30
  assert all(math.isclose(x['learning_rate'],1e-6,abs_tol=1e-16) for x in h[s['T_max']:])
 tail=v[-10:];slope=sum((i-4.5)*(x-statistics.mean(tail)) for i,x in enumerate(tail))/82.5
 row=dict(job=p.parent.name,scale=d['scale'],split=p.parent.name.split('-')[1],baseline=baseline,lr=s['lr'],l2=s['l2_matrix'],T=s['T_max'],epochs=n,best_epoch=best['epoch'],ce=min(v),npb=best['validation']['nats_per_byte'],train_best=best['train']['loss'],gap=min(v)-best['train']['loss'],final=v[-1],rise_pct=100*(v[-1]/min(v)-1),tail10_change_pct=100*(v[-1]/v[-10]-1),tail10_slope=slope,tail5_span=max(v[-5:])-min(v[-5:]),capped=n==s['max_epochs'],bad_epochs=bad,late_recovery=best['epoch']<n-5 and v[-1]<v[-6] and n<=s['T_max']+1)
 rows.append(row);histories[row['job']]=d
with (b/'review_all_runs.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=[]
for scale in [212,636]:
 for split in ['811','622']:
  group=[x for x in rows if (x['scale'],x['split'])==(scale,split)];base=next(x for x in group if x['baseline']);a=sorted([x for x in group if not x['baseline']],key=lambda x:x['ce']);win=a[0];runner=a[1];summary.append(dict(scale=scale,split=split,baseline=base,winner=win,runner_up=runner,ranked=a,improvement_pct=100*(1-win['ce']/base['ce']),runner_gap_pct=100*(runner['ce']/win['ce']-1)))
  for x in a[:3]:
   h=histories[x['job']]['history']
   for patience in [5,10,15]:
    anchor=math.inf;bad=0;seen=[]
    for t in h:
     seen.append(t);v=t['validation']['loss']
     if v<anchor-1e-4:anchor=v;bad=0
     else:bad+=1
     if len(seen)>=30 and bad>=patience:break
    replays.append(dict(job=x['job'],patience=patience,stop=len(seen),loss_penalty_pct=100*(min(t['validation']['loss'] for t in seen)/x['ce']-1)))
(b/'review.json').write_text(json.dumps(dict(status='PASS',count=len(rows),summary=summary,replays=replays,capped=[x for x in rows if x['capped']],late_recovery=[x for x in rows if x['late_recovery']]),indent=2))
for g in summary:
 x=g['winner'];print('WIN',x['job'],'improve',g['improvement_pct'],'runner_gap',g['runner_gap_pct'],'tail10',x['tail10_change_pct'],'gap',x['gap'])
 h=histories[x['job']]['history'];print('TRAJECTORY',[(t['epoch'],round(t['train']['loss'],6),round(t['validation']['loss'],6)) for t in h if t['epoch'] in [1,5,10,15,20,25,30,x['best_epoch'],x['epochs']]])
 print('L2_GROUP',[(l2,round(min(x['ce'] for x in g['ranked'] if x['l2']==l2),6)) for l2 in [0.,.001,.01]])
print('CAP_COUNT',sum(x['capped'] for x in rows));print('LATE_RECOVERY',[(x['job'],x['best_epoch'],x['epochs'],x['rise_pct'],x['tail10_change_pct']) for x in rows if x['late_recovery']]);print('REPLAYS',[x for x in replays if x['job'] in [g['winner']['job'] for g in summary]])
