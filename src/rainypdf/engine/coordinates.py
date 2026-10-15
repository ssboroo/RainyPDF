import pymupdf as fitz

def view_rect_to_page(page,rect,scale):
 if scale<=0:raise ValueError('Харагдацын хэмжээ буруу.')
 result=fitz.Rect(*(float(v)/scale for v in rect))*page.derotation_matrix
 visible=page.rect*page.derotation_matrix
 return result & visible
