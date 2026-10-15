import sys,multiprocessing,os,json
from pathlib import Path

def main():
 multiprocessing.freeze_support()
 if '--self-test' in sys.argv:
  from rainypdf.qa import run
  return run(sys.argv[sys.argv.index('--self-test')+1])
 if '--health-report' in sys.argv:
  from rainypdf.conversion.runtime import tool,RUNTIMES
  import subprocess
  result={}
  for name in ['tesseract','office']:
   try:result[name]=Path(tool(name)).is_file()
   except Exception:result[name]=False
  result['ready']=all(result.values());Path(sys.argv[sys.argv.index('--health-report')+1]).write_text(json.dumps(result));return 0 if result['ready'] else 1
 from PySide6.QtWidgets import QApplication
 from PySide6.QtGui import QFont,QIcon
 from rainypdf.ui.main_window import MainWindow
 app=QApplication(sys.argv);app.setApplicationName('RAINY PDF');app.setOrganizationName('RAINY');app.setFont(QFont('Segoe UI',10))
 window=MainWindow();icon=Path(__file__).resolve().parents[1]/'assets'/'rainypdf.ico'
 if icon.exists():app.setWindowIcon(QIcon(str(icon)))
 if len(sys.argv)>1 and Path(sys.argv[1]).suffix.lower()=='.pdf':window.guard(lambda:window.open_document(Path(sys.argv[1])))
 window.show()
 if '--screenshot' in sys.argv:
  from PySide6.QtCore import QTimer
  def capture():window.grab().save(sys.argv[sys.argv.index('--screenshot')+1]);window.session=None;window.close();app.quit()
  QTimer.singleShot(1400,capture)
 return app.exec()
