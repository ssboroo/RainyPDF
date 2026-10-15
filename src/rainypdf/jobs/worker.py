import os
from pathlib import Path
from rainypdf.domain.types import JobEvent

def worker_main(request,events,workspace=None):
 if workspace:
  import tempfile
  tempfile.tempdir=workspace
  os.environ["TMP"]=workspace;os.environ["TEMP"]=workspace;os.environ["TMPDIR"]=workspace
 os.environ["RAINYPDF_WORKER"]=str(os.getpid())
 if os.name!='nt':os.setsid()
 generation=request.snapshot.generation if request.snapshot else 0
 def progress(n):events.put(JobEvent(request.id,generation,'running',float(n),'Боловсруулж байна…'))
 try:
  progress(0);kind=request.kind;s=request.snapshot;o=request.options;dest=request.output;result_data=None
  if kind=='pdf':
   from rainypdf.engine.pdf import PdfEngine
   PdfEngine.export(s,dest,o.get('overwrite',False))
  elif kind=='compress':
   from rainypdf.engine.compression import compress
   result=compress(s,dest);events.put(JobEvent(request.id,generation,'running',1,f"{result['before']:,} → {result['after']:,} байт"))
  elif kind=='docx':
   from rainypdf.conversion.docx import pdf_to_docx
   pdf_to_docx(s,dest,o.get('mode','native_layout'))
  elif kind=='scan_table':
   from rainypdf.conversion.xlsx import extract_scan_tables
   result_data={'tables':extract_scan_tables(s,o.get('pages'),o.get('language','mon+eng'))}
  elif kind=='ocr_text':
   from rainypdf.conversion.ocr import recognize_pages
   result_data={'ocr_pages':recognize_pages(s or Path(o['source']),o.get('language','mon+eng'))}
  elif kind=='xlsx':
   from rainypdf.conversion.xlsx import extract_tables,tables_to_xlsx
   tables_to_xlsx(o.get('tables') or extract_tables(s),dest,o.get('numeric_columns'))
  elif kind=='ocr':
   from rainypdf.conversion.ocr import ocr_document
   ocr_document(s or Path(o['source']),dest,o.get('language','mon+eng'),progress)
  elif kind=='office':
   from rainypdf.conversion.office import office_to_pdf
   office_to_pdf(Path(o['source']),dest)
  elif kind=='images':
   from rainypdf.conversion.images import images_to_pdf
   images_to_pdf(o['sources'],o,dest)
  elif kind=='raster':
   from rainypdf.conversion.images import pdf_to_images
   pdf_to_images(s,o,dest)
  elif kind=='merge':
   from rainypdf.engine.pages import merge
   merge(o['sources'],dest)
  elif kind=='split':
   from rainypdf.engine.pages import export_pages
   export_pages(s,o['page_ids'],dest)
  else:raise ValueError('Дэмжигдээгүй боловсруулалт.')
  events.put(JobEvent(request.id,generation,'done',1,'Боловсруулалт дууслаа.',dest if result_data is None else None,data=result_data))
 except Exception as e:events.put(JobEvent(request.id,generation,'error',0,str(e)[:600]))
