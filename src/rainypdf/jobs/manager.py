"""Own process trees and temporary files; deliver terminal states before UI callbacks."""
import multiprocessing as mp
import queue,os,subprocess,signal,tempfile,shutil
from pathlib import Path
from PySide6.QtCore import QObject,QTimer
from rainypdf.domain.types import JobEvent
from rainypdf.jobs.worker import worker_main
class JobManager(QObject):
 def __init__(self,callback,parent=None):
  super().__init__(parent)
  self.callback=callback;self.context=mp.get_context('spawn');self.events=self.context.Queue();self.jobs={}
  self.timer=QTimer(self);self.timer.timeout.connect(self.poll);self.timer.start(80)
 def submit(self,request):
  if self.jobs:raise ValueError('Боловсруулалт ажиллаж байна. Дуусах эсвэл цуцлахыг хүлээнэ үү.')
  workspace=Path(tempfile.mkdtemp(prefix='rainypdf-job-'))
  process=self.context.Process(target=worker_main,args=(request,self.events,str(workspace)))
  try:process.start()
  except Exception:shutil.rmtree(workspace,ignore_errors=True);raise
  self.jobs[request.id]=(process,request,workspace)
  return request.id
 def cleanup(self,item):
  process,request,workspace=item;process.join(timeout=.1)
  shutil.rmtree(workspace,ignore_errors=True)
  for path in request.output.parent.glob(f'.rainypdf-{process.pid}-*'):
   if path.is_file():path.unlink(missing_ok=True)
 def poll(self):
  while True:
   try:event=self.events.get_nowait()
   except queue.Empty:break
   if event.id not in self.jobs:continue
   if event.state in ('done','error'):
    item=self.jobs.pop(event.id);self.cleanup(item)
   self.callback(event)
  for ident,item in list(self.jobs.items()):
   process,request,_=item
   if not process.is_alive():
    if getattr(process,'_rainy_dead',False):
     self.jobs.pop(ident);self.cleanup(item)
     self.callback(JobEvent(ident,request.snapshot.generation if request.snapshot else 0,'error',message='Боловсруулалт гэнэт зогслоо.'))
    else:process._rainy_dead=True
 def cancel(self,ident):
  item=self.jobs.pop(ident,None)
  if not item:return
  process,request,_=item
  if process.is_alive():
   if os.name=='nt':subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True,creationflags=0x08000000)
   else:
    try:os.killpg(process.pid,signal.SIGTERM)
    except ProcessLookupError:process.terminate()
   process.join(timeout=3)
   if process.is_alive():process.kill();process.join(timeout=2)
  self.cleanup(item)
  self.callback(JobEvent(ident,request.snapshot.generation if request.snapshot else 0,'cancelled',message='Цуцаллаа.'))
 def close(self):
  self.timer.stop()
  for ident in list(self.jobs):self.cancel(ident)
