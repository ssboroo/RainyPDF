import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest,pymupdf as fitz
@pytest.fixture
def pdf(tmp_path):
 p=tmp_path/'Эх баримт.pdf'
 d=fitz.open()
 for n in range(3):
  page=d.new_page(width=595,height=842);page.insert_text((50,60),f'Page {n+1} SECRET visible',fontsize=14)
 d.save(p);d.close();return p
