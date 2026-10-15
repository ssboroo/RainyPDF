from pathlib import Path
import time
from rainypdf.jobs.manager import JobManager
from rainypdf.domain.types import JobRequest
from rainypdf.domain.session import DocumentSession
from rainypdf.ui.main_window import MainWindow

def test_background_export(qtbot,pdf,tmp_path):
 events=[];manager=JobManager(events.append)
 dest=tmp_path/'export.pdf';s=DocumentSession.open(pdf)
 manager.submit(JobRequest('one','pdf',s.snapshot(),{},dest))
 qtbot.waitUntil(lambda:any(e.state in ('done','error') for e in events),timeout=15000)
 assert events[-1].state=='done';assert dest.exists();manager.close()

def test_editor_open_undo_and_dirty_guard(qtbot,pdf):
 win=MainWindow();qtbot.addWidget(win);win.open_document(pdf)
 assert win.session is not None;assert win.page_count==3
 win.rotate_page();assert win.session.dirty
 win.undo();assert not win.session.dirty
 assert win.canvas.pixmap() is not None
 win.session.mark_saved();win.close()

def test_terminal_callback_observes_released_job(qtbot,pdf,tmp_path):
 seen=[];manager=None
 def done(event):
  if event.state in ('done','error'):seen.append(not manager.jobs)
 manager=JobManager(done);manager.submit(JobRequest('terminal','pdf',DocumentSession.open(pdf).snapshot(),{},tmp_path/'out.pdf'))
 qtbot.waitUntil(lambda:bool(seen),timeout=15000);assert seen==[True];manager.close()

def test_old_result_cannot_attach_to_new_document(qtbot,pdf,tmp_path):
 from rainypdf.domain.types import JobEvent
 win=MainWindow();qtbot.addWidget(win);win.open_document(pdf);old=win.session
 win.job_contexts['old']=(old,old.generation)
 second=tmp_path/'second.pdf';second.write_bytes(pdf.read_bytes());win.open_document(second)
 seen=[];win.table_preview=lambda tables:seen.append(tables)
 win.job_event(JobEvent('old',0,'done',data={'tables':[{'cells':[['FROM A']]}]}));qtbot.wait(100)
 assert seen==[];win.close()

def test_empty_ocr_edit_stays_empty(qtbot):
 from PySide6.QtWidgets import QApplication,QComboBox,QTextEdit
 from PySide6.QtCore import QTimer
 from io import BytesIO
 from PIL import Image
 image=BytesIO();Image.new('RGB',(20,20),'white').save(image,'PNG')
 win=MainWindow();qtbot.addWidget(win);seen=[]
 def drive():
  dialog=QApplication.activeModalWidget()
  try:
   text=dialog.findChild(QTextEdit);combo=dialog.findChild(QComboBox);text.clear();combo.setCurrentIndex(1);combo.setCurrentIndex(0);seen.append(text.toPlainText())
  finally:dialog.reject()
 QTimer.singleShot(20,drive);win.ocr_text_preview([{'text':'FIRST','image':image.getvalue()},{'text':'SECOND','image':image.getvalue()}]);assert seen==[''];win.close()
