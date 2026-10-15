# RAINY PDF 0.1 — шалгалт ба хязгаар

## Баталгаажуулалт

2026-10-15, Python 3.12, Linux: `python -m pytest -q` — 28 passed, 1 skipped. LibreOffice байхгүй учир Office round-trip тестийг энэ орчинд алгассан. Windows CI нь тусдаа багцалсан LibreOffice, Tesseract хөдөлгүүртэй шалгана. Эцсийн Windows суулгацын төлөвийг release-ийн QA тайлан болон Actions үр дүнгээр баталгаажуулна.

Тестүүд PDF текст, Unicode, overflow, эх файлын хамгаалалт, undo/redo, page operations, image conversion, true redaction (текст ба огтлолцсон vector), ink, координат, Excel literal data, OCR, background job, cancellation cleanup, Office process timeout болон Qt session identity-г хамарна. Энэ нь бүх төрлийн бодит баримтын төгс хөрвүүлэлтийн баталгаа биш.

## Хэрэгжүүлэлтийн шийдвэрүүд

- Хөгжүүлэлтийг шинэ repository-ийн тусдаа feature branch дээр хийсэн; анхны main зөвхөн баримтжуулалттай байсан.
- Session snapshot нь тайлагдсан PDF-ийн өөрчлөгдөхгүй bytes хадгална. Эх файлыг гаднаас солиход background job-ийн агуулга өөрчлөгдөхгүй; том файл санах ой илүү хэрэглэнэ.
- Ойролцоо PDF үйлдлүүд нэг replay engine ашиглана. Тоон гарын үсэгтэй PDF-г одоогоор нээхээс татгалзана.
- Worker үр дүнг atomic file mailbox-оор дамжуулна. Тасалсан worker Qt-г хагас дамжсан pipe frame дээр гацуулахгүй; review payload 96 MiB хүртэл, түр диск ашиглана.
- Нууцлах хүрээнд хүрсэн vector path-ийг бүхэлд нь арилгана. Хүрээнээс гаднах нэг объектын хэсэг хамт арилж болохыг интерфэйст анхааруулна.
- PDF/Office-ийн төвөгтэй layout, scan OCR болон хүснэгт танилтыг upstream хөдөлгүүрийн хязгаартайгаар ашиглаж, preview ба гараар засварлах боломж өгнө.

## Шалгаж дуусаагүй зүйлс

Бодит хэвлэгчийн hardware, Windows display scaling-ийн бүх тохиргоо, бүх хэлбэрийн гэмтсэн/хортой Office файл, бүх font/layout хослолыг туршаагүй. Macro ба link update-ийг хаах LibreOffice profile тохируулсан боловч үүнийг тусгаарлагдсан security sandbox гэж үзэхгүй. OCR-д албан ёсны CER/WER үнэлгээ хийгээгүй.

Суулгац digital code-signing сертификатгүй. Зурган гарын үсэг нь тоон гарын үсэг биш. Текст солих нь энгийн сонгож болох хэсэгт ажиллана; Acrobat-ийн бүх боломжийг амлахгүй.
