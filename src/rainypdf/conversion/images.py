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
    page=d.new_page(width=w,height=h);page.insert_image(fitz.Rect(margin,margin,w-margin,h-margin),stream=data,keep_proportion=True)
   d.save(p,deflate=True)
  finally:d.close()
 return atomic_export(output,write,validate_pdf)
def pdf_to_images(snapshot,options,folder):
 dpi=int(options.get('dpi',150))
 if not 36<=dpi<=600:raise ValueError('DPI 36–600 хооронд байна.')
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);outputs=[]
 with PdfEngine.document(snapshot) as d:
  for i in options.get('pages',range(len(d))):
   ext=options.get('format','png')
   if ext not in ('png','jpg'):raise ValueError('PNG эсвэл JPG сонгоно уу.')
   dest=folder/f'page-{i+1}.{ext}'
   def write(p):d[i].get_pixmap(dpi=dpi,alpha=False).save(str(p))
   atomic_export(dest,write,lambda p:Image.open(p).verify());outputs.append(dest)
 return outputs
