"""GPU campaign with pinned configs, bounded CPU workers and independent logs."""
import argparse,json,os,subprocess,sys,time,traceback
from pathlib import Path
from .runner import write


def worker(config_path,manifest,output):
    import torch
    from .data import SimulationData
    from .generator import factory
    from .runner import run,evaluate_frozen
    cfg=json.loads(Path(config_path).read_text());out=Path(output)
    torch.set_num_threads(4);torch.set_num_interop_threads(1)
    torch.cuda.set_per_process_memory_fraction(cfg.get('campaign',{}).get('cuda_memory_fraction',.20))
    write(out.parent/'worker_status.json',dict(stage='loading_model',pid=os.getpid(),started=time.time()))
    generator,numerics=factory(cfg)
    # Pretraining optimizer state is not used by online SFT, which resets Adam.
    generator.optimizer=None;torch.cuda.empty_cache()
    write(out.parent/'worker_status.json',dict(stage='auditing_data',pid=os.getpid(),time=time.time()))
    data=SimulationData(manifest,cfg)
    try:
        write(out.parent/'worker_status.json',dict(stage='training',pid=os.getpid(),time=time.time()))
        state=run(cfg,data,generator,numerics,out,1.)
        assert state['finished']
        write(out.parent/'worker_status.json',dict(stage='frozen_test',pid=os.getpid(),time=time.time()))
        evaluate_frozen(cfg,data,numerics,out)
        write(out.parent/'worker_status.json',dict(stage='complete',pid=os.getpid(),time=time.time()))
    finally:
        data.close()
        if hasattr(numerics,'close'):numerics.close()


def supervisor(root,manifest):
    root=Path(root);matrix=json.loads((root/'matrix.json').read_text())
    parallelism=int(matrix.get('parallelism',2))
    if not 1<=parallelism<=6:raise ValueError('Invalid campaign concurrency')
    active={};pending=list(matrix['jobs']);complete=[];failed=[];handles=[]
    def status():
        write(root/'queue_status.json',dict(supervisor_pid=os.getpid(),gpu=matrix.get('gpu',3),parallelism=parallelism,
            running=[dict(job=job,pid=p.pid) for job,p in active.items()],
            pending=pending,complete=complete,failed=failed,time=time.time(),
            queue_paused_on_failure=bool(failed)))
    while pending or active:
        for name,p in list(active.items()):
            code=p.poll()
            if code is None:continue
            del active[name]
            (complete if code==0 else failed).append(dict(job=name,exit_code=code))
        while pending and len(active)<parallelism and not failed:
            name=pending.pop(0);job=root/name;job.mkdir(exist_ok=False)
            f=(job/'run.log').open('w');handles.append(f)
            cmd=[sys.executable,'-u','-m','stage2_main_v1.full_campaign','worker',
                '--root',str(root),'--job',name,'--manifest',str(manifest)]
            p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
            active[name]=p
        status()
        if failed and not active:break
        time.sleep(10)
    status()
    for f in handles:f.close()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['worker','supervisor'])
    ap.add_argument('--root',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--job');a=ap.parse_args()
    if a.action=='supervisor':supervisor(a.root,a.manifest)
    else:
        try:worker(a.root/'configs'/(a.job+'.json'),a.manifest,a.root/a.job/'output')
        except Exception as error:
            write(a.root/a.job/'worker_status.json',dict(stage='failed',error=repr(error),traceback=traceback.format_exc(),pid=os.getpid(),time=time.time()))
            raise


if __name__=='__main__':main()
