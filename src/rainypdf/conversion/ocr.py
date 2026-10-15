from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess,csv,io
from PIL import Image
import pymupdf as fitz
from rainypdf.conversion.runtime import tool,options,environment
from rainypdf.engine.output import atomic_export
from rainypdf.engine.pdf import validate_pdf,PdfEngine

def recognize_image(path,language='mon+eng'):
 if language not in ('mon','eng','mon+eng'):raise ValueError('OCR хэл буруу.')
 p=subprocess.run([tool('tesseract'),str(path),'stdout','-l',language,'--psm','3','-c','tessedit_create_tsv=1'],capture_output=True,timeout=180,env=environment(),**options())
 if p.returncode:raise ValueError('OCR танилт амжилтгүй. Хэлний өгөгдөл байгаа эсэхийг шалгана уу.')
 rows=list(csv.DictReader(io.StringIO(p.stdout.decode('utf-8','replace')),delimiter='\t'));words=[];lines={}
 for r in rows:
  if r.get('level')!='5' or not r.get('text','').strip():continue
  key=tuple(r[k] for k in ('page_num','block_num','par_num','line_num'));lines.setdefault(key,[]).append(r['text'])
  words.append({'text':r['text'],'left':int(r['left']),'top':int(r['top']),'width':int(r['width']),'height':int(r['height']),'confidence':float(r['conf'])})
 return {'text':'\n'.join(' '.join(v) for v in lines.values()),'words':words}

def ocr_document(source,output,language='mon+eng',progress=None):
 def write(dest):
  with TemporaryDirectory(prefix='rainypdf-ocr-') as folder:
   folder=Path(folder);combined=fitz.open()
   try:
    if isinstance(source,(str,Path)) and Path(source).suffix.lower()!='.pdf':
     im=Image.open(source).convert('RGB');files=[folder/'scan.png'];im.save(files[0]);doc=None
    else:
     doc=PdfEngine.document(source) if not isinstance(source,(str,Path)) else fitz.open(source);files=[]
     for i,page in enumerate(doc):
      path=folder/f'scan-{i}.png';page.get_pixmap(dpi=300,alpha=False).save(path);files.append(path)
    try:
     for i,path in enumerate(files):
      base=folder/f'result-{i}'
      p=subprocess.run([tool('tesseract'),str(path),str(base),'-l',language,'--psm','3','-c','tessedit_create_pdf=1'],capture_output=True,timeout=180,env=environment(),**options())
      if p.returncode or not base.with_suffix('.pdf').exists():raise ValueError('OCR PDF үүсгэж чадсангүй. mon/eng хэлний санг шалгана уу.')
      with fitz.open(base.with_suffix('.pdf')) as page:combined.insert_pdf(page)
      if progress:progress((i+1)/len(files))
     combined.save(dest,garbage=4,deflate=True)
    finally:
     if doc:doc.close()
   finally:combined.close()
 return atomic_export(output,write,validate_pdf)

def recognize_pages(source,language='mon+eng'):
 from rainypdf.conversion.images import image_bytes
 pages=[]
 with TemporaryDirectory(prefix='rainypdf-review-') as folder:
  if isinstance(source,(str,Path)) and Path(source).suffix.lower()!='.pdf':
   path=Path(folder)/'image.png';path.write_bytes(image_bytes(source));result=recognize_image(path,language);result['image']=path.read_bytes();return [result]
  with (PdfEngine.document(source) if not isinstance(source,(str,Path)) else fitz.open(source)) as doc:
   if len(doc)>50:raise ValueError('Текст хянах OCR-д нэг удаад 50 хүртэл хуудас сонгоно уу.')
   for i,page in enumerate(doc):
    path=Path(folder)/f'{i}.png';page.get_pixmap(dpi=200,alpha=False).save(path);result=recognize_image(path,language);result['image']=path.read_bytes();pages.append(result)
 return pages
