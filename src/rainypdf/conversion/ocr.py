from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess,csv,io
from rainypdf.conversion.process import run_tool
from PIL import Image
import pymupdf as fitz
from rainypdf.conversion.runtime import tool,options,environment
from rainypdf.engine.output import atomic_export
from rainypdf.engine.pdf import validate_pdf,PdfEngine

def recognize_image(path,language='mon+eng'):
 if language not in ('mon','eng','mon+eng'):raise ValueError('OCR хэл буруу.')
 p=run_tool([tool('tesseract'),str(path),'stdout','-l',language,'--psm','3','-c','tessedit_create_tsv=1'],timeout=180,env=environment(),**options())
 if p.returncode:raise ValueError('OCR танилт амжилтгүй. Хэлний өгөгдөл байгаа эсэхийг шалгана уу.')
 rows=list(csv.DictReader(io.StringIO(p.stdout.decode('utf-8','replace')),delimiter='\t'));words=[];lines={}
 for r in rows:
  if r.get('level')!='5' or not r.get('text','').strip():continue
  key=tuple(r[k] for k in ('page_num','block_num','par_num','line_num'));lines.setdefault(key,[]).append(r['text'])
  words.append({'text':r['text'],'left':int(r['left']),'top':int(r['top']),'width':int(r['width']),'height':int(r['height']),'confidence':float(r['conf'])})
 return {'text':'\n'.join(' '.join(v) for v in lines.values()),'words':words}

def ocr_document(source,output,language='mon+eng',progress=None,pages=None,rotation=0,grayscale=False,deskew=False,page_mode='all'):
 def write(dest):
  with TemporaryDirectory(prefix='rainypdf-ocr-') as folder:
   folder=Path(folder);combined=fitz.open();original_pages=[]
   try:
    if isinstance(source,(str,Path)) and Path(source).suffix.lower()!='.pdf':
     im=Image.open(source).convert('RGB');files=[folder/'scan.png'];im.save(files[0]);doc=None
    else:
     doc=PdfEngine.document(source) if not isinstance(source,(str,Path)) else fitz.open(source);files=[]
     for i in pages if pages is not None else range(len(doc)):
      page=doc[i];path=folder/f'scan-{i}.png';page.get_pixmap(dpi=300,alpha=False).save(path);files.append(path);original_pages.append(i)
    try:
     for i,path in enumerate(files):
      if doc is not None and page_mode=='skip_text' and doc[original_pages[i]].get_text().strip():
       combined.insert_pdf(doc,from_page=original_pages[i],to_page=original_pages[i]);continue
      from rainypdf.conversion.page_options import prepare_ocr_image
      path=prepare_ocr_image(path,folder/f'prepared-{i}.png',rotation,grayscale,deskew)
      base=folder/f'result-{i}'
      p=run_tool([tool('tesseract'),str(path),str(base),'-l',language,'--psm','3','-c','tessedit_create_pdf=1'],timeout=180,env=environment(),**options())
      if p.returncode or not base.with_suffix('.pdf').exists():raise ValueError('OCR PDF үүсгэж чадсангүй. mon/eng хэлний санг шалгана уу.')
      with fitz.open(base.with_suffix('.pdf')) as page:combined.insert_pdf(page)
      if progress:progress((i+1)/len(files))
     combined.save(dest,garbage=4,deflate=True)
    finally:
     if doc:doc.close()
   finally:combined.close()
 return atomic_export(output,write,validate_pdf)

def recognize_pages(source,language='mon+eng',pages=None,rotation=0,grayscale=False,deskew=False):
 from rainypdf.conversion.images import image_bytes
 selected=pages;result_pages=[]
 with TemporaryDirectory(prefix='rainypdf-review-') as folder:
  if isinstance(source,(str,Path)) and Path(source).suffix.lower()!='.pdf':
   path=Path(folder)/'image.png';path.write_bytes(image_bytes(source));from rainypdf.conversion.page_options import prepare_ocr_image
   path=prepare_ocr_image(path,Path(folder)/'prepared.png',rotation,grayscale,deskew);result=recognize_image(path,language);result['image']=path.read_bytes();return [result]
  with (PdfEngine.document(source) if not isinstance(source,(str,Path)) else fitz.open(source)) as doc:
   indices=list(selected if selected is not None else range(len(doc)))
   if len(indices)>50:raise ValueError('Текст хянах OCR-д нэг удаад 50 хүртэл хуудас сонгоно уу.')
   for i in indices:
    page=doc[i];path=Path(folder)/f'{i}.png';page.get_pixmap(dpi=200,alpha=False).save(path)
    from rainypdf.conversion.page_options import prepare_ocr_image
    path=prepare_ocr_image(path,Path(folder)/f'prepared-{i}.png',rotation,grayscale,deskew);result=recognize_image(path,language);result['image']=path.read_bytes();result_pages.append(result)
 return result_pages
