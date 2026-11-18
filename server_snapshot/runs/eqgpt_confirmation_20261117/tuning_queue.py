import os,json,subprocess,time,sys,fcntl
from pathlib import Path
root=Path(__file__).resolve().parent
lock=(root/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
gpu='GPU-ba72db90-47e9-38fd-0e9e-905c3b1798b5'
class ExistingProcess:
 def __init__(self,pid,folder):self.pid=pid;self.folder=folder
 def poll(self):
  if (self.folder/'COMPLETE.json').exists():return 0
  try:
   if (Path('/proc')/str(self.pid)/'stat').read_text().split(') ')[1].split()[0]=='Z':return 1
  except FileNotFoundError:return 1
  return None
matrix=json.loads((root/'matrix.json').read_text());byid={j['job']:j for j in matrix};state=json.loads((root/'queue_status.json').read_text())
jobs=[byid[k] for k in state['pending']];running=[(byid[x['job']],ExistingProcess(x['pid'],root/'jobs'/x['job'])) for x in state['running']];done=state['completed'];failed=state['failed']
while jobs or running:
 for j,p in running[:]:
  rc=p.poll()
  if rc is not None:
   done.append(dict(job=j['job'],returncode=rc));running.remove((j,p));failed=failed or rc!=0
 if jobs and len(running)<8 and not failed:
  used=int(subprocess.check_output(['nvidia-smi','--id='+gpu,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
  if used+9*1024<=92*1024 and (len(running)+1)*8<=64:
   j=jobs.pop(0);folder=root/'jobs'/j['job'];folder.mkdir(parents=True,exist_ok=True)
   cmd=[sys.executable,'-u',str(root/'pretrain_tune.py'),'--campaign',str(root)]
   for k,v in j.items():cmd+=['--'+k.replace('_','-'),str(v)]
   with (folder/'run.log').open('w') as f:p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT)
   running.append((j,p))
 state=dict(time=time.time(),gpu=gpu,concurrency_limit=8,worker_cap_gib=8,total=11,running=[dict(job=j['job'],pid=p.pid) for j,p in running],completed=done,pending=[j['job'] for j in jobs],failed=failed)
 tmp=root/'queue_status.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(root/'queue_status.json')
 if failed and not running:break
 if jobs or running:time.sleep(5)
if not failed:
 with (root/'analysis.log').open('w') as f:p=subprocess.run([sys.executable,str(root/'analyze_results.py')],stdout=f,stderr=subprocess.STDOUT)
 (root/'analysis_status.json').write_text(json.dumps(dict(returncode=p.returncode,time=time.time()),indent=2))
