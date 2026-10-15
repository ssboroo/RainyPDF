from pathlib import Path
import subprocess,sys,json,struct
exe=Path(sys.argv[1]).resolve();root=Path(__file__).resolve().parents[1];out=root/'dist';out.mkdir(exist_ok=True)
p=subprocess.run([str(exe),'--self-test',str(out)],timeout=300)
if p.returncode:raise SystemExit('Packaged self-test failed')
report=json.loads((out/'qa-report.json').read_text())
if not report['ready']:raise SystemExit(report)
print(json.dumps(report,ensure_ascii=True))
# Windows shell must be able to extract the executable icon.
import ctypes
large=ctypes.c_void_p();small=ctypes.c_void_p()
count=ctypes.windll.shell32.ExtractIconExW(str(exe),0,ctypes.byref(large),ctypes.byref(small),1)
if count<1:raise RuntimeError('Executable has no shell icon')
for handle in [large,small]:
 if handle.value:ctypes.windll.user32.DestroyIcon(handle)
