from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess,shutil
from rainypdf.conversion.runtime import tool,options
from rainypdf.engine.pdf import validate_pdf
from rainypdf.engine.output import atomic_export

def office_to_pdf(source,output):
 source=Path(source).resolve()
 if source.suffix.lower() not in ('.doc','.docx','.xls','.xlsx','.odt','.ods'):raise ValueError('Word эсвэл Excel файл сонгоно уу.')
 def write(dest):
  with TemporaryDirectory(prefix='rainypdf-office-') as folder:
   root=Path(folder);profile=root/'profile';(profile/'user').mkdir(parents=True)
   (profile/'user'/'registrymodifications.xcu').write_text('''<?xml version="1.0" encoding="UTF-8"?><oor:items xmlns:oor="http://openoffice.org/2001/registry"><item oor:path="/org.openoffice.Office.Common/Security/Scripting"><prop oor:name="MacroSecurityLevel" oor:op="fuse" oor:finalized="true"><value>3</value></prop></item><item oor:path="/org.openoffice.Office.Calc/Content/Update"><prop oor:name="Link" oor:op="fuse" oor:finalized="true"><value>1</value></prop></item><item oor:path="/org.openoffice.Office.Writer/Content/Update"><prop oor:name="Link" oor:op="fuse" oor:finalized="true"><value>2</value></prop></item></oor:items>''')
   result=subprocess.run([tool('office'),'-env:UserInstallation='+profile.as_uri(),'--headless','--nologo','--nodefault','--norestore','--convert-to','pdf','--outdir',str(root),str(source)],capture_output=True,timeout=180,**options())
   created=root/(source.stem+'.pdf')
   if result.returncode or not created.exists():raise ValueError('Office хөрвүүлэлт амжилтгүй. Файл нууц үгтэй эсвэл гэмтсэн байж болно.')
   shutil.copyfile(created,dest)
 return atomic_export(output,write,validate_pdf)
