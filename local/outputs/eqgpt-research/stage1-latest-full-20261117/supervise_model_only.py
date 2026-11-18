import runpy,json,time,traceback
from pathlib import Path
r=Path(__file__).resolve().parent
try:runpy.run_path(str(r/'model_only_queue.py'),run_name='__main__')
except BaseException:
 (r/'MODEL_ONLY_FAILED.json').write_text(json.dumps(dict(time=time.time(),traceback=traceback.format_exc()),indent=2));raise
