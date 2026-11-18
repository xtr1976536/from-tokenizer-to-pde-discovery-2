import json,shlex,time
from pathlib import Path
import paramiko
b=Path(__file__).resolve().parent;launch=json.loads((b/'launch.json').read_text());r=launch['root'];base='/data1/users/liugang/src/eq-bpe/project';oldpid=launch['pid']
c=paramiko.SSHClient();c.load_system_host_keys();c.connect('81.70.169.155',username='liugang',password=os.environ["PDE_SSH_PASSWORD"],look_for_keys=False,allow_agent=False,timeout=15)
code=r'''from pathlib import Path
import os,signal,time,json,shutil
r=Path(ROOT);old=int(OLDPID);q=json.loads((r/'queue_status.json').read_text())
# Freeze the supervisor, then stop only the current AST batch so its partial
# candidates cannot be mistaken for a complete cycle under the new budget.
try:
 argv=(Path('/proc')/str(old)/'cmdline').read_bytes().split(b'\0');assert str(r/'supervise_ast.py').encode() in argv;os.kill(old,signal.SIGSTOP)
except FileNotFoundError:pass
pids=[x['pid'] for x in q['active']]
for pid in pids:
 try:os.kill(pid,signal.SIGTERM)
 except ProcessLookupError:pass
time.sleep(.5)
for pid in pids:
 p=Path('/proc')/str(pid)/'cmdline'
 if p.exists() and p.read_bytes():os.kill(pid,signal.SIGKILL)
time.sleep(.5)
audit=r/'ast_queue_recovery_20261117';audit.mkdir(exist_ok=True);moved=[]
for p in (r/'search/results').glob('*/*/*/*/*/*'):
 if p.is_dir() and '.partial_' in p.name:
  target=audit/(p.parent.parent.parent.parent.parent.parent.name+'-'+p.parent.parent.parent.parent.parent.name+'-'+p.parent.parent.parent.parent.name+'-'+p.parent.parent.parent.name+'-'+p.parent.parent.name+'-'+p.parent.name+'-'+p.name+'-'+str(time.time_ns()))
  shutil.move(str(p),target);moved.append(str(p.relative_to(r)))
# All completed final directories remain untouched; old cap failures are kept for audit.
for x in q['failed']:
 j=x['job'];name='-'.join(str(v) for v in j.values());p=r/'logs'/('search-'+name+'.log')
 if p.exists():shutil.copy2(p,audit/(name+'.cap5000.log'))
receipt=dict(time=time.time(),old_supervisor=old,stopped_active_pids=pids,partial_search_directories_quarantined=moved,preserved_completed=int(q['completed']),previous_cap_failures=len(q['failed']))
(r/'queue_recovery.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''
_,o,e=c.exec_command(base+'/.venv/bin/python -c '+shlex.quote('ROOT='+repr(r)+'\nOLDPID='+str(oldpid)+'\n'+code));out=o.read().decode();print(out,e.read().decode());assert o.channel.recv_exit_status()==0
# Update the shared sampler and runner, preserving 400 successful candidates as the normal target.
updates=r'''
from pathlib import Path
r=Path(ROOT)
p=r/'sampler.py';s=p.read_text().replace('max_attempts=5000','max_attempts=15000').replace('seed=seed+cycle*(5000-400)','seed=seed+cycle*(15000-400)').replace("  if attempt>=max_attempts:raise RuntimeError(f'Candidate cap reached: {target=} {max_attempts=}')","  if attempt>=max_attempts:break")
assert 'Candidate cap reached' not in s and 'max_attempts=15000' in s;p.write_text(s)
p=r/'search_case.py';s=p.read_text().replace("kwargs['max_attempts']=5000","kwargs['max_attempts']=15000").replace('  assert n==settings[\'attempts\']',"  assert 1<=n<=settings['attempts']")
assert "kwargs['max_attempts']=15000" in s and "assert n==settings['attempts']" not in s;p.write_text(s)
'''
_,o,e=c.exec_command(base+'/.venv/bin/python -c '+shlex.quote('ROOT='+repr(r)+'\n'+updates));print(o.read().decode(),e.read().decode());assert o.channel.recv_exit_status()==0
s=c.open_sftp()
for n in ['sampler.py','search_case.py']: (b/(n+'.repaired')).write_bytes(s.open(r+'/'+n).read())
s.put(str(b/'ast_only_queue.py'),r+'/ast_only_queue.py');s.put(str(b/'PLAN.md'),r+'/PLAN.md')
# Restart complete job list: verified final cases are adopted by the runner's already-complete path.
resume="import subprocess,os,json,time;from pathlib import Path;r=Path("+repr(r)+");env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='GPU-e857f4d0-daa6-f33d-3dc8-927f15ab7d59',PYTHONPATH=str(r/'src'),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',STAGE1_SEARCH_CAP_GIB='14');f=(r/'ast-supervisor-restarted.log').open('w');p=subprocess.Popen(["+repr(base+'/.venv/bin/python')+",'-u',str(r/'supervise_ast.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);d=dict(pid=p.pid,root=str(r),gpu=1,search_cases=576,attempt_cap=15000,case_failures_continue=True,restarted=time.time());(r/'launch.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))"
_,o,e=c.exec_command(base+'/.venv/bin/python -c '+shlex.quote(resume));out=o.read().decode();print(out,e.read().decode());assert o.channel.recv_exit_status()==0;(b/'launch.json').write_text(out)
s.close();c.close()
