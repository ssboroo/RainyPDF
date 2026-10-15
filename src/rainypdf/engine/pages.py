from pathlib import Path
import pymupdf as fitz
from rainypdf.engine.output import atomic_export
from rainypdf.engine.pdf import PdfEngine,validate_pdf

def merge(paths,output):
 if not paths:raise ValueError('PDF файлуудаа сонгоно уу.')
 if Path(output).resolve() in [Path(p).resolve() for p in paths]:raise ValueError('Эх файлыг дарж бичихгүй.')
 def write(p):
  with fitz.open() as d:
   for source in paths:
    with fitz.open(source) as extra:
     if extra.needs_pass:raise ValueError('Нууц үгтэй файлыг эхлээд програмд нээнэ үү.')
     d.insert_pdf(extra)
   d.save(p,garbage=4,deflate=True)
 return atomic_export(output,write,validate_pdf)
def export_pages(snapshot,page_ids,output):
 if Path(output).resolve()==snapshot.source.resolve():raise ValueError('Өөр нэр сонгоно уу.')
 ids=PdfEngine.page_ids(snapshot)
 if not page_ids:raise ValueError('Хуудас сонгоно уу.')
 def write(p):
  with PdfEngine.document(snapshot) as d:
   d.select([ids.index(i) for i in page_ids]);d.save(p,garbage=4,deflate=True)
 return atomic_export(output,write,validate_pdf)
