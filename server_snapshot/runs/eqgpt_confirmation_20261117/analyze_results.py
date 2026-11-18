import json,math,csv,statistics
from pathlib import Path
r=Path(__file__).resolve().parent;old=json.loads((r/'previous_review.json').read_text());rows=[];history={}
for p in sorted((r/'jobs').glob('*/training.json')):
 d=json.loads(p.read_text());h=d['history'];s=d['settings'];c=json.loads((p.parent/'COMPLETE.json').read_text());best=min(h,key=lambda x:x['validation']['loss']);v=[x['validation']['loss'] for x in h];n=len(h)
 assert n==c['epochs'] and best['epoch']==c['best_epoch']==d['best_epoch'] and math.isclose(min(v),d['best_validation_loss'])
 assert n>=s['minimum_epochs'] and all(math.isfinite(x['validation']['loss']) and math.isfinite(x['train']['loss']) for x in h)
 assert all(math.isclose(x['learning_rate'],1e-6,abs_tol=1e-16) for x in h[s['T_max']:])
 anchor=math.inf;bad=0
 for value in v:
  if value<anchor-s['min_delta']:anchor=value;bad=0
  else:bad+=1
 assert n==80 or bad>=15
 row=dict(job=p.parent.name,scale=d['scale'],split=p.parent.name.split('-')[1],seed=s['seed'],lr=s['lr'],l2=s['l2_matrix'],T=s['T_max'],minimum=s['minimum_epochs'],epochs=n,best_epoch=best['epoch'],best_ce=min(v),gap_ce=min(v)-best['train']['loss'],rise_pct=100*(v[-1]/min(v)-1),tail10_change_pct=100*(v[-1]/v[-10]-1),capped=n==80);rows.append(row);history[row['job']]=d
assert len(rows)==11
with (r/'confirmation_runs.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=[]
for g in old['summary']:
 scale,split=g['scale'],g['split'];a=[x for x in rows if (x['scale'],x['split'])==(scale,split) and '-selected-' in x['job']];assert len(a)==2
 vals=[g['winner']['ce']]+[x['best_ce'] for x in a];summary.append(dict(scale=scale,split=split,ce_mean=statistics.mean(vals),ce_sd=statistics.stdev(vals),old525=g['baseline']['ce'],selected525=g['winner']['ce'],max_rise=max([g['winner']['rise_pct']]+[x['rise_pct'] for x in a]),capped=sum(x['capped'] for x in a)))
paired=[];g=next(g for g in old['summary'] if (g['scale'],g['split'])==(636,'622'))
for seed in [525,526,527]:
 if seed==525:
  t30=g['winner']['ce'];t25=next(x['ce'] for x in g['ranked'] if x['T']==25 and x['lr']==1e-4 and x['l2']==.001)
 else:
  t30=next(x['best_ce'] for x in rows if x['scale']==636 and x['split']=='622' and x['seed']==seed and '-selected-' in x['job']);t25=next(x['best_ce'] for x in rows if x['seed']==seed and '-alternateT25-' in x['job'])
 paired.append(dict(seed=seed,T30=t30,T25=t25,T25_minus_T30=t25-t30))
recovery=next(x for x in rows if 'recoveryT30min45' in x['job']);baseg=next(g for g in old['summary'] if (g['scale'],g['split'])==(212,'622'));recovery['previous_T30']=next(x['ce'] for x in baseg['ranked'] if x['T']==30 and x['lr']==5e-5 and x['l2']==.001);recovery['selected_T20']=baseg['winner']['ce']
(r/'analysis.json').write_text(json.dumps(dict(status='AUDITED_NOT_FINAL_SELECTION',summary=summary,paired_T25_T30=paired,recovery=recovery,rows=rows),indent=2))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes=plt.subplots(3,4,figsize=(16,10),layout='constrained')
for ax,x in zip(axes.flat,rows):
 h=history[x['job']]['history'];xx=[t['epoch'] for t in h];ax.plot(xx,[t['validation']['loss'] for t in h],color='#725B88',label='Validation');ax.plot(xx,[t['train']['loss'] for t in h],color='#658F88',ls='--',label='Train');ax.set_title(x['job'].replace('-eqgpt-','\n'),fontsize=9);ax.set_xlabel('Epoch');ax.set_ylabel('Token CE');ax.legend(fontsize=8)
axes.flat[-1].axis('off');fig.savefig(r/'confirmation_curves.png',dpi=220);fig.savefig(r/'confirmation_curves.pdf')
print(json.dumps(dict(summary=summary,paired=paired,recovery=recovery),indent=2))
