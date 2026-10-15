from pathlib import Path
from PIL import Image,ImageOps

def parse_pages(value,count):
 if count<1:raise ValueError('Хуудас алга.')
 if not value.strip() or value.strip().lower() in ('all','бүгд'):return list(range(count))
 result=[]
 try:
  for part in value.split(','):
   bounds=part.strip().split('-')
   if len(bounds)==1:a=b=int(bounds[0])
   elif len(bounds)==2:a,b=map(int,bounds)
   else:raise ValueError()
   if a<1 or b<a or b>count:raise ValueError()
   for n in range(a-1,b):
    if n not in result:result.append(n)
 except (ValueError,TypeError):raise ValueError(f'1–{count} хүрээнд хуудас сонгоно уу. Жишээ: 1,3-5')
 return result

def prepare_ocr_image(source,output,rotation=0,grayscale=False,deskew=False):
 with Image.open(source) as original:
  image=ImageOps.exif_transpose(original).convert('RGB')
  if rotation not in (0,90,180,270):raise ValueError('Эргүүлэх өнцөг буруу.')
  if rotation:image=image.rotate(-rotation,expand=True,fillcolor='white')
  if deskew:
   import cv2,numpy as np
   gray=np.array(image.convert('L'));edges=cv2.Canny(gray,50,150);lines=cv2.HoughLinesP(edges,1,np.pi/180,threshold=80,minLineLength=max(50,gray.shape[1]//5),maxLineGap=20)
   angles=[]
   if lines is not None:
    for line in lines[:,0]:
     x1,y1,x2,y2=line;angle=np.degrees(np.arctan2(y2-y1,x2-x1))
     if abs(angle)<=10:angles.append(angle)
   if angles:image=image.rotate(float(np.median(angles)),expand=True,fillcolor='white')
  if grayscale:image=ImageOps.grayscale(image)
  image.save(output,'PNG')
 return Path(output)
