import os,tempfile
from pathlib import Path

def atomic_export(destination,writer,validator,overwrite=False):
 destination=Path(destination).resolve()
 if destination.exists() and not overwrite:raise FileExistsError('Ижил нэртэй файл байна. Өөр нэр сонгоно уу.')
 destination.parent.mkdir(parents=True,exist_ok=True)
 fd,name=tempfile.mkstemp(prefix='.rainypdf-'+(str(os.getpid())+'-' if os.environ.get('RAINYPDF_WORKER') else ''),suffix=destination.suffix,dir=destination.parent);os.close(fd);temp=Path(name)
 try:
  writer(temp);validator(temp)
  with temp.open('r+b') as f:os.fsync(f.fileno())
  if overwrite:os.replace(temp,destination)
  else:
   # Atomic no-clobber publication on the same filesystem.
   os.link(temp,destination);temp.unlink()
  return destination
 finally:temp.unlink(missing_ok=True)
