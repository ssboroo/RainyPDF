# RAINY PDF — Баримтын туслах

Огноо: 2026-10-15
Төлөв: Хэрэглэгчээр хянуулах шаардлагын загвар. Програм, installer хараахан бэлэн биш.
Repository: https://github.com/ssboroo/RainyPDF

## Зорилго
Монгол хэрэглэгч баримтаа Windows 10/11 x64 компьютертээ нээх, засах, цэгцлэх, хэвлэхэд бэлтгэх. Монгол интерфэйс, цайвар цэнхэр R брэнд, локал боловсруулалт. Хэрэглэгч Python болон хөгжүүлэлтийн хэрэгсэл суулгахгүй.
Acrobat-тай ижил ангиллын бүтээгдэхүүн хөгжүүлэх зорилготой. Эхний хувилбар нь Acrobat-ийн бүх боломжтой дүйцсэн гэж сурталчлахгүй.

## Хувилбар ба сонгосон шийдэл
1. Санал болгож буй хувилбар: PySide6 desktop + PyMuPDF PDF engine + Pillow. Локал засвар, rendering, annotation болон Windows хэвлэл нэг урсгалтай. PDF engine нь лицензийн нөхцөлтэй.
2. PDFium + pikepdf: нээлттэй бүрэлдэхүүнтэй өөр сонголт; одоо байгаа текст засах ажиллагааг илүү ихээр өөрсдөө хэрэгжүүлнэ.
3. Commercial PDF SDK: өргөн засварлах боломжтой байж болох боловч лицензийн төсөв, түгээлтийн нөхцөлийг тусад нь батална.
Энэ загвар эхний сонголтыг санал болгож байна. PyMuPDF ашигласан нээлттэй түгээлтийг AGPLv3 нөхцөлтэй төлөвлөнө; хаалттай эх кодтой түгээлт хүсвэл commercial engine/license сонголтыг хэрэгжүүлэхээс өмнө шийднэ. Энэ баримт өөрөө репод лиценз олгосон хэрэг биш.

## Эхний хувилбарын заавал ажиллах боломжууд
### PDF унших
- PDF нээх, олон хуудасны thumbnail, zoom, fit width/page, хуудас руу үсрэх, хайлт, текст сонгох/хуулах.
- Том файлыг хуудас тус бүрээр render хийх; UI thread дээр урт ажил гүйцэтгэхгүй.
- Нууц үгтэй файлыг хэрэглэгчийн оруулсан зөв нууц үгээр нээх. Нууц үгийг диск/log/history-д хадгалахгүй.

### Текст ба объект засах
- Шинэ Монгол/Англи текст нэмэх; фонт, хэмжээ, өнгө, байрлал тохируулах.
- Сонгож болох энгийн текстийн хэсгийг хүрээгээр сонгож солих. Өөрчлөх хүрээ, үсгийн хэлбэр, багтах эсэхийг урьдчилан харуулна. Анхны текстийг жинхэнэ арилгаж орлуулна; цагаан дөрвөлжин тавиад мэдээлэл нуусан гэж үзэхгүй.
- Давхцалтай объект, урт догол мөрийн урсгал, эвдэрхий font mapping, outline болгон хувиргасан текстийг автоматаар төгс засах амлалтгүй. Боломжгүй хэсэгт шалтгааныг тайлбарлаж үйлдлийг хориглоно.
- Scan/зураг PDF дээр эхний хувилбарт текст давхарлаж нэмж болно; доторх хэвлэмэл үгийг шууд текст мэт засахгүй. Доорх OCR урсгалаар текст таньж хайдаг PDF, TXT/DOCX гаргана; scan зураг өөрөө Word мэт засагдахгүй.
- PNG/JPG зураг болон зурган гарын үсэг оруулах, байрлуулах, хэмжээг өөрчлөх. Эдгээр нь криптограф тоон гарын үсэг биш.
- Өөрсдийн нэмсэн объектуудыг сонгох, зөөх, устгах.
- Undo/Redo: баримтын үйлдлийн bounded snapshot/command history; өөрчлөгдсөн төлөв тод харагдана.

### Тэмдэглэгээ ба хамгаалалт
- Highlight, underline, strikeout, note, rectangle, чөлөөт зурлага.
- Нууцлах хүрээ тэмдэглэх → урьдчилан шалгах → жинхэнэ redaction хийх → шинэ файлд хадгалах. Export хийсэн файлд нууцалсан текст хайлтаар илрэхгүйг шалгана. Нууцлах хүрээнд зураг/давхцсан текст байвал үр дагаврыг урьдчилан харуулна.
- Тоон гарын үсэгтэй PDF-г өөрчлөхөд баталгаажуулалт хүчингүй болж болохыг засварын өмнө тод мэдэгдэнэ; сертификаттай гарын үсэг үүсгэх боломж эхний хувилбарт орохгүй.

### Хуудас ба хөрвүүлэлт
- PDF нэгтгэх, сонгосон хуудас салгах, эргүүлэх, устгах, хуулбарлах, дараалал солих.
- JPG/PNG → PDF: A4/original size, босоо/хэвтээ, margin, fit/fill.
- PDF → PNG/JPG: сонгосон хуудас, DPI.
- Шахалт: эхлээд lossless stream/structure optimization. Хэмнэлтгүй бол тод хэлнэ; файлыг заавал багасгана гэж амлахгүй. Сонгомол lossy image compression дараагийн үе шатанд.

### OCR — эхний хувилбарт
- Tesseract 5, mon+eng болон osd language data-г Windows багцад хамтад нь оруулна. Хэрэглэгч OCR-ийг тусдаа суулгахгүй. Үндсэн урсгал интернэтгүй ажиллана.
- Зураг болон скан PDF-ийн сонгосон хуудсыг 300 DPI орчим raster болгож, эргүүлэх/deskew болон grayscale тохируулгаар танина. Эх зураг хэвээр, searchable text layer бүхий PDF эсвэл TXT гаргана.
- OCR текст ба хуудсыг зэрэг урьдчилан харуулж, буруу таньсан үгийг export хийхээс өмнө засах боломжтой. Энэ засвар эх зургийн пикселийг өөрчлөхгүй.
- Хэвлэмэл Монгол кирилл/Англи текстийг зорилтот хэрэглээ болгоно; гар бичмэл, тамга, муу зураг, босоо Монгол бичгийн нарийвчлалыг батлахгүй. Тодорхойгүй танилтыг хэрэглэгчид мэдэгдэнэ.
- Хуудсаар progress/cancel, temporary file cleanup, давхар text layer үүсгэхээс хамгаалах page mode сонголттой.

### PDF ↔ Word — эхний хувилбарт
- PDF → DOCX: pdf2docx адаптераар сонгосон хуудасны текст, зураг, энгийн хүснэгт, байршлыг боломжийн хэмжээнд сэргээнэ. Шинээр нэмсэн текст/зураг бүхий session-ийн өөрчлөлтийг conversion snapshot-д багтаана.
- Scan PDF-д OCR үр дүнг DOCX текст болгон гаргах тусдаа mode байна; visual-layout mode-той андуурахгүй. Хоосон DOCX-ийг амжилттай гэж үзэхгүй.
- DOC/DOCX → PDF: багцалсан LibreOffice runtime ашиглаж, тусгаарласан temporary profile болон output folder-т ажиллуулна. Office эсвэл LibreOffice-ийг хэрэглэгчээр тусад нь суулгахгүй; installer хэмжээ өсөхийг хүлээн зөвшөөрнө.
- Фонт орлуулалт болон олон багана, томъёо, төвөгтэй хүснэгтээс үүдэх layout өөрчлөлтийг preview ба тайлбарт харуулна. Pixel-perfect round trip амлахгүй.

### PDF ↔ Excel — эхний хувилбарт
- PDF → XLSX: PDF engine-ийн table detection/coordinate extraction + openpyxl; хүснэгт тус бүрийг нэртэй sheet-д гаргаж, page provenance тэмдэглэнэ. Бүх хуудсыг нэг зураг хэлбэрээр Excel-д тавьсныг хүснэгт хөрвүүлэлт гэж үзэхгүй.
- Хүснэгтийн хүрээг хэрэглэгч сонгож, мөр/багана болон толгойг preview дээр хянана. Table олдоогүй үед хоосон Excel гаргахгүй.
- Scan хүснэгтэд OCR word boxes → мөр/багана тааруулах, хэрэглэгчийн хяналт шаардлагатай урсгал ашиглана. Энгийн хүрээтэй хүснэгт нь хүлээн авах үндсэн fixture; бүх төрлийн merged cell/complex layout-ийг автоматаар таних амлалтгүй.
- Регистр, утас, эхний тэгтэй дугаарыг анхдагчаар текст хэлбэрээр хадгална. Тоо болгох үйлдлийг preview дээр сонгоно. =,+,-,@ зэрэг эхлэлтэй эх текстийг formula болгон ажиллуулахгүй.
- XLS/XLSX → PDF: LibreOffice Calc export; sheet selection, page orientation/fit болон print range preview. Macro ажиллуулахгүй, external link refresh хийхгүй. Формулын cached/recalculated үр дүнгийн зөрүүг fixture-аар шалгана.
- Word/Excel файлыг sandbox-like тусдаа worker process, macro-disabled dedicated profile, bounded timeout-той боловсруулна; систем дээр байгаа LibreOffice process-ийг зогсоохгүй. Нууц үгтэй Office файлын дэмжлэг эхний хувилбарт орохгүй, тод алдаа өгнө.

### Хэвлэх
- Windows printer сонгох, хуудас/хуулбар/чиглэл, fit/actual size, preview.
- Үнэмлэхийн хоёр талын зураг нэг A4 дээр; хэмжээг мм-ээр тохируулж, хэвлэхээс өмнө шалгах.
- Цээж зураг: хэрэглэгчийн сонгосон мм хэмжээ, мөр/багана, margin, crop preview. Биометрийн шаардлага автоматаар баталгаажуулахгүй.

## Интерфэйс ба урсгал
Нүүр: сүүлийн файлуудын зөвхөн локал жагсаалт, файл чирж оруулах талбар, гол үйлдлийн картууд.
Editor: дээд toolbar (Нээх/Буцаах/Дахин хийх/Хадгалах), зүүн thumbnails, гол page canvas, баруун сонгосон хэрэгслийн properties. Текст/Зураг/Тэмдэглэгээ/Хуудас/OCR/Хөрвүүлэх/Хэвлэх табууд. Хөрвүүлэх хэсэгт PDF → Word, Word → PDF, PDF → Excel, Excel → PDF гэсэн тусдаа үйлдэл байна.
Хэрэглэгч файл нээнэ → хэрэгсэл сонгоно → хуудсан дээр өөрчилнө → preview → Save As. Товчнууд баримт болон сонголтын төлөвөөс хамаарч идэвхжинэ. Shortcut, tooltip, keyboard focus, DPI scaling дэмжинэ.

## Архитектур ба өгөгдөл
- domain/document: session, page identity/order, edit commands, dirty state.
- engine: render/extract/edit/annotation/redaction/export adapters; engine объектууд UI-д шууд тархахгүй.
- conversion: OCR, DOCX, XLSX, LibreOffice тусдаа adapter; language data/runtime-ийн version ба SHA256-г build manifest-д бичнэ. Conversion output-ийг PDF/ZIP container бүтэц болон non-empty content-аар шалгана.
- jobs: тусдаа process-д урт OCR/conversion/export/merge/compress; progress/cancel, session generation id-аар хуучирсан үр дүнг үл хэрэгсэх.
- ui: Qt widgets/canvas, thumbnail virtualization, toolbar/properties, Mongolian messages.
- storage: зөвхөн preferences ба recent paths; recent history-г арилгах боломжтой. Баримтын агуулга, нууц үг, хувийн зураг log-д орохгүй.
- packaging: PyInstaller onedir, Inno Setup per-user, R icon, versioned RainyPDF-<version>-Setup.exe. PDF default association-ийг зөвхөн хэрэглэгчийн сонголтоор өөрчилнө.

## Найдвартай хадгалалт ба алдаа
Эх файлыг анхдагчаар дарж бичихгүй. Export-ийг output folder дахь түр файлд бичиж, дахин нээж шалгасны дараа эцсийн нэр рүү атомикаар шилжүүлнэ. Алдаа/цуцлалт дээр эх файл болон өмнөх output-ийг гэмтээхгүй. Нэр давхцвал хэрэглэгчээр шийдүүлнэ.
Эвдэрхий PDF, буруу нууц үг, эрхгүй хавтас, дүүрсэн диск, font олдоогүй, текст хүрээнд багтаагүй зэрэгт Монгол тайлбар өгнө. Багтахгүй текстийг чимээгүй таслахгүй. Signed file-ийн өөрчлөлт, жинхэнэ redaction нь илт баталгаажуулах урсгалтай байна.

## Дараагийн үе шат
- AcroForm бөглөх/үүсгэх, document compare, batch processing.
- Догол мөрийн илүү өргөн reflow, төвөгтэй хүснэгт/layout сэргээх сайжруулалт.
- Сертификаттай тоон гарын үсэг ба баталгаажуулалт.
Эдгээрийг ажилладаг болохоос өмнө эхний хувилбарын боломж гэж жагсаахгүй.

## Хүлээн авах шалгалт
- Монгол кирилл (Ө, Ү зэрэг) текстийг нэмэх/солих, хадгалах, дахин нээхэд зөв текст болон дүрслэлтэй байх.
- Rotated/cropped page дээр cursor → PDF координат, зураг/annotation байрлал зөв байх.
- Text replacement нь сонгоогүй хэсгийг өөрчлөхгүй; хэт урт текст тод алдаатай байх.
- Redaction exported file-ээс нууцалсан үгийг text extraction/search-аар олохгүй; зурагтай хүрээний үр дүнг render-ээр шалгах.
- Merge/split/order/rotate-ийн page count/content; source bytes unchanged; save/cancel/disk error atomicity.
- Image conversion-ийн мм хэмжээ, DPI, aspect ratio ба print preview зөв байх.
- UI responsiveness, undo/redo, dirty-close prompt, stale job result, password handling.
- OCR: Монгол Ө/Ү, Англи ба холимог хэвлэмэл текстийн тогтмол fixture дээр extracted text, page count, text layer alignment-ийг шалгана. CER/WER-г тайланд бодитоор хэмжиж, чанарын хязгаарыг мэдээлнэ; 100% гэсэн зохиомол амжилтын хувь тавихгүй.
- Word: native PDF → editable DOCX, scan → OCR DOCX, DOCX → PDF; Монгол текст, зураг, хүснэгт, page count/layout-ийг render-ээр шалгана. Exact-layout боломжгүй fixture-ийн хүлээгдэж буй зөрүүг тод тэмдэглэнэ.
- Excel: native болон scan хүснэгтийн header/rows/cells, leading zero, formula injection хамгаалалт, XLSX → PDF sheet/print area; expected cell matrix-тай харьцуулна.
- Packaging: Tesseract mon/eng/osd, LibreOffice runtime/licenses/fonts бүгд offline clean Windows VM дээр ажиллах ёстой. Макро болон external link test fixtures нь гаднын нөлөө үзүүлэхгүйг батална.
- Windows packaged EXE launch, Mongolian path/font, embedded R icon extraction, installer install/uninstall, non-admin account, 100%/150% DPI.
- Installer, эх код, Монгол гарын авлага, dependency notices, бодит QA зураг/тайлан гаргана. Шалгаж амжаагүй зүйлсийг тайланд тусад нь тэмдэглэнэ.

## Лавлах анхдагч эх сурвалж
- https://pymupdf.readthedocs.io/en/latest/page.html
- https://github.com/pymupdf/PyMuPDF
- https://pymupdf.io/licensing
- https://github.com/pyside/pyside-setup

- https://tesseract-ocr.github.io/tessdoc/
- https://github.com/tesseract-ocr/tessdata_fast
- https://pdf2docx.readthedocs.io/en/latest/
- https://help.libreoffice.org/latest/en-US/text/shared/guide/pdf_params.html
