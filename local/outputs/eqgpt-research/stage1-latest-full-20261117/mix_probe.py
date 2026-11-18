import json,os,sys,subprocess,time,fcntl
from pathlib import Path
r=Path(__file__).resolve().parent
lock=(r/'mix_probe.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
gpu='GPU-ba72db90-47e9-38fd-0e9e-905c3b1798b5'
env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu,PYTHONPATH=str(r/'src'),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',STAGE1_SEARCH_CAP_GIB='10')
jobs=json.loads((r/'mix_probe_jobs.json').read_text());pending=jobs.copy();active=[];done=[];failed=[]
while pending or active:
 for j,p,f in active[:]:
  if p.poll() is not None:
   f.close();active.remove((j,p,f));(done if p.returncode==0 else failed).append(dict(job=j,returncode=p.returncode))
 if pending and len(active)<2:
  used=int(subprocess.check_output(['nvidia-smi','--id='+gpu,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
  if used+11*1024<=92*1024:
   j=pending.pop(0);cmd=[sys.executable,'-u',str(r/'search_case.py')]
   for k,v in j.items():cmd+=['--'+k.replace('_','-'),str(v)]
   f=(r/'logs'/('mix-probe-'+j['case']+'.log')).open('w');p=subprocess.Popen(cmd,cwd=r,env=env,stdout=f,stderr=subprocess.STDOUT);active.append((j,p,f))
 d=dict(time=time.time(),gpu=gpu,worker_cap_gib=10,total=2,completed=done,failed=failed,active=[dict(job=j,pid=p.pid) for j,p,f in active],pending=pending)
 tmp=r/'mix_probe_status.tmp';tmp.write_text(json.dumps(d,indent=2));tmp.replace(r/'mix_probe_status.json')
 if pending or active:time.sleep(5)
