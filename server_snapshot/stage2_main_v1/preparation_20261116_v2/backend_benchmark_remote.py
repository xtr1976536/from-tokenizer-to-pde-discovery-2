"""Same discretization/tolerances: baseline vs optimized numerical acceptance."""
from pathlib import Path
import importlib.util,sys,json,time,statistics,resource
import numpy as np
from stage2_main_v1.acceptance import write
from stage2_main_v1.implicit_backend import ImplicitBackend
from stage2_main_v1.safe_backend import SafeBackend
from stage2_main_v1.data import SimulationData
from stage2_main_v1.tests.test_implicit_backend import manufactured
from stage2_main_v1.contracts import InvalidCandidate
root=Path(__file__).resolve().parents[0]
base=Path('/data1/users/liugang/src/eq-bpe/project');work=base/'stage2_main_v1/preparation_20261116_v2';out=base/'runs/stage2_backend_repair_20261116';out.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('stage2_main_v1._benchmark_baseline',work/'outputs/eqgpt-research/stage2-backend-repair-2026-11-16/implicit_backend_before.py')
old=importlib.util.module_from_spec(spec);sys.modules[spec.name]=old;spec.loader.exec_module(old)
results=[]

def compare(name,text,visible,mask,times):
 row=dict(name=name,text=text)
 values={}
 for label,backend in [('before',old.ImplicitBackend()),('after',ImplicitBackend())]:
  try:
   start=time.monotonic();s=backend.parse(text);row[label+'_parse_seconds']=time.monotonic()-start
   start=time.monotonic();c,r2=backend.fit(s,visible,mask);row[label+'_fit_seconds']=time.monotonic()-start
   start=time.monotonic();pred=backend.forecast(s,c,visible,times,mask);row[label+'_forecast_seconds']=time.monotonic()-start
   row[label+'_r2']=list(r2);row[label+'_diagnostics']=backend.last_diagnostics;values[label]=pred
  except InvalidCandidate as error:row[label+'_rejected']=str(error)
 if len(values)==2:
  row['max_absolute_prediction_difference']=float(np.max(np.abs(values['after']-values['before'])))
  row['rmse_prediction_difference']=float(np.sqrt(np.mean((values['after']-values['before'])**2)))
  row['forecast_speedup']=row['before_forecast_seconds']/row['after_forecast_seconds']
 results.append(row);write(out/'benchmark-progress.json',results);print(name,json.dumps({k:v for k,v in row.items() if k not in ['text'] and 'diagnostics' not in k}),flush=True)

visible,mask,A,mode=manufactured()
compare('manufactured_affine',r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v',visible,mask,np.arange(20,40)*.01)
compare('manufactured_nonlinear',r'u_t=\Delta(u)+p+u*v\\v_t=\Delta(v)-u\\p=u+v',visible,mask,np.arange(20,40)*.01)
# Real Cylinder: same observed prefix and full cropped grid, no future target read.
cfg=json.loads((work/'stage2_main_v1/config.json').read_text());data=SimulationData(base/'data/cylinder_numerical_stage2_v1/manifest.json',cfg)
window=data.roles['validation_stop'][0];rv,rt,rm=data.visible(window,'validation_stop')
selected=json.loads((base/'runs/stage2_acceptance_20261116/fit-gate-relaxed-smoke-v1/selected.json').read_text())
compare('real_cylinder_selected',selected['selected']['text'],rv,rm,rt)
# Repeated cross-candidate training fits, with a bounded derivative cache.
by={}
for w in data.roles['train_fit']:by.setdefault(w.trajectory,w)
windows=[by[name] for name in sorted(by)[:4]]
texts=[r['text'] for r in json.loads((base/'runs/stage2_cancelled_audit_20261116/reference_top10.json').read_text())[:3]]
fit_result={};fit_values={}
for label,backend in [('before',old.ImplicitBackend()),('after',ImplicitBackend())]:
 start=time.monotonic();rows=[]
 for repetition in range(3):
  for text in texts:
   system=backend.parse(text)
   for w in windows:
    v,_,m=data.visible(w,'train_fit')
    try:_,r=backend.fit(system,v,m);rows.append(list(r))
    except InvalidCandidate:rows.append(None)
 fit_result[label+'_seconds']=time.monotonic()-start;fit_values[label]=rows
fit_result['speedup']=fit_result['before_seconds']/fit_result['after_seconds']
fit_result['same_rejection_pattern']=[r is None for r in fit_values['before']]==[r is None for r in fit_values['after']]
a=np.array([r for r in fit_values['before'] if r is not None]);b=np.array([r for r in fit_values['after'] if r is not None]);fit_result['max_r2_difference']=float(np.max(np.abs(a-b)))
print('fit_cache',json.dumps(fit_result),flush=True)
# Fault formulas: production wrapper protects parent and recovers for a good candidate.
faults=[];safe=SafeBackend(**cfg['numerics'],**cfg['resource_limits'])
for name in ['stalled-806.json','stalled-1615.json']:
 text=json.loads((work/'stage2_main_v1/tests/fixtures'/name).read_text())['text'];start=time.monotonic()
 try:safe.parse(text);status='compiled_within_budget'
 except InvalidCandidate as error:status=str(error)
 safe.parse(r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v')
 faults.append(dict(name=name,status=status,seconds=time.monotonic()-start,next_candidate_recovered=True))
safe.close();data.close()
write(out/'result.json',dict(comparisons=results,repeated_fit=fit_result,fault_recovery=faults,test_read=False,training_started=False,peak_parent_rss_kb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
print('BENCHMARK_COMPLETE',flush=True)
