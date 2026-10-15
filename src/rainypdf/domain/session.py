from pathlib import Path
from copy import deepcopy
import uuid
import pymupdf as fitz
from rainypdf.domain.types import Command,SessionSnapshot
from rainypdf.engine.pdf import PdfEngine
class DocumentSession:
 def __init__(self,path,data):
  self.source=Path(path);self.data=data;self.history=[()];self.position=0;self.generation=0;self.saved_commands=()
 @classmethod
 def open(cls,path,password=None):
  try:
   with fitz.open(path) as d:
    if not d.is_pdf or len(d)<1:raise ValueError('PDF файл биш эсвэл хоосон байна.')
    if d.needs_pass and not d.authenticate(password or ''):raise ValueError('Нууц үг шаардлагатай эсвэл буруу байна.')
    if d.get_sigflags()>0:raise ValueError('Тоон гарын үсэгтэй PDF байна. Засахад гарын үсэг хүчингүй болно. Эхлээд баталгаажуулсан хуулбар нээнэ үү.')
    data=d.tobytes(encryption=fitz.PDF_ENCRYPT_NONE)
   return cls(path,data)
  except (fitz.FileDataError,fitz.EmptyFileError,RuntimeError) as e:raise ValueError('PDF нээж чадсангүй. Файл гэмтсэн байж болно.') from e
 def snapshot(self):return SessionSnapshot(self.source,self.data,deepcopy(self.history[self.position]),self.generation)
 @property
 def page_ids(self):return PdfEngine.page_ids(self.snapshot())
 @property
 def dirty(self):return self.history[self.position]!=self.saved_commands
 def apply(self,command):
  command=deepcopy(command)
  if command.kind=='duplicate':command.payload['new_id']=uuid.uuid4().hex
  candidate=SessionSnapshot(self.source,self.data,self.history[self.position]+(command,),self.generation+1)
  with PdfEngine.document(candidate):pass
  self.history=self.history[:self.position+1]+[candidate.commands]
  if len(self.history)>201:self.history.pop(0)
  self.position=len(self.history)-1;self.generation+=1
 def undo(self):
  if not self.position:return False
  self.position-=1;self.generation+=1;return True
 def redo(self):
  if self.position>=len(self.history)-1:return False
  self.position+=1;self.generation+=1;return True
 def mark_saved(self):self.saved_commands=deepcopy(self.history[self.position])

 def edit_overlay(self,index,rect=None,delete=False):
  commands=list(deepcopy(self.history[self.position]))
  if index<0 or index>=len(commands) or commands[index].kind not in ('text','image','highlight','underline','strikeout','rectangle','note','ink'):raise ValueError('Зөвхөн өөрийн нэмсэн объектыг сонгоно уу.')
  if delete:commands.pop(index)
  else:
   if not rect:raise ValueError('Шинэ байрлал сонгоно уу.')
   old=commands[index].payload['rect']
   if commands[index].kind=='ink':
    if old[2]<=old[0] or old[3]<=old[1]:raise ValueError('Зургийн хүрээ буруу.')
    commands[index].payload['points']=[(rect[0]+(x-old[0])*(rect[2]-rect[0])/(old[2]-old[0]),rect[1]+(y-old[1])*(rect[3]-rect[1])/(old[3]-old[1])) for x,y in commands[index].payload['points']]
   commands[index].payload['rect']=list(rect)
  candidate=SessionSnapshot(self.source,self.data,tuple(commands),self.generation+1)
  with PdfEngine.document(candidate):pass
  self.history=self.history[:self.position+1]+[candidate.commands]
  if len(self.history)>201:self.history.pop(0)
  self.position=len(self.history)-1;self.generation+=1
