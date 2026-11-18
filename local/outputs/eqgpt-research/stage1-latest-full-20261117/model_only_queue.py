import json,subprocess,sys,os,time,fcntl,hashlib,csv
from pathlib import Path
r=Path(__file__).resolve().parent
lock=(r/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
gpu='GPU-e857f4d0-daa6-f33d-3dc8-927f15ab7d59';env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu,PYTHONPATH=str(r/'src'),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',STAGE1_SEARCH_CAP_GIB='14')
def dump(p,d):
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.replace(p)
def dest(j):return r/'search/results'/str(j['scale'])/j['split']/j['arm']/'model'/str(j['seed'])/j['case']
def complete(j):
 p=dest(j)/'complete.json'
 if not p.exists():return False
 m=json.loads(p.read_text());assert m['status']=='PASS'
 for name,digest in m['files'].items():assert hashlib.sha256((p.parent/name).read_bytes()).hexdigest()==digest
 return True
jobs=json.loads((r/'model_only_jobs.json').read_text());assert len(jobs)==288 and all(j['random_fraction']==0 for j in jobs)
done=[j for j in jobs if complete(j)];pending=[j for j in jobs if not complete(j)];active=[];failed=[]
while pending or active:
 for j,p,f in active[:]:
  rc=p.poll()
  if rc is not None:
   f.close();active.remove((j,p,f))
   if rc==0 and complete(j):done.append(j)
   else:failed.append(dict(job=j,returncode=rc))
 if pending and len(active)<6:
  used=int(subprocess.check_output(['nvidia-smi','--id='+gpu,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
  if used+15*1024<=92*1024 and (len(active)+1)*14<=84:
   j=pending.pop(0);cmd=[sys.executable,'-u',str(r/'search_case.py')]
   for k,v in j.items():cmd+=['--'+k.replace('_','-'),str(v)]
   name='-'.join(str(v) for v in j.values());f=(r/'logs'/('search-'+name+'.log')).open('w');p=subprocess.Popen(cmd,cwd=r,env=env,stdout=f,stderr=subprocess.STDOUT);active.append((j,p,f))
 state=dict(phase='model_only_search',time=time.time(),total=288,completed=len(done),pending=len(pending),active=[dict(job=j,pid=p.pid) for j,p,f in active],failed=failed,deferred_mix20=288,gpu=gpu,worker_cap_gib=14,limit=6)
 dump(r/'queue_status.json',state);dump(r/'model_only_status.json',state)
 if pending or active:time.sleep(5)
rows=[]
for j in done:
 d=json.loads((dest(j)/'result.json').read_text());d['sampling']='model';rows.append(d)
with (r/'model_only_case_results.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
groups={}
for d in rows:
 k=(d['scale'],d['split'],d['arm']);groups.setdefault(k,[]).append(d)
dump(r/'model_only_summary.json',dict(results=[dict(scale=k[0],split=k[1],arm=k[2],cases=len(v),top1=sum(x['top1'] for x in v),top10=sum(x['top10'] for x in v)) for k,v in groups.items()],failed=failed))
dump(r/'MODEL_ONLY_COMPLETE.json',dict(status='PASS' if not failed else 'FINISHED_WITH_CASE_FAILURES',completed=len(done),failed=failed,mix20='deferred',time=time.time()))
