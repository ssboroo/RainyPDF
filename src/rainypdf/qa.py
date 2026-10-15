"""Synthetic-only packaged regression; does not open user documents or use network."""
from pathlib import Path
import json,traceback

def run(folder):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);results={};report={'ready':False,'checks':results}
 try:
  import pymupdf as fitz
  from PIL import Image,ImageDraw,ImageFont
  from rainypdf.engine.fonts import FONT
  from rainypdf.domain.session import DocumentSession
  from rainypdf.domain.types import Command
  from rainypdf.engine.pdf import PdfEngine
  from rainypdf.conversion.ocr import recognize_image,ocr_document
  from rainypdf.conversion.docx import pdf_to_docx
  from rainypdf.conversion.xlsx import tables_to_xlsx
  from rainypdf.conversion.office import office_to_pdf
  from rainypdf.ui.main_window import MainWindow
  from PySide6.QtWidgets import QApplication
  app=QApplication.instance() or QApplication([])
  source=folder/'qa-source.pdf'
  with fitz.open() as d:
   p=d.new_page();p.insert_text((50,70),'RAINY SECRET',fontsize=16);d.save(source)
  session=DocumentSession.open(source);ident=session.page_ids[0]
  session.apply(Command('text',ident,{'rect':[50,120,500,180],'text':'Монгол Улс Өдөр бүр Үүл','size':20}))
  edited=folder/'qa-edited.pdf';edited.unlink(missing_ok=True);PdfEngine.export(session.snapshot(),edited)
  with fitz.open(edited) as d:assert 'Монгол' in d[0].get_text()
  results['mongolian_pdf_edit']=True
  session.apply(Command('redact',ident,{'rect':[40,45,300,85]}));redacted=folder/'qa-redacted.pdf';redacted.unlink(missing_ok=True);PdfEngine.export(session.snapshot(),redacted)
  with fitz.open(redacted) as d:assert 'SECRET' not in d[0].get_text()
  results['true_redaction']=True
  im=Image.new('RGB',(1700,450),'white');ImageDraw.Draw(im).text((40,80),'Монгол Улс Өдөр бүр Үүл 12345',font=ImageFont.truetype(str(FONT),70),fill='black');scan=folder/'qa-scan.png';im.save(scan)
  text=recognize_image(scan)['text'];assert 'Монгол' in text and '12345' in text;results['mongolian_ocr']=True;report['ocr_sample']=text
  searchable=folder/'qa-ocr.pdf';searchable.unlink(missing_ok=True);ocr_document(scan,searchable)
  with fitz.open(searchable) as d:assert 'Монгол' in d[0].get_text()
  results['searchable_scan']=True
  docx=folder/'qa.docx';docx.unlink(missing_ok=True);pdf_to_docx(DocumentSession.open(edited).snapshot(),docx);assert docx.stat().st_size>1000;results['pdf_to_word']=True
  office=folder/'qa-word.pdf';office.unlink(missing_ok=True);office_to_pdf(docx,office)
  with fitz.open(office) as d:assert 'Монгол' in ''.join(p.get_text() for p in d)
  results['word_to_pdf']=True
  xlsx=folder/'qa.xlsx';xlsx.unlink(missing_ok=True);tables_to_xlsx([{'cells':[['Нэр','Дүн'],['Бараа','00123'],['Текст','=1+2']],'source_page':1}],xlsx);excel=folder/'qa-excel.pdf';excel.unlink(missing_ok=True);office_to_pdf(xlsx,excel)
  with fitz.open(excel) as d:assert '00123' in ''.join(p.get_text() for p in d)
  results['excel_to_pdf']=True
  window=MainWindow();window.resize(1280,860);window.show();app.processEvents();window.grab().save(str(folder/'qa-home.png'));window.open_document(edited);app.processEvents();window.grab().save(str(folder/'qa-editor.png'))
  from rainypdf.ui.printing import render_printer
  from PySide6.QtPrintSupport import QPrinter
  printer=QPrinter(QPrinter.PrinterMode.HighResolution);printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat);printer.setOutputFileName(str(folder/'qa-printed.pdf'));printer.setResolution(150);render_printer(window.session.snapshot(),printer)
  with fitz.open(folder/'qa-printed.pdf') as d:assert len(d)==1
  results['qt_print_to_pdf']=True
  window.session=None;window.close();app.processEvents();results['gui_home_editor']=True;report['ready']=True
 except Exception:report['error']=traceback.format_exc()
 (folder/'qa-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 return 0 if report['ready'] else 1
