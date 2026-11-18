import os,json,subprocess,time,sys
from pathlib import Path
root=Path(__file__).resolve().parent
class ExistingProcess:
 def __init__(self,pid,folder):self.pid=pid;self.folder=folder
 def poll(self):
  if (self.folder/'COMPLETE.json').exists():return 0
  proc=Path('/proc')/str(self.pid)/'stat'
  try:
   if proc.read_text().split(') ')[1].split()[0]=='Z':return 1
  except FileNotFoundError:return 1
  return None
matrix=json.loads((root/'matrix.json').read_text());by_id={j['job']:j for j in matrix}
state=json.loads((root/'queue_status.json').read_text())
jobs=[by_id[n] for n in state['pending']];done=state['completed']
running=[(by_id[x['job']],ExistingProcess(x['pid'],root/'jobs'/x['job'])) for x in state['running']]
while jobs or running:
 while jobs and len(running)<10:
  j=jobs.pop(0);folder=root/'jobs'/j['job'];folder.mkdir(parents=True,exist_ok=True)
  cmd=[sys.executable,'-u',str(root/'pretrain_tune.py'),'--campaign',str(root),'--arm','ast_bpe_128','--seed','525']
  for k,v in j.items():cmd += ['--'+k.replace('_','-'),str(v)]
  f=(folder/'run.log').open('w');p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);f.close();running.append((j,p))
 for j,p in running[:]:
  rc=p.poll()
  if rc is not None:
   done.append(dict(job=j['job'],returncode=rc));running.remove((j,p))
   if rc:jobs=[]
 state=dict(time=time.time(),running=[dict(job=j['job'],pid=p.pid) for j,p in running],completed=done,pending=[j['job'] for j in jobs]);tmp=root/'queue_status.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(root/'queue_status.json')
 if jobs or running:time.sleep(5)
