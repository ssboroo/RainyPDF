from PySide6.QtWidgets import QDialog,QFormLayout,QLineEdit,QComboBox,QCheckBox,QSpinBox,QDoubleSpinBox,QDialogButtonBox,QMessageBox,QLabel,QListWidget,QListWidgetItem
from PySide6.QtCore import Qt
from rainypdf.conversion.page_options import parse_pages

class PageOptionsDialog(QDialog):
 def __init__(self,count,parent=None,ocr=False,raster=False):
  super().__init__(parent);self.count=count;self.setWindowTitle('Хуудас ба боловсруулалтын тохиргоо');self.layout=QFormLayout(self);self.pages=QLineEdit();self.pages.setPlaceholderText(f'Бүгд (1–{count}) эсвэл 1,3-5');self.layout.addRow('Хуудас',self.pages);self.layout.addRow(QLabel('Сонгосон хуудсуудыг шинэ файлд гаргана.'))
  self.ocr=ocr;self.raster=raster
  if ocr:
   self.language=QComboBox();self.language.addItem('Монгол + Англи','mon+eng');self.language.addItem('Монгол','mon');self.language.addItem('Англи','eng');self.layout.addRow('OCR хэл',self.language)
   self.rotation=QComboBox();self.rotation.addItems(['0','90','180','270']);self.layout.addRow('Эргүүлэх · градус',self.rotation)
   self.gray=QCheckBox('Саарал болгох');self.deskew=QCheckBox('Бага хазайлтыг тэгшлэх');self.layout.addRow(self.gray);self.layout.addRow(self.deskew)
   self.mode=QComboBox();self.mode.addItem('Тексттэй хуудсыг хэвээр хадгалах','skip_text');self.mode.addItem('Бүх хуудсыг дахин таних','all');self.layout.addRow('PDF текстийн давхарга',self.mode)
  if raster:
   self.dpi=QSpinBox();self.dpi.setRange(36,600);self.dpi.setValue(150);self.layout.addRow('DPI',self.dpi);self.format=QComboBox();self.format.addItems(['png','jpg']);self.layout.addRow('Зургийн формат',self.format)
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);self.layout.addRow(buttons)
 def accept(self):
  try:parse_pages(self.pages.text(),self.count)
  except ValueError as e:QMessageBox.warning(self,'Хуудас сонголт',str(e));return
  super().accept()
 def values(self):
  result={'pages':parse_pages(self.pages.text(),self.count)}
  if self.ocr:result.update(language=self.language.currentData(),rotation=int(self.rotation.currentText()),grayscale=self.gray.isChecked(),deskew=self.deskew.isChecked(),page_mode=self.mode.currentData())
  if self.raster:result.update(dpi=self.dpi.value(),format=self.format.currentText())
  return result

class LayoutOptionsDialog(QDialog):
 def __init__(self,parent=None,kind='photo'):
  super().__init__(parent);self.setWindowTitle('A4 өрөлтийн тохиргоо');form=QFormLayout(self);self.kind=kind
  def number(value):
   n=QDoubleSpinBox();n.setRange(1,297);n.setDecimals(1);n.setValue(value);return n
  self.width=number(85.6 if kind=='id' else 35);self.height=number(54 if kind=='id' else 45);form.addRow('Өргөн · мм',self.width);form.addRow('Өндөр · мм',self.height)
  self.rows=QSpinBox();self.rows.setRange(1,20);self.rows.setValue(3);self.cols=QSpinBox();self.cols.setRange(1,20);self.cols.setValue(4)
  self.margin=number(10);self.gap=number(4);self.crop=QComboBox();self.crop.addItem('Зургийг бүтнээр багтаах','fit');self.crop.addItem('Хүрээг дүүргэж тайрах','fill')
  if kind=='photo':form.addRow('Мөр',self.rows);form.addRow('Багана',self.cols);form.addRow('Зах · мм',self.margin);form.addRow('Завсар · мм',self.gap);form.addRow('Зургийн горим',self.crop)
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);form.addRow(buttons)
 def values(self):return {'size':(self.width.value(),self.height.value()),'rows':self.rows.value(),'cols':self.cols.value(),'margin_mm':self.margin.value(),'gap_mm':self.gap.value(),'crop':self.crop.currentData()}

class ImagePdfOptionsDialog(QDialog):
 def __init__(self,parent=None):
  super().__init__(parent);self.setWindowTitle('Зураг → PDF');form=QFormLayout(self);self.size=QComboBox();self.size.addItem('A4',True);self.size.addItem('Зургийн пиксел · 96 DPI',False);form.addRow('Хуудас',self.size)
  self.landscape=QCheckBox('Хэвтээ A4');form.addRow(self.landscape);self.margin=QDoubleSpinBox();self.margin.setRange(0,50);self.margin.setValue(10);form.addRow('Зах · мм',self.margin);self.fill=QCheckBox('Хүрээг дүүргэж тайрах');form.addRow(self.fill)
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);form.addRow(buttons)
 def values(self):return {'a4':self.size.currentData(),'landscape':self.landscape.isChecked(),'margin':self.margin.value(),'fill':self.fill.isChecked()}

class ExcelPrintOptionsDialog(QDialog):
 def __init__(self,names,parent=None):
  super().__init__(parent);self.setWindowTitle('Excel → PDF · Хэвлэх тохиргоо');form=QFormLayout(self);self.sheets=QListWidget()
  for name in names:
   item=QListWidgetItem(name);item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable);item.setCheckState(Qt.CheckState.Checked);self.sheets.addItem(item)
  form.addRow('Гаргах sheet',self.sheets);self.area=QLineEdit();self.area.setPlaceholderText('Хоосон = эх print area; жишээ A1:H35');form.addRow('Хэвлэх хүрээ',self.area)
  self.landscape=QCheckBox('Хэвтээ');self.fit=QCheckBox('Өргөнийг нэг хуудсанд багтаах');self.fit.setChecked(True);form.addRow(self.landscape);form.addRow(self.fit)
  self.preview=QCheckBox('Хөрвүүлсэн PDF-ийг нээж шалгах');self.preview.setChecked(True);form.addRow(self.preview)
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);form.addRow(buttons)
 def values(self):return {'sheets':[self.sheets.item(i).text() for i in range(self.sheets.count()) if self.sheets.item(i).checkState()==Qt.CheckState.Checked],'print_area':self.area.text().strip(),'landscape':self.landscape.isChecked(),'fit_width':self.fit.isChecked(),'preview':self.preview.isChecked()}
