import pytest,pymupdf as fitz
from PIL import Image
from rainypdf.conversion.images import images_to_pdf,pdf_to_images
from rainypdf.engine.pages import merge,export_pages
from rainypdf.engine.print_layout import build_id_layout,build_photo_sheet
from rainypdf.engine.compression import compress
from rainypdf.domain.session import DocumentSession

def test_image_a4_and_export_dpi(tmp_path):
 image=tmp_path/'зураг.png';Image.new('RGB',(600,400),'red').save(image)
 p=tmp_path/'зураг.pdf';images_to_pdf([image],{'a4':True,'margin':10},p)
 with fitz.open(p) as d:assert d.page_count==1;assert d[0].rect.width==pytest.approx(595.28,abs=.1)
 files=pdf_to_images(DocumentSession.open(p).snapshot(),{'dpi':72},tmp_path/'images');assert Image.open(files[0]).width==596

def test_merge_split_and_compress(pdf,tmp_path):
 out=tmp_path/'merged.pdf';merge([pdf,pdf],out)
 with fitz.open(out) as d:assert len(d)==6
 s=DocumentSession.open(out);split=tmp_path/'split.pdf';export_pages(s.snapshot(),[s.page_ids[3]],split)
 with fitz.open(split) as d:assert len(d)==1;assert 'Page 1' in d[0].get_text()
 result=compress(s.snapshot(),tmp_path/'small.pdf');assert result['after']>0;assert isinstance(result['saved'],int)

def test_id_photo_layout_geometry(tmp_path):
 p=tmp_path/'img.png';Image.new('RGB',(400,300),'green').save(p)
 for data,count in [(build_id_layout(p,p,(85.6,54)),2),(build_photo_sheet(p,(35,45),'fit',3,4),12)]:
  with fitz.open(stream=data,filetype='pdf') as d:
   assert len(d)==1;assert len(d[0].get_image_rects(d[0].get_images()[0][0]))==count
 with pytest.raises(ValueError):build_photo_sheet(p,(200,200),'fit',3,4)
