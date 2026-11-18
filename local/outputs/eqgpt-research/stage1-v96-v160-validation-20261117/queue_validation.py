import os,json,subprocess,time,sys
from pathlib import Path
root=Path(__file__).resolve().parent
jobs=json.loads((root/'matrix.json').read_text());running=[];done=[];failed=False
while jobs or running:
 while jobs and len(running)<10 and not failed:
  j=jobs.pop(0);folder=root/'jobs'/j['job'];folder.mkdir(parents=True,exist_ok=True)
  cmd=[sys.executable,'-u',str(root/'pretrain_tune.py'),'--campaign',str(root)]
  for k,v in j.items():cmd+=['--'+k.replace('_','-'),str(v)]
  with (folder/'run.log').open('w') as f:p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT)
  running.append((j,p))
 for j,p in running[:]:
  rc=p.poll()
  if rc is not None:
   done.append(dict(job=j['job'],returncode=rc));running.remove((j,p));failed=failed or rc!=0
 state=dict(time=time.time(),concurrency_limit=10,running=[dict(job=j['job'],pid=p.pid) for j,p in running],completed=done,pending=[j['job'] for j in jobs],failed=failed)
 tmp=root/'queue_status.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(root/'queue_status.json')
 if failed and not running:break
 if jobs or running:time.sleep(5)
if not failed:
 with (root/'analysis.log').open('w') as f:
  result=subprocess.run([sys.executable,str(root/'analyze_results.py')],stdout=f,stderr=subprocess.STDOUT)
 (root/'analysis_status.json').write_text(json.dumps(dict(returncode=result.returncode,time=time.time()),indent=2))
