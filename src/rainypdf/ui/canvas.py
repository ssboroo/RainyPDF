from PySide6.QtWidgets import QLabel,QRubberBand
from PySide6.QtCore import Qt,QRect,QPoint,Signal
from PySide6.QtGui import QPainter,QPen
class Canvas(QLabel):
 selection=Signal(object,object)
 def __init__(self):
  super().__init__();self.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop);self.setStyleSheet('background:white;');self.origin=None;self.points=[];self.band=QRubberBand(QRubberBand.Shape.Rectangle,self);self.setCursor(Qt.CursorShape.CrossCursor)
 def mousePressEvent(self,e):
  if e.button()==Qt.MouseButton.LeftButton:self.origin=e.position().toPoint();self.points=[self.origin];self.band.setGeometry(QRect(self.origin,self.origin));self.band.show()
 def mouseMoveEvent(self,e):
  if self.origin is not None:self.points.append(e.position().toPoint());self.band.setGeometry(QRect(self.origin,e.position().toPoint()).normalized())
 def mouseReleaseEvent(self,e):
  if self.origin is None:return
  r=QRect(self.origin,e.position().toPoint()).normalized();self.band.hide();self.origin=None
  if r.width()>3 and r.height()>3:self.selection.emit(r,self.points)
