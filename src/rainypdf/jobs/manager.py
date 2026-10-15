"""Process-owned file mailboxes keep a killed producer from blocking the UI."""
import multiprocessing as mp
import os,tempfile,shutil,threading,queue
from pathlib import Path
from PySide6.QtCore import QObject,QTimer
from rainypdf.domain.types import JobEvent
from rainypdf.jobs.worker import worker_main
from rainypdf.jobs.protocol import read_event,read_result
from rainypdf.conversion.process import terminate_tree
class JobManager(QObject):
 def __init__(self,callback,parent=None):
  super().__init__(parent);self.callback=callback;self.context=mp.get_context('spawn');self.jobs={};self.finishing=set();self.ready=queue.Queue();self.last={}
  self.timer=QTimer(self);self.timer.timeout.connect(self.poll);self.timer.start(80)
 def submit(self,request):
  if self.jobs:raise ValueError('Боловсруулалт ажиллаж байна. Дуусах эсвэл цуцлахыг хүлээнэ үү.')
  workspace=Path(tempfile.mkdtemp(prefix='rainypdf-job-'));process=self.context.Process(target=worker_main,args=(request,str(workspace)))
  try:process.start()
  except Exception:shutil.rmtree(workspace,ignore_errors=True);raise
  self.jobs[request.id]=(process,request,workspace);return request.id
 def cleanup(self,item):
  process,request,workspace=item;process.join(timeout=.2);shutil.rmtree(workspace,ignore_errors=True)
  for path in request.output.parent.glob(f'.rainypdf-{process.pid}-*'):
   try:
    if path.is_dir():shutil.rmtree(path)
    elif path.is_file():path.unlink(missing_ok=True)
   except OSError:pass
 def finish_result(self,ident,event,item):
  try:event.data=read_result(item[2])
  except Exception as e:event=JobEvent(ident,event.generation,'error',message=str(e)[:600])
  self.ready.put((ident,event))
 def poll(self):
  while True:
   try:ident,event=self.ready.get_nowait()
   except queue.Empty:break
   item=self.jobs.pop(ident,None);self.finishing.discard(ident)
   if item:self.cleanup(item);self.last.pop(ident,None);self.callback(event)
  for ident,item in list(self.jobs.items()):
   if ident in self.finishing:continue
   process,request,workspace=item
   try:payload=read_event(workspace)
   except Exception as e:payload={'id':ident,'generation':0,'state':'error','message':str(e)[:600]}
   if payload and payload!=self.last.get(ident):
    self.last[ident]=payload;event=JobEvent(**payload)
    if event.output is not None:event.output=Path(event.output)
    if event.state in ('done','error'):
     if event.data:
      self.finishing.add(ident);threading.Thread(target=self.finish_result,args=(ident,event,item),daemon=True).start()
     else:
      self.jobs.pop(ident);self.cleanup(item);self.last.pop(ident,None);self.callback(event)
     continue
    self.callback(event)
   if ident in self.jobs and not process.is_alive():
    self.jobs.pop(ident);self.cleanup(item);self.last.pop(ident,None)
    self.callback(JobEvent(ident,request.snapshot.generation if request.snapshot else 0,'error',message='Боловсруулалт гэнэт зогслоо.'))
 def cancel(self,ident):
  item=self.jobs.pop(ident,None)
  if not item:return
  process,request,_=item
  if process.is_alive():terminate_tree(process)
  self.cleanup(item);self.finishing.discard(ident);self.last.pop(ident,None)
  self.callback(JobEvent(ident,request.snapshot.generation if request.snapshot else 0,'cancelled',message='Цуцаллаа.'))
 def close(self):
  self.timer.stop()
  for ident in list(self.jobs):self.cancel(ident)
