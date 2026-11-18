import os,json,subprocess,time,sys
from pathlib import Path
root=Path(__file__).resolve().parent
jobs=json.loads((root/'matrix.json').read_text());running=[];done=[];failed=False
while jobs or running:
 # All four corrected seed525 runs finish before multi-seed replication begins.
 phase525=any(j['seed']==525 for j in jobs) or any(j['seed']==525 for j,p in running)
 while jobs and len(running)<8 and not failed:
  if phase525 and jobs[0]['seed']!=525:break
  j=jobs.pop(0);folder=root/'jobs'/j['job'];folder.mkdir(parents=True,exist_ok=True)
  cmd=[sys.executable,'-u',str(root/'pretrain_tune.py'),'--campaign',str(root),'--arm','ast_bpe_128']
  for k,v in j.items():cmd+=['--'+k.replace('_','-'),str(v)]
  with (folder/'run.log').open('w') as f:p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT)
  running.append((j,p))
 for j,p in running[:]:
  rc=p.poll()
  if rc is not None:
   done.append(dict(job=j['job'],returncode=rc));running.remove((j,p));failed=failed or rc!=0
 state=dict(time=time.time(),phase='corrected_seed525' if phase525 else 'seed526_527',concurrency_limit=8,running=[dict(job=j['job'],pid=p.pid) for j,p in running],completed=done,pending=[j['job'] for j in jobs],failed=failed)
 tmp=root/'queue_status.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(root/'queue_status.json')
 if failed and not running:break
 if jobs or running:time.sleep(5)
