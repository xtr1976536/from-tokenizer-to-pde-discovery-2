"""Bounded CPU numerical worker; CUDA/model state never enters this process.

Each RPC has a parent-enforced wall deadline. Linux RLIMIT_AS bounds address
space before scientific imports; crashes/timeouts kill only the CPU worker.
"""
from collections import OrderedDict
from dataclasses import dataclass
import os,pickle,select,struct,subprocess,sys,time
from pathlib import Path
from .contracts import InvalidCandidate


@dataclass
class RemoteSystem:
    text:str
    structure_key:str
    term_counts:tuple
    anchor_indices:tuple


class SafeBackend:
    fields=('u','v','p');equation_count=3;spatial_dimensions=2
    term_count_convention='canonical_lhs_plus_rhs_before_stencil_expansion'
    def __init__(self,compile_seconds=15,fit_seconds=30,forecast_seconds=90,memory_mb=4096,**numerics):
        self.limits=dict(compile_seconds=compile_seconds,fit_seconds=fit_seconds,
                         forecast_seconds=forecast_seconds,memory_mb=memory_mb)
        self.numerics=numerics;self.process=None;self.last_diagnostics={};self.restarts=0
        self.on_progress=None
    def _start(self):
        env=os.environ.copy()
        env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='')
        root=str(Path(__file__).resolve().parents[1]);env['PYTHONPATH']=root+os.pathsep+env.get('PYTHONPATH','')
        self.process=subprocess.Popen([sys.executable,'-u','-m','stage2_main_v1.safe_backend','worker',str(self.limits['memory_mb'])],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=None,env=env,bufsize=0)
        os.set_blocking(self.process.stdin.fileno(),False)
    def close(self):
        if self.process is not None:
            p=self.process;self.process=None
            if p.poll() is None:p.kill()
            p.wait(timeout=5)
            p.stdin.close();p.stdout.close()
    def __del__(self):
        try:self.close()
        except Exception:pass
    def _request(self,action,system=None,**arguments):
        if self.process is None or self.process.poll() is not None:self.close();self._start()
        p=self.process;start=time.monotonic();seconds=self.limits[dict(parse='compile_seconds',fit='fit_seconds',forecast='forecast_seconds')[action]]
        window=arguments.get('visible',{}).get('_cache_key')
        def progress(phase,**extra):
            if self.on_progress is not None:
                self.on_progress(dict(action=action,phase=phase,worker_pid=p.pid,window=window,
                    wall_limit_seconds=seconds,memory_limit_mb=self.limits['memory_mb'],
                    elapsed_seconds=time.monotonic()-start,time=time.time(),**extra))
        progress('started')
        payload=pickle.dumps(dict(action=action,text=system.text if system is not None else arguments.pop('text',None),
                                  numerics=self.numerics,arguments=arguments),protocol=5)
        try:
            # One writer; payload is scientific arrays and already parsed text,
            # never model weights. Worker reads continuously while this writes.
            pending=memoryview(struct.pack('!Q',len(payload))+payload)
            while pending:
                remaining=seconds-(time.monotonic()-start)
                if remaining<=0 or not select.select([],[p.stdin],[],max(0,remaining))[1]:
                    raise TimeoutError(action+' input transfer deadline')
                try:sent=os.write(p.stdin.fileno(),pending[:65536])
                except BlockingIOError:continue
                pending=pending[sent:]
            def read(size):
                parts=[];left=size
                while left:
                    remaining=seconds-(time.monotonic()-start)
                    if remaining<=0:raise TimeoutError(action+' wall deadline')
                    if not select.select([p.stdout],[],[],min(.25,remaining))[0]:
                        if sys.platform=='darwin':
                            rss=int(subprocess.check_output(['ps','-o','rss=','-p',str(p.pid)],timeout=1).strip() or 0)
                            if rss>self.limits['memory_mb']*1024:raise MemoryError('Worker RSS cap')
                        continue
                    chunk=os.read(p.stdout.fileno(),min(left,1048576))
                    if not chunk:raise EOFError('Numerical worker exited')
                    parts.append(chunk);left-=len(chunk)
                return b''.join(parts)
            length=struct.unpack('!Q',read(8))[0]
            if length>64*1024**2:raise ValueError('Worker response size exceeded')
            response=pickle.loads(read(length))
        except (TimeoutError,EOFError,BrokenPipeError,OSError,ValueError,MemoryError) as error:
            self.close();self.restarts+=1
            progress('resource_rejected',error=str(error))
            raise InvalidCandidate(f'Isolated {action} failed: {error}; cap={seconds}s/{self.limits["memory_mb"]}MiB') from error
        except BaseException:
            # External cancellation/deadline must not leave an in-flight RPC
            # whose late response could be mistaken for the next candidate.
            self.close();self.restarts+=1;raise
        self.last_diagnostics=response.get('diagnostics',{})
        self.last_diagnostics['isolation']=dict(worker_pid=p.pid,seconds=time.monotonic()-start,
            worker_peak_rss_mb=response.get('worker_peak_rss_mb'),memory_cap_mb=self.limits['memory_mb'],
            kernel_address_space_limit_mb=response.get('kernel_address_space_limit_mb'))
        if response['status']!='ok':
            progress('rejected',error=response['error'])
            if response.get('fatal'):self.close();self.restarts+=1
            if response['status']=='bug':raise RuntimeError(response['error'])
            raise InvalidCandidate(response['error'])
        progress('complete',worker_peak_rss_mb=response.get('worker_peak_rss_mb'))
        return response['value']
    def parse(self,text):return RemoteSystem(text,**self._request('parse',text=text))
    def structure_key(self,system):return system.structure_key
    def term_counts(self,system):return system.term_counts
    def fit(self,system,visible,mask):return self._request('fit',system,visible=visible,mask=mask)
    def forecast(self,system,coefficients,visible,future_times,mask):
        return self._request('forecast',system,coefficients=coefficients,visible=visible,future_times=future_times,mask=mask)


def worker(memory_mb):
    import resource
    if sys.platform.startswith('linux'):
        resource.setrlimit(resource.RLIMIT_AS,(memory_mb*1024**2,memory_mb*1024**2))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    from .implicit_backend import ImplicitBackend
    backend=None;systems=OrderedDict();source=sys.stdin.buffer;dest=sys.stdout.buffer
    def read(size):
        pieces=[]
        while size:
            data=source.read(size)
            if not data:raise EOFError()
            pieces.append(data);size-=len(data)
        return b''.join(pieces)
    while True:
        try:header=read(8)
        except EOFError:return
        request=pickle.loads(read(struct.unpack('!Q',header)[0]))
        try:
            if backend is None:backend=ImplicitBackend(**request['numerics'])
            text=request['text']
            if text not in systems:
                systems[text]=backend.parse(text)
                while len(systems)>16:systems.popitem(last=False)
            systems.move_to_end(text);system=systems[text];action=request['action']
            if action=='parse':value=dict(structure_key=system.structure_key,term_counts=system.term_counts,anchor_indices=system.anchor_indices)
            else:value=getattr(backend,action)(system,**request['arguments'])
            response=dict(status='ok',value=value,diagnostics=backend.last_diagnostics)
        except InvalidCandidate as error:response=dict(status='rejected',error=str(error),diagnostics=backend.last_diagnostics if backend else {})
        except (MemoryError,RecursionError) as error:
            response=dict(status='rejected',error='Isolated resource limit: '+type(error).__name__,fatal=True)
        except Exception as error:response=dict(status='bug',error=type(error).__name__+': '+str(error))
        peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        response['worker_peak_rss_mb']=peak/(1024**2 if sys.platform=='darwin' else 1024)
        response['kernel_address_space_limit_mb']=resource.getrlimit(resource.RLIMIT_AS)[0]/1024**2 if sys.platform.startswith('linux') else None
        payload=pickle.dumps(response,protocol=5);dest.write(struct.pack('!Q',len(payload)));dest.write(payload);dest.flush()
        if response.get('fatal'):return


if __name__=='__main__':worker(int(sys.argv[2]))
