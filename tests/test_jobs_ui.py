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
