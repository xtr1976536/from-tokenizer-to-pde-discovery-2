import json,csv,math,statistics
from pathlib import Path
b=Path(__file__).resolve().parent;r=b/'records';rows=[];by={};audit=[]
for p in sorted((r/'jobs').glob('*/training.json')):
 d=json.loads(p.read_text());c=json.loads((p.parent/'COMPLETE.json').read_text());h=d['history'];s=d['settings'];vals=[x['validation']['loss'] for x in h];i=min(range(len(h)),key=lambda i:vals[i]);be=h[i];end=h[-1];tail=h[-5:];n=len(h)
 assert all(math.isfinite(x['validation']['loss']) and math.isfinite(x['train']['loss']) for x in h)
 assert abs(min(vals)-d['best_validation_loss'])<1e-10 and h[i]['epoch']==d['best_epoch']==c['best_epoch']
 assert [x['epoch'] for x in h]==list(range(1,n+1))
 if n!=c['epochs']:audit.append(dict(job=p.parent.name,history_epochs=n,complete_epochs=c['epochs']))
 slope=lambda a:sum((j-(len(a)-1)/2)*(v-statistics.mean(a)) for j,v in enumerate(a))/sum((j-(len(a)-1)/2)**2 for j in range(len(a)))
 row=dict(job=p.parent.name,scale=d['scale'],split=p.parent.name.split('-')[1],baseline=p.parent.name.endswith('baseline'),epochs=n,best_epoch=d['best_epoch'],val_best=min(vals),val_final=vals[-1],rise_pct=100*(vals[-1]/min(vals)-1),train_at_best=be['train']['loss'],train_final=end['train']['loss'],gap_at_best=min(vals)-be['train']['loss'],tail5_range=max(x['validation']['loss'] for x in tail)-min(x['validation']['loss'] for x in tail),tail10_slope=slope(vals[-10:]),tail10_gain_pct=100*(vals[-10]-vals[-1])/vals[-10],lr=s['lr'],l2=s['l2_matrix'],T=s['T_max'],last_lr=end['learning_rate'],at_cap=n==s['max_epochs'],nats_per_byte_best=be['validation']['nats_per_byte'],train_sources=d['train_sources'],validation_sources=d['validation_sources'],stop_reason=c['stopped_by'])
 rows.append(row);by[row['job']]=d
with (b/'all_runs.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
selected=[];replays=[]
for scale in [212,636]:
 for split in ['811','622']:
  group=[x for x in rows if x['scale']==scale and x['split']==split];base=next(x for x in group if x['baseline']);ranked=sorted([x for x in group if not x['baseline']],key=lambda x:x['val_best']);win=dict(ranked[0]);win['baseline']=base;win['improvement_pct']=100*(base['val_best']-win['val_best'])/base['val_best'];win['runners_up']=ranked[1:4];selected.append(win)
  for row in ranked[:3]:
   h=by[row['job']]['history']
   for minimum in [20,25,30]:
    for patience in [5,10,15]:
     for delta in [1e-5,1e-4]:
      anchor=math.inf;bad=0;seen=[]
      for x in h:
       seen.append(x)
       v=x['validation']['loss']
       if v<anchor-delta:anchor=v;bad=0
       else:bad+=1
       if x['epoch']>=minimum and bad>=patience:break
      replaybest=min(x['validation']['loss'] for x in seen)
      replays.append(dict(job=row['job'],minimum=minimum,patience=patience,delta=delta,stop=len(seen),observed_stop_condition=(bad>=patience and len(seen)>=minimum),val_best=replaybest,loss_penalty_pct=100*(replaybest/row['val_best']-1)))
(b/'selection_analysis.json').write_text(json.dumps(dict(selected=selected,cap_runs=[x for x in rows if x['at_cap']],metadata_discrepancies=audit,replays=replays),indent=2))
for win in selected:
 print('\nWIN',json.dumps({k:v for k,v in win.items() if k not in ['baseline','runners_up']}))
 print('BASE',json.dumps(win['baseline']));print('TOP3',[(x['T'],x['lr'],x['l2'],round(x['val_best'],6),round(x['rise_pct'],3)) for x in win['runners_up'][:2]])
 print('WIN_HISTORY',[(x['epoch'],round(x['train']['loss'],5),round(x['validation']['loss'],5),x['learning_rate']) for x in by[win['job']]['history'] if x['epoch'] in [1,5,10,15,20,21,25,30,win['best_epoch'],win['epochs']]])
print('AT_CAP',len([x for x in rows if x['at_cap']]),'DISCREPANCIES',audit)
print('REPLAY_WIN_MIN30',[(x['job'],x['patience'],x['delta'],x['stop'],x['loss_penalty_pct']) for x in replays if x['job'] in [w['job'] for w in selected] and x['minimum']==30])
