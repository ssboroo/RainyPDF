from pathlib import Path
import importlib.metadata as metadata,shutil,json,sys
output=Path(sys.argv[1]);output.mkdir(parents=True,exist_ok=True);manifest=[]
for dist in metadata.distributions():
 name=dist.metadata.get('Name','unknown');version=dist.version;manifest.append({'name':name,'version':version,'license':dist.metadata.get('License-Expression') or dist.metadata.get('License',''),'source':dist.metadata.get('Home-page','')})
 for item in dist.files or []:
  path=Path(str(item));lower=path.name.lower()
  if not ('license' in str(path).lower() or lower.startswith(('copying','notice'))):continue
  source=Path(dist.locate_file(item))
  if not source.is_file() or source.stat().st_size>1024*1024:continue
  target=output/name/(str(path).replace('../','').replace('..\\',''));target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
(output/'components.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
