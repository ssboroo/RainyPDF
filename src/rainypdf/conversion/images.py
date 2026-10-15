from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps
import pymupdf as fitz
from rainypdf.engine.output import atomic_export
from rainypdf.engine.pdf import validate_pdf,PdfEngine

def image_bytes(path):
 with Image.open(path) as im:
  if im.width*im.height>80_000_000:raise ValueError('Зураг хэт том байна.')
  out=BytesIO();ImageOps.exif_transpose(im).convert('RGB').save(out,'PNG');return out.getvalue()
def images_to_pdf(paths,options,output):
 if not paths:raise ValueError('Зураг сонгоно уу.')
 def write(p):
  d=fitz.open()
  try:
   for path in paths:
    data=image_bytes(path);im=Image.open(BytesIO(data));a4=options.get('a4',True)
    w,h=(595.276,841.89) if a4 else (im.width*72/96,im.height*72/96)
    if options.get('landscape') and a4:w,h=h,w
    margin=float(options.get('margin',10))*72/25.4
    if margin<0 or margin*2>=min(w,h):raise ValueError('Захын хэмжээ буруу.')
    page=d.new_page(width=w,height=h)
    if options.get('fill'):
     fill=ImageOps.fit(im,(max(1,round((w-2*margin)*2)),max(1,round((h-2*margin)*2))));buffer=BytesIO();fill.save(buffer,'PNG');data=buffer.getvalue()
    page.insert_image(fitz.Rect(margin,margin,w-margin,h-margin),stream=data,keep_proportion=True)
   d.save(p,deflate=True)
  finally:d.close()
 return atomic_export(output,write,validate_pdf)
def pdf_to_images(snapshot,options,folder,progress=None):
 from tempfile import mkdtemp
 import os,shutil
 dpi=int(options.get('dpi',150))
 if not 36<=dpi<=600:raise ValueError('DPI 36–600 хооронд байна.')
 folder=Path(folder)
 if folder.exists():raise FileExistsError('Зургийг шинэ хавтсанд гаргана. Өөр нэр сонгоно уу.')
 folder.parent.mkdir(parents=True,exist_ok=True);stage=Path(mkdtemp(prefix=f'.rainypdf-{os.getpid()}-images-',dir=folder.parent));outputs=[]
 try:
  with PdfEngine.document(snapshot) as d:
   indices=list(options.get('pages',range(len(d))))
   for n,i in enumerate(indices):
    ext=options.get('format','png')
    if ext not in ('png','jpg'):raise ValueError('PNG эсвэл JPG сонгоно уу.')
    name=f'page-{i+1}.{ext}';dest=stage/name;d[i].get_pixmap(dpi=dpi,alpha=False).save(str(dest));Image.open(dest).verify();outputs.append(folder/name)
    if progress:progress((n+1)/len(indices))
  os.rename(stage,folder)
  return outputs
 finally:
  if stage.exists():shutil.rmtree(stage)
