import os,json,subprocess,time,sys
from pathlib import Path
root=Path(__file__).resolve().parent
jobs=json.loads((root/'matrix.json').read_text());running=[];done=[]
while jobs or running:
 while jobs and len(running)<2:
  j=jobs.pop(0);folder=root/'jobs'/j['job'];folder.mkdir(parents=True,exist_ok=True)
  cmd=[sys.executable,'-u',str(root/'pretrain_tune.py'),'--campaign',str(root),'--arm','ast_bpe_288','--seed','525']
  for k,v in j.items():cmd += ['--'+k.replace('_','-'),str(v)]
  f=(folder/'run.log').open('w');p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);f.close();running.append((j,p))
 for j,p in running[:]:
  rc=p.poll()
  if rc is not None:
   done.append(dict(job=j['job'],returncode=rc));running.remove((j,p))
   if rc:jobs=[]
 state=dict(time=time.time(),running=[dict(job=j['job'],pid=p.pid) for j,p in running],completed=done,pending=[j['job'] for j in jobs]);tmp=root/'queue_status.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(root/'queue_status.json')
 if jobs or running:time.sleep(5)
