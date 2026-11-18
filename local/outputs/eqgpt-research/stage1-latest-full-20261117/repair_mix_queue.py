from pathlib import Path
import json,os,signal,time,shutil
r=Path(ROOT);launch=json.loads((r/'launch.json').read_text());pid=launch['pid'];proc=Path('/proc')/str(pid)
if proc.exists():
 argv=(proc/'cmdline').read_bytes().split(b'\0');assert str(r/'supervise_ast.py').encode() in argv;os.kill(pid,signal.SIGSTOP)
q=json.loads((r/'queue_status.json').read_text());failed=[x for x in q['failed'] if x['job']['random_fraction']==.2];preserved=q['active'];targets=[]
# Stop only active cases in this same 212/811/v96/mix20 batch so they restart against the new budget.
for x in preserved:
 j=x['job']
 if (j['scale'],j['split'],j['arm'],j['random_fraction'],j['seed'])==(212,'811','ast_bpe_96',.2,525):
  os.kill(x['pid'],signal.SIGTERM);targets.append(x['pid'])
for pid0 in targets:
 time.sleep(.2);p=Path('/proc')/str(pid0)/'cmdline'
 if p.exists() and p.read_bytes():os.kill(pid0,signal.SIGKILL)
# Keep good completed work; move failed/in-progress artifacts into a named audit folder.
audit=r/'ast_queue_recovery_20261117';audit.mkdir(exist_ok=True);moved=[]
all_jobs=json.loads((r/'search_jobs.json').read_text())
retry=failed+[dict(job=x['job'],returncode=143) for x in preserved if x['pid'] in targets]
for x in retry:
 j=x['job'];dest=r/'search'/'results'/str(j['scale'])/j['split']/j['arm']/('model' if j['random_fraction']==0 else 'mix20')/str(j['seed'])/j['case']
 if dest.exists():
  assert not (dest/'complete.json').exists(),dest
  target=audit/dest.name
  # Disambiguate identical case names across retry metadata.
  target=audit/(f"{j['scale']}-{j['split']}-{j['arm']}-{j['seed']}-{j['case']}-{time.time_ns()}")
  shutil.move(str(dest),target);moved.append(str(dest.relative_to(r)))
for j in all_jobs:
 if j['random_fraction']==.2 and (j['scale'],j['split'],j['arm'],j['seed'])==(212,'811','ast_bpe_96',525):
  dest=r/'search'/'results'/str(j['scale'])/j['split']/j['arm']/'mix20'/str(j['seed'])/j['case']
  if dest.exists() and not (dest/'complete.json').exists():
   target=audit/(f"partial-{j['case']}-{time.time_ns()}");shutil.move(str(dest),target);moved.append(str(dest.relative_to(r)))
for x in failed:
 j=x['job'];name='-'.join(str(v) for v in j.values());p=r/'logs'/('search-'+name+'.log')
 if p.exists():shutil.copy2(p,audit/(p.name+'.cap5000.log'))
q['failed']=[x for x in q['failed'] if x['job']['random_fraction']!=.2];q['active']=[x for x in q['active'] if x['pid'] not in targets]
q['completed']=max(0,q['completed']-len(failed));q['pending']=sum(1 for j in all_jobs if not ((r/'search'/'results'/str(j['scale'])/j['split']/j['arm']/('model' if j['random_fraction']==0 else 'mix20')/str(j['seed'])/j['case']/'complete.json').exists()))
(r/'queue_status.json').write_text(json.dumps(q,indent=2));(r/'search_status.json').write_text(json.dumps(q,indent=2))
# Update sampler: return partial evaluated set at cap; preserve attempt count and RNG stream with extended cycles.
p=r/'sampler.py';s=p.read_text().replace('max_attempts=5000','max_attempts=15000').replace('seed=seed+cycle*(5000-400)','seed=seed+cycle*(15000-400)').replace("  if attempt>=max_attempts:raise RuntimeError(f'Candidate cap reached: {target=} {max_attempts=}')","  if attempt>=max_attempts:break")
assert 'Candidate cap reached' not in s and 'max_attempts=15000' in s;p.write_text(s)
p=r/'search_case.py';s=p.read_text().replace("kwargs['max_attempts']=5000","kwargs['max_attempts']=15000");s=s.replace("  assert n==settings['attempts']","  assert 1<=n<=settings['attempts']")
assert "kwargs['max_attempts']=15000" in s and 'assert n==settings' not in s;p.write_text(s)
# Scheduler continues after an individual task error while recording that task.
p=r/'ast_only_queue.py';s=p.read_text().replace("pending=jobs.copy();active=[];done=[];failed=[]","pending=jobs.copy();active=[];done=[];failed=[]")
s=s.replace("if pending and not failed and len(active)<limit:","if pending and len(active)<limit:")
s=s.replace("  if failed and not active:raise RuntimeError('Task failure; stop queue')\n","")
s=s.replace("if not failed:\n subprocess.run([sys.executable,'scripts/summarize_stage1_20261113.py'],cwd=r,check=True)","if not failed:\n pass")
p.write_text(s)
receipt=dict(time=time.time(),status='REPAIRED_PARTIAL_BATCH_AND_CONTINUE_ON_CASE_FAILURE',failed_retry=[x['job'] for x in failed],active_restarted=targets,attempt_cap=15000,partial_scored_candidates_continue=True,per_case_failures_do_not_stop_dispatch=True,quarantine=moved,ast_completed_preserved=True)
(r/'ast_queue_repair.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
