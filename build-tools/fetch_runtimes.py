"""Pinned upstream Windows runtimes; reject any checksum mismatch before extraction."""
from pathlib import Path
import hashlib,json,urllib.request,subprocess,shutil,sys
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'build'/'downloads';CACHE.mkdir(parents=True,exist_ok=True);OUT=ROOT/'runtimes';OUT.mkdir(exist_ok=True)
FILES={
 'tesseract.exe':('https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe','c885fff6998e0608ba4bb8ab51436e1c6775c2bafc2559a19b423e18678b60c9'),
 'office.msi':('https://downloadarchive.documentfoundation.org/libreoffice/old/25.8.4.2/win/x86_64/LibreOffice_25.8.4.2_Win_x86-64.msi','b2b23d91bda5ad6e97b38008b082060a55d2a3c7c269b2c0e78daca865133d48'),
}
COMMIT='87416418657359cb625c412a48b6e1d6d41c29bd'
MODELS={'mon':'a151a3806d61ac43619cd383896d551ba5c3b07388ffec6fc83c8c604d677570','eng':'7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2','osd':'9cf5d576fcc47564f11265841e5ca839001e7e6f38ff7f7aacf46d15a96b00ff'}
def download(url,sha,path):
 if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
  request=urllib.request.Request(url,headers={'User-Agent':'RAINY-PDF-build'})
  with urllib.request.urlopen(request,timeout=120) as response,path.open('wb') as dest:shutil.copyfileobj(response,dest)
 if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:raise ValueError('SHA256 mismatch: '+path.name)
 return path

def main():
 if sys.platform!='win32':raise SystemExit('Windows build required')
 manifest=[]
 for name,(url,sha) in FILES.items():
  path=download(url,sha,CACHE/name);manifest.append({'file':name,'url':url,'sha256':sha})
 tess=OUT/'tesseract'
 if not (tess/'tesseract.exe').exists():
  result=subprocess.run([str(CACHE/'tesseract.exe'),'/S','/D='+str(tess)],timeout=240)
  if result.returncode or not (tess/'tesseract.exe').exists():raise RuntimeError('Tesseract extraction failed')
 office=OUT/'office'
 if not (office/'program'/'soffice.exe').exists():
  extract=ROOT/'build'/'office-extract';extract.mkdir(parents=True,exist_ok=True)
  result=subprocess.run(['msiexec','/a',str(CACHE/'office.msi'),'/qn','TARGETDIR='+str(extract)],timeout=480)
  if result.returncode not in (0,3010):raise RuntimeError('LibreOffice administrative extraction failed: '+str(result.returncode))
  source=next(extract.rglob('soffice.exe')).parent.parent;shutil.copytree(source,office,dirs_exist_ok=True)
 for name,sha in MODELS.items():
  path=tess/'tessdata'/(name+'.traineddata');path.parent.mkdir(exist_ok=True)
  url=f'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/{COMMIT}/{name}.traineddata';download(url,sha,path);manifest.append({'file':name+'.traineddata','url':url,'sha256':sha})
 # Windows 10 supplies UCRT; redistribute installed Microsoft runtime DLLs app-locally.
 import os
 for folder in [office/'program',tess]:
  for name in ['vcruntime140.dll','vcruntime140_1.dll','msvcp140.dll','msvcp140_1.dll','msvcp140_2.dll','concrt140.dll']:
   source=Path(os.environ['SystemRoot'])/'System32'/name
   if source.exists() and not (folder/name).exists():shutil.copyfile(source,folder/name)
 (OUT/'runtime-manifest.json').write_text(json.dumps(manifest,indent=2));print('Verified runtimes ready')
if __name__=='__main__':main()
