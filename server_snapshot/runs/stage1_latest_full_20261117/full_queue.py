import json,subprocess,sys,os,time,fcntl,hashlib
from pathlib import Path
r=Path(__file__).resolve().parent
lock=(r/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
gpu='GPU-e857f4d0-daa6-f33d-3dc8-927f15ab7d59';env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu,PYTHONPATH=str(r/'src'),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',STAGE1_WORKER_CAP_GIB='8',STAGE1_SEARCH_CAP_GIB='14')
def dump(p,d):
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.replace(p)
def execute(jobs,phase,limit,cap):
 pending=jobs.copy();active=[];done=[];failed=[]
 while pending or active:
  for j,p,f in active[:]:
   rc=p.poll()
   if rc is not None:
    f.close();active.remove((j,p,f));(done if rc==0 else failed).append(dict(job=j,returncode=rc))
    if rc==0 and phase=='pretrain':
     folder=r/'jobs'/j['job'];target=r/'pretrained'/j['job'];target.symlink_to(folder,target_is_directory=True)
  if pending and not failed and len(active)<limit:
   used=int(subprocess.check_output(['nvidia-smi','--id='+gpu,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
   if used+(cap+1)*1024<=92*1024 and (len(active)+1)*cap<=84:
    j=pending.pop(0);cmd=[sys.executable,'-u',str(r/('pretrain_tune.py' if phase=='pretrain' else 'search_case.py'))]
    if phase=='pretrain':cmd+=['--campaign',str(r)]
    for k,v in j.items():cmd+=['--'+k.replace('_','-'),str(v)]
    name=j.get('job','-'.join(str(v) for v in j.values()));f=(r/'logs'/(phase+'-'+name+'.log')).open('w');p=subprocess.Popen(cmd,cwd=r,env=env,stdout=f,stderr=subprocess.STDOUT);active.append((j,p,f))
  state=dict(phase=phase,time=time.time(),total=len(jobs),completed=len(done),pending=len(pending),active=[dict(job=j,pid=p.pid) for j,p,f in active],failed=failed,gpu=gpu,worker_cap_gib=cap,limit=limit)
  dump(r/'queue_status.json',state);dump(r/(phase+'_status.json'),state)
  if failed and not active:raise RuntimeError('Task failure; stop queue')
  if pending or active:time.sleep(5)
 return done
execute(json.loads((r/'pretrain_jobs.json').read_text()),'pretrain',4,8)
# Original EqGPT sampler and continuation smoke test after baseline checkpoints exist.
smoke=dict(scale=212,split='811',seed=525,arm='eqgpt_reference',random_fraction=.2,case='Wave_equation')
cmd=[sys.executable,'-u',str(r/'search_case.py'),'--smoke']
for k,v in smoke.items():cmd+=['--'+k.replace('_','-'),str(v)]
with (r/'logs/reference-smoke.log').open('w') as f:subprocess.run(cmd,cwd=r,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
execute(json.loads((r/'search_jobs.json').read_text()),'search',6,14)
dump(r/'ALL_COMPLETE.json',dict(status='PASS',search_cases=672,time=time.time()))
# Final report groups the same Top1/Top10 outcomes, keeping split explicit.
import csv,statistics
rows=[]
for p in sorted((r/'search/results').glob('*/*/*/*/*/*/result.json')):
 d=json.loads(p.read_text());d['sampling']=p.parents[2].name;rows.append(d)
assert len(rows)==672
with (r/'case_results.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
groups={}
for d in rows:
 k=(d['scale'],d['split'],d['arm'],d['sampling']);groups.setdefault(k,[]).append(d)
summary=[dict(scale=k[0],split=k[1],arm=k[2],sampling=k[3],cases=len(v),top1=sum(x['top1'] for x in v),top10=sum(x['top10'] for x in v)) for k,v in groups.items()]
dump(r/'summary.json',dict(results=summary,definition='correct-structure recovery;24 case-seed outcomes per arm/split/sampling'))
