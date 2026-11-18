import json,math,statistics,csv
from pathlib import Path
b=Path(__file__).resolve().parent
rows=[];histories={};audits=[]
oldb=b.parent/'stage1-tuning-20261116/analysis-v128/records/jobs'
for p in sorted((b/'records/jobs').glob('*/training.json')):
 d=json.loads(p.read_text());h=d['history'];c=json.loads((p.parent/'COMPLETE.json').read_text());s=d['settings'];job=p.parent.name;scale=d['scale'];split=job.split('-')[1];seed=s['seed'];vs=[x['validation']['loss'] for x in h];best=min(h,key=lambda x:x['validation']['loss']);n=len(h)
 assert n==c['epochs'] and n>=30 and c['best_epoch']==best['epoch']==d['best_epoch']
 assert abs(min(vs)-d['best_validation_loss'])<1e-10
 assert all(math.isclose(x['learning_rate'],1e-6,abs_tol=1e-16) for x in h[20:])
 assert all(math.isfinite(x['validation']['loss']) and math.isfinite(x['train']['loss']) for x in h)
 anchor=math.inf;bad=0
 for x in h:
  if x['validation']['loss']<anchor-1e-4:anchor=x['validation']['loss'];bad=0
  else:bad+=1
 assert bad>=15 and n<80
 tail=vs[-10:];slope=sum((i-4.5)*(v-statistics.mean(tail)) for i,v in enumerate(tail))/82.5
 old=json.loads((oldb/f'{scale}-{split}-v128-baseline/training.json').read_text());oldwin=json.loads((oldb/(f'{scale}-{split}-v128-t20-lr'+('0.0001-l20.001' if scale==212 else '5e-05-l20'))/'training.json').read_text())
 row=dict(job=job,scale=scale,split=split,seed=seed,epochs=n,best_epoch=best['epoch'],best_ce=min(vs),best_npb=best['validation']['nats_per_byte'],train_at_best=best['train']['loss'],gap_at_best=min(vs)-best['train']['loss'],final_ce=vs[-1],rise_pct=100*(vs[-1]/min(vs)-1),tail10_slope=slope,tail10_change_pct=100*(vs[-1]/vs[-10]-1),tail5_span=max(vs[-5:])-min(vs[-5:]),bad_epochs=bad,reference_ce=anchor,lr=s['lr'],l2=s['l2_matrix'],baseline525_best=old['best_validation_loss'],vs_baseline525_pct=100*(1-min(vs)/old['best_validation_loss']),vs_oldwinner525_pct=100*(min(vs)/oldwin['best_validation_loss']-1))
 rows.append(row);histories[job]=d
summary=[]
for scale in [212,636]:
 for split in ['811','622']:
  a=[x for x in rows if (x['scale'],x['split'])==(scale,split)]
  v=[x['best_ce'] for x in a];npb=[x['best_npb'] for x in a]
  summary.append(dict(scale=scale,split=split,ce_mean=statistics.mean(v),ce_sd=statistics.stdev(v),npb_mean=statistics.mean(npb),npb_sd=statistics.stdev(npb),min_epochs=min(x['epochs'] for x in a),max_epochs=max(x['epochs'] for x in a),max_rise_pct=max(x['rise_pct'] for x in a),gap_min=min(x['gap_at_best'] for x in a),gap_max=max(x['gap_at_best'] for x in a),mean_vs_baseline525_pct=100*(1-statistics.mean(v)/a[0]['baseline525_best'])))
with (b/'per_run_analysis.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(b/'analysis.json').write_text(json.dumps(dict(rows=rows,summary=summary,audit='12/12: matching epochs, best epoch, finite losses, eta_min plateau and early-stop counter verified'),indent=2))
print(json.dumps(summary,indent=2))
for x in rows:print(x['job'],'gap',round(x['gap_at_best'],4),'tail10',round(x['tail10_change_pct'],5),'slope',round(x['tail10_slope'],8),'seed525 correction diff %',round(x['vs_oldwinner525_pct'],5) if x['seed']==525 else 'NA')
x=histories['636-811-v128-seed526'];print('LATE_BEST',[(v['epoch'],v['validation']['loss'],v['train']['loss']) for v in x['history'] if v['epoch'] in [20,21,25,30,35,40,44,45,50,54]])
