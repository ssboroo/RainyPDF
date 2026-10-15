from pathlib import Path
import pymupdf as fitz
from rainypdf.engine.fonts import FONT,color
from rainypdf.engine.output import atomic_export

def validate_pdf(path):
 with fitz.open(path) as d:
  if d.page_count<1:raise ValueError('Хоосон PDF байна.')
  for page in d:page.get_text()

class PdfEngine:
 @staticmethod
 def document(snapshot):
  d=fitz.open(stream=snapshot.data,filetype='pdf');ids=[f'p{i}' for i in range(len(d))]
  try:
   for c in snapshot.commands:
    p=c.payload;k=c.kind
    if k=='merge':
     with fitz.open(stream=p['data'],filetype='pdf') as extra:d.insert_pdf(extra);ids.extend(p['ids'])
     continue
    if k=='reorder':
     order=p['order']
     if len(order)!=len(ids) or set(order)!=set(ids):raise ValueError('Хуудасны дараалал буруу.')
     d.select([ids.index(i) for i in order]);ids=list(order);continue
    if c.page_id not in ids:raise ValueError('Хуудас олдсонгүй.')
    index=ids.index(c.page_id);page=d[index]
    if k=='delete':
     if len(ids)==1:raise ValueError('Сүүлийн хуудсыг устгах боломжгүй.')
     d.delete_page(index);ids.pop(index)
    elif k=='duplicate':d.fullcopy_page(index,to=index+1);ids.insert(index+1,p['new_id'])
    elif k=='rotate':page.set_rotation((page.rotation+int(p['angle']))%360)
    elif k in ('text','replace'):
     rect=fitz.Rect(p['rect']);size=float(p.get('size',14));text=str(p['text'])
     if rect.is_empty or size<4 or size>200:raise ValueError('Текстийн хүрээ/хэмжээ буруу.')
     # Measure using a scratch page before touching existing content.
     scratch=fitz.open();test=scratch.new_page(width=page.mediabox.width,height=page.mediabox.height)
     remaining=test.insert_textbox(rect,text,fontname='rainy',fontfile=str(FONT),fontsize=size,color=color(p.get('color','#172B4D')))
     scratch.close()
     if remaining<0:raise ValueError('Текст хүрээнд багтахгүй. Хүрээг томруулах эсвэл үсгийн хэмжээг багасгана уу.')
     if k=='replace':
      if page.get_images() and any(rect.intersects(r) for info in page.get_images() for r in page.get_image_rects(info[0])):raise ValueError('Энэ хүрээнд зураг давхцаж байна. Шинэ текст нэмэх хэрэгсэл ашиглана уу.')
      page.add_redact_annot(rect,fill=None);page.apply_redactions(images=0,graphics=0)
     page.insert_textbox(rect,text,fontname='rainy',fontfile=str(FONT),fontsize=size,color=color(p.get('color','#172B4D')))
    elif k=='image':page.insert_image(fitz.Rect(p['rect']),stream=p['data'],keep_proportion=True)
    elif k=='redact':
     page.add_redact_annot(fitz.Rect(p['rect']),fill=(0,0,0));page.apply_redactions(images=2,graphics=1)
     for a in list(page.annots() or []):
      if a.rect.intersects(fitz.Rect(p['rect'])):page.delete_annot(a)
     for widget in list(page.widgets() or []):
      if widget.rect.intersects(fitz.Rect(p['rect'])):page.delete_widget(widget)
     d.set_metadata({});d.del_xml_metadata();d.set_toc([])
     for name in d.embfile_names():d.embfile_del(name)
    elif k in ('highlight','underline','strikeout','rectangle','note','ink'):
     rect=fitz.Rect(p['rect'])
     if k=='note':a=page.add_text_annot(rect.tl,p.get('text','Тэмдэглэл'))
     elif k=='ink':a=page.add_ink_annot([[fitz.Point(x,y) for x,y in p['points']]])
     else:a=getattr(page,{'highlight':'add_highlight_annot','underline':'add_underline_annot','strikeout':'add_strikeout_annot','rectangle':'add_rect_annot'}[k])(rect)
     if k=='rectangle':a.set_colors(stroke=color(p.get('color','#2563EB')))
     a.update()
    else:raise ValueError('Дэмжигдээгүй үйлдэл: '+k)
   return d
  except Exception:d.close();raise
 @staticmethod
 def materialize(snapshot):
  with PdfEngine.document(snapshot) as d:return d.tobytes(garbage=4,deflate=True,clean=True)
 @staticmethod
 def export(snapshot,path,overwrite=False):
  if Path(path).resolve()==snapshot.source.resolve():raise ValueError('Эх файлаа хадгална. Өөр нэр сонгоно уу.')
  return atomic_export(path,lambda p:p.write_bytes(PdfEngine.materialize(snapshot)),validate_pdf,overwrite)
 @staticmethod
 def render(snapshot,page_id,scale=1):
  with PdfEngine.document(snapshot) as d:
   ids=PdfEngine.page_ids(snapshot);return d[ids.index(page_id)].get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
 @staticmethod
 def page_ids(snapshot):
  with fitz.open(stream=snapshot.data,filetype='pdf') as d:ids=[f'p{i}' for i in range(len(d))]
  for c in snapshot.commands:
   if c.kind=='delete':ids.remove(c.page_id)
   elif c.kind=='duplicate':ids.insert(ids.index(c.page_id)+1,c.payload['new_id'])
   elif c.kind=='reorder':ids=list(c.payload['order'])
   elif c.kind=='merge':ids.extend(c.payload['ids'])
  return ids
