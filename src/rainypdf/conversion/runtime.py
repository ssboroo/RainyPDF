from pathlib import Path
import sys,shutil,os
ROOT=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[3]
RUNTIMES=ROOT/'runtimes'
def tool(name):
 candidates={'tesseract':[RUNTIMES/'tesseract'/'tesseract.exe'],'office':[RUNTIMES/'office'/'program'/'soffice.com',RUNTIMES/'office'/'program'/'soffice.exe']}[name]
 for p in candidates:
  if p.is_file():return str(p)
 value=shutil.which('tesseract' if name=='tesseract' else 'libreoffice')
 if value:return value
 raise ValueError(('OCR' if name=='tesseract' else 'Office хөрвүүлэлтийн')+' хөдөлгүүр олдсонгүй. Бүрэн суулгацаа дахин суулгана уу.')
def options():return {'creationflags':0x08000000} if os.name=='nt' else {}
def environment():
 env=os.environ.copy();data=RUNTIMES/'tesseract'/'tessdata'
 if data.exists():env['TESSDATA_PREFIX']=str(data)
 return env
