import pymupdf as fitz
from PIL import Image,ImageOps
from io import BytesIO
from rainypdf.conversion.images import image_bytes
MM=72/25.4

def build_id_layout(front,back,dimensions_mm=(85.6,54)):
 w,h=[float(x)*MM for x in dimensions_mm]
 if w<=0 or h<=0 or w>555 or 2*h+80>802:raise ValueError('Хэмжээ A4 хуудсанд багтахгүй.')
 with fitz.open() as d:
  p=d.new_page(width=595.276,height=841.89)
  for i,img in enumerate([front,back]):
   x=(p.rect.width-w)/2;y=70+i*(h+35);p.insert_image(fitz.Rect(x,y,x+w,y+h),stream=image_bytes(img),keep_proportion=True)
  return d.tobytes(deflate=True)
def build_photo_sheet(image,size_mm=(35,45),crop='fit',rows=3,cols=4,margin_mm=10,gap_mm=4):
 w,h=[float(x)*MM for x in size_mm];rows=int(rows);cols=int(cols);gap=float(gap_mm)*MM;margin=float(margin_mm)*MM
 if min(w,h,rows,cols)<=0 or cols*w+(cols-1)*gap+2*margin>595.276 or rows*h+(rows-1)*gap+2*margin>841.89:raise ValueError('Сонгосон зураг/тоо A4 хуудсанд багтахгүй.')
 data=image_bytes(image)
 if crop=='fill':
  with Image.open(BytesIO(data)) as im:
   buf=BytesIO();ImageOps.fit(im,(round(w*4),round(h*4))).save(buf,'PNG');data=buf.getvalue()
 elif crop!='fit':raise ValueError('Fit/fill сонгоно уу.')
 with fitz.open() as d:
  p=d.new_page(width=595.276,height=841.89)
  for row in range(rows):
   for col in range(cols):
    x=margin+col*(w+gap);y=margin+row*(h+gap);p.insert_image(fitz.Rect(x,y,x+w,y+h),stream=data,keep_proportion=True)
  return d.tobytes(deflate=True)
