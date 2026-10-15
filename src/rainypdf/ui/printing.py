from PySide6.QtPrintSupport import QPrintPreviewDialog,QPrinter
from PySide6.QtWidgets import QInputDialog
from PySide6.QtGui import QPainter,QImage
from PySide6.QtCore import QRectF
from rainypdf.engine.pdf import PdfEngine

def render_printer(snapshot,device,fit=True):
 painter=QPainter(device)
 if not painter.isActive():raise ValueError('Хэвлэгч нээгдсэнгүй.')
 try:
  with PdfEngine.document(snapshot) as d:
   first=device.fromPage() or 1;last=device.toPage() or len(d)
   for index in range(max(0,first-1),min(last,len(d))):
    if index>max(0,first-1):device.newPage()
    pix=d[index].get_pixmap(dpi=device.resolution(),alpha=False);image=QImage(pix.samples,pix.width,pix.height,pix.stride,QImage.Format.Format_RGB888).copy()
    viewport=painter.viewport();ratio=min(viewport.width()/image.width(),viewport.height()/image.height()) if fit else 1
    w=image.width()*ratio;h=image.height()*ratio;painter.drawImage(QRectF((viewport.width()-w)/2,(viewport.height()-h)/2,w,h),image)
 finally:painter.end()
def print_preview(snapshot,parent=None):
 mode,ok=QInputDialog.getItem(parent,'Хэвлэх хэмжээ','Горим',['Хуудаст багтаах','Бодит хэмжээ · 100%'],0,False)
 if not ok:return
 printer=QPrinter(QPrinter.PrinterMode.HighResolution);printer.setResolution(150)
 dialog=QPrintPreviewDialog(printer,parent);dialog.setWindowTitle('Хэвлэхийн өмнөх харагдац');dialog.resize(1000,750)
 dialog.paintRequested.connect(lambda device:render_printer(snapshot,device,mode.startswith('Хуудаст')));dialog.exec()
