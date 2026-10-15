from pathlib import Path
import pytest,pymupdf as fitz
from rainypdf.engine.output import atomic_export
from rainypdf.domain.session import DocumentSession
from rainypdf.domain.types import Command
from rainypdf.engine.pdf import PdfEngine

def test_atomic_failure_preserves_existing(tmp_path):
 p=tmp_path/'out.pdf';p.write_bytes(b'previous')
 def broken(t):t.write_bytes(b'partial');raise OSError('disk')
 with pytest.raises(OSError):atomic_export(p,broken,lambda p:None,overwrite=True)
 assert p.read_bytes()==b'previous';assert len(list(tmp_path.iterdir()))==1

def test_atomic_validation_and_collision(tmp_path):
 p=tmp_path/'out';p.write_bytes(b'old')
 with pytest.raises(FileExistsError):atomic_export(p,lambda t:t.write_bytes(b'new'),lambda t:None)
 with pytest.raises(ValueError):atomic_export(p,lambda t:t.write_bytes(b'new'),lambda t:(_ for _ in ()).throw(ValueError()),True)
 assert p.read_bytes()==b'old'

def test_session_history_and_source_immutable(pdf):
 source=pdf.read_bytes();s=DocumentSession.open(pdf);ids=s.page_ids
 s.apply(Command('rotate',ids[0],{'angle':90}));assert s.dirty
 assert PdfEngine.document(s.snapshot())[0].rotation==90
 assert s.undo();assert PdfEngine.document(s.snapshot())[0].rotation==0
 assert s.redo();s.undo();s.apply(Command('delete',ids[2],{}));assert not s.redo()
 assert len(s.page_ids)==2;assert pdf.read_bytes()==source

def test_text_add_replace_overflow_and_redaction(pdf):
 s=DocumentSession.open(pdf);page=s.page_ids[0]
 s.apply(Command('text',page,{'rect':[50,100,400,150],'text':'Монгол Өөрөө Үүл','size':18,'color':'#172B4D'}))
 d=PdfEngine.document(s.snapshot());assert 'Монгол Өөрөө Үүл' in d[0].get_text();d.close()
 s.apply(Command('replace',page,{'rect':[49,43,200,65],'text':'Шинэ','size':12,'color':'#000000'}))
 d=PdfEngine.document(s.snapshot());assert 'SECRET' not in d[0].get_text();assert 'Шинэ' in d[0].get_text();d.close()
 before=s.snapshot()
 with pytest.raises(ValueError):s.apply(Command('text',page,{'rect':[0,0,5,5],'text':'too long'*50,'size':20}))
 assert s.snapshot().commands==before.commands
 s.apply(Command('redact',page,{'rect':[0,0,595,160]}));d=PdfEngine.document(s.snapshot());assert 'Шинэ' not in d[0].get_text();assert 'SECRET' in d[1].get_text()

def test_page_operations_and_last_page_guard(pdf):
 s=DocumentSession.open(pdf);ids=s.page_ids
 s.apply(Command('reorder','',{'order':[ids[2],ids[0],ids[1]]}))
 assert 'Page 3' in PdfEngine.document(s.snapshot())[0].get_text()
 s.apply(Command('duplicate',ids[0],{}));assert len(s.page_ids)==4
 for ident in s.page_ids[:-1]:s.apply(Command('delete',ident,{}))
 with pytest.raises(ValueError):s.apply(Command('delete',s.page_ids[0],{}))

def test_invalid_password_and_frozen_source(pdf):
 s=DocumentSession.open(pdf);pdf.write_bytes(b'changed');assert PdfEngine.document(s.snapshot()).page_count==3
 with pytest.raises(ValueError):DocumentSession.open(pdf)

def test_export_source_same_rejected(pdf):
 s=DocumentSession.open(pdf)
 with pytest.raises(ValueError):PdfEngine.export(s.snapshot(),pdf)

def test_move_delete_added_object_undo(pdf):
 s=DocumentSession.open(pdf);ident=s.page_ids[0]
 s.apply(Command('text',ident,{'rect':[50,100,400,150],'text':'Overlay','size':14}))
 s.edit_overlay(0,[50,250,400,300]);d=PdfEngine.document(s.snapshot());assert d[0].search_for('Overlay')[0].y0>240
 s.edit_overlay(0,delete=True);d=PdfEngine.document(s.snapshot());assert 'Overlay' not in d[0].get_text()
 s.undo();assert 'Overlay' in PdfEngine.document(s.snapshot())[0].get_text()

def test_vector_redaction_removes_crossing_path(tmp_path):
 p=tmp_path/'vector.pdf'
 with fitz.open() as d:
  page=d.new_page();page.draw_line((20,100),(300,100),color=(1,0,0),width=5);d.save(p)
 s=DocumentSession.open(p);s.apply(Command('redact',s.page_ids[0],{'rect':[100,85,200,115]}))
 out=tmp_path/'redacted.pdf';PdfEngine.export(s.snapshot(),out)
 with fitz.open(out) as d:assert not any(x['color']==(1.,0.,0.) for x in d[0].get_drawings())

def test_ink_creation_and_move(pdf):
 s=DocumentSession.open(pdf);s.apply(Command('ink',s.page_ids[0],{'rect':[30,100,90,150],'points':[(30,100),(60,150),(90,100)]}))
 with PdfEngine.document(s.snapshot()) as d:assert len(list(d[0].annots()))==1
 s.edit_overlay(0,[130,200,190,250])
 with PdfEngine.document(s.snapshot()) as d:
  page=d[0];assert list(page.annots())[0].vertices[0][0]==pytest.approx((130,200))

def test_nonzero_media_origin_selection():
 from rainypdf.engine.coordinates import view_rect_to_page
 with fitz.open() as d:
  page=d.new_page(width=500,height=500);page.set_mediabox(fitz.Rect(100,100,400,400));page.insert_text((10,30),'SECRET')
  rect=view_rect_to_page(page,(0,0,90,50),1);assert 'SECRET' in page.get_textbox(rect)
