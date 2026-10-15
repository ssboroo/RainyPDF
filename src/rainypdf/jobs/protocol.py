"""Small atomic event files, with large OCR results outside process pipes."""
import json,base64,os
from pathlib import Path
from dataclasses import asdict

def encode(value):
 if isinstance(value,bytes):return {'__rainy_bytes__':base64.b64encode(value).decode('ascii')}
 if isinstance(value,Path):return str(value)
 raise TypeError(type(value).__name__)
def decode(value):
 if set(value)=={'__rainy_bytes__'}:return base64.b64decode(value['__rainy_bytes__'],validate=True)
 return value

def emit(workspace,event):
 root=Path(workspace);payload=asdict(event)
 if payload['data'] is not None:
  body=json.dumps(payload['data'],default=encode,ensure_ascii=False).encode('utf-8')
  if len(body)>96*1024*1024:raise ValueError('OCR хяналтын үр дүн хэт том. Цөөн хуудас сонгоно уу.')
  (root/'result.tmp').write_bytes(body);os.replace(root/'result.tmp',root/'result.json');payload['data']={'stored':True}
 data=json.dumps(payload,default=encode,ensure_ascii=False).encode('utf-8')
 if len(data)>8192:raise ValueError('Ажлын төлөв хэт том.')
 (root/'event.tmp').write_bytes(data);os.replace(root/'event.tmp',root/'event.json')
def read_event(workspace):
 path=Path(workspace)/'event.json'
 if not path.exists():return None
 if path.stat().st_size>8192:raise ValueError('Ажлын төлөв буруу.')
 return json.loads(path.read_text(encoding='utf-8'))
def read_result(workspace):
 path=Path(workspace)/'result.json'
 if path.stat().st_size>96*1024*1024:raise ValueError('Үр дүн хэт том.')
 return json.loads(path.read_text(encoding='utf-8'),object_hook=decode)
