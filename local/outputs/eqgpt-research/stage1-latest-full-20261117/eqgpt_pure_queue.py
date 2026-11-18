import json,subprocess,sys,os,time,fcntl,hashlib,csv
from pathlib import Path
r=Path(__file__).resolve().parent;lock=(r/'eqgpt_pure.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
gpu='GPU-ba72db90-47e9-38fd-0e9e-905c3b1798b5';env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu,PYTHONPATH=str(r/'src'),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',STAGE1_SEARCH_CAP_GIB='12')
def dump(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2));t.replace(p)
def dest(j):return r/'search/results'/str(j['scale'])/j['split']/j['arm']/'model'/str(j['seed'])/j['case']
def complete(j):
 p=dest(j)/'complete.json'
 if not p.exists():return False
 m=json.loads(p.read_text());assert m['status']=='PASS'
 for n,h in m['files'].items():assert hashlib.sha256((p.parent/n).read_bytes()).hexdigest()==h
 return True
jobs=json.loads((r/'eqgpt_pure_jobs.json').read_text());assert len(jobs)==96 and all(j['eqgpt_random_fraction']==0 for j in jobs)
done=[j for j in jobs if complete(j)];pending=[j for j in jobs if not complete(j)];active=[];failed=[]
while pending or active:
 for j,p,f in active[:]:
  rc=p.poll()
  if rc is not None:
   f.close();active.remove((j,p,f))
   if rc==0 and complete(j):done.append(j)
   else:failed.append(dict(job=j,returncode=rc))
 if pending and len(active)<4:
  used=int(subprocess.check_output(['nvidia-smi','--id='+gpu,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
  if used+13*1024<=92*1024 and (len(active)+1)*12<=48:
   j=pending.pop(0);cmd=[sys.executable,'-u',str(r/'eqgpt_pure_case.py')]
   for k,v in j.items():cmd+=['--'+k.replace('_','-'),str(v)]
   name='-'.join(str(v) for v in j.values());f=(r/'logs'/('eqgpt-pure-'+name+'.log')).open('w');p=subprocess.Popen(cmd,cwd=r,env=env,stdout=f,stderr=subprocess.STDOUT);active.append((j,p,f))
 state=dict(phase='eqgpt_pure_model_sampling',time=time.time(),total=96,completed=len(done),pending=len(pending),active=[dict(job=j,pid=p.pid) for j,p,f in active],failed=failed,gpu=gpu,worker_cap_gib=12,limit=4,eqgpt_legacy_preserved=True)
 dump(r/'eqgpt_pure_status.json',state)
 if pending or active:time.sleep(5)
rows=[]
for j in done:
 d=json.loads((dest(j)/'result.json').read_text());d['sampling']='eqgpt_model';rows.append(d)
with (r/'eqgpt_pure_results.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
dump(r/'EQGPT_PURE_COMPLETE.json',dict(status='PASS' if not failed else 'FINISHED_WITH_CASE_FAILURES',completed=len(done),failed=failed))
