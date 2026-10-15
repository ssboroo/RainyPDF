# RAINY PDF — Баримтын туслах

Монгол интерфэйстэй, Windows 10/11 x64 дээр интернэтгүй ажиллах PDF засварлагч.

**Төлөв:** эхний хувилбарын хөгжүүлэлт ба Windows багцын баталгаажуулалт. Бэлэн суулгац нь [Releases](https://github.com/ssboroo/RainyPDF/releases)-д Windows шалгалт амжилттай дууссаны дараа гарна.

## Боломжууд
- PDF нээх, хуудас урьдчилан харах, zoom, текст хайх/хуулах.
- Монгол текст нэмэх, сонгосон энгийн текст солих, зураг/зурган гарын үсэг оруулах.
- Highlight, underline, strikeout, note, хүрээ, чөлөөт зурлага; өөрийн нэмсэн объект зөөх/устгах.
- Undo/Redo, хуудас эргүүлэх/устгах/хуулбарлах/дараалал солих.
- PDF нэгтгэх/салгах, lossless шахалт, зураг ↔ PDF.
- Жинхэнэ redaction: сонгосон мэдээллийг арилгаж шинэ файл гаргах.
- Монгол/Англи OCR: searchable PDF, таньсан текстийг эх зурагтай харьцуулж засах, TXT/Word экспорт.
- PDF → Word; PDF хүснэгт → Excel, засаж шалгах preview; энгийн хүрээтэй скан хүснэгтийн OCR.
- Word/Excel → PDF, bundled LibreOffice runtime.
- Print preview / Windows хэвлэгч; үнэмлэх/цээж зураг A4 layout.

## Хэрэглэх
[Монгол гарын авлага](docs/USER-GUIDE-MN.md). Програмын `Тусламж` цэснээс товч заавар үзнэ.
Баримт сервер рүү илгээгдэхгүй. Эх файлаа дарж бичихгүй; шинэ хуулбар хадгална.

## Бодит хязгаар
Acrobat-ийн бүх боломжийг дуурайсан бүтээгдэхүүн гэж үзэхгүй. Текст солих нь энгийн сонгож болох хэсэгт; догол мөрийг бүхэлд нь автоматаар reflow хийхгүй. Scan-ийн пиксел дээрх үсгийг Word шиг засахгүй. OCR/Office хөрвүүлэлтийн чанар эх файл, фонт, байрлалаас хамаарна. Зурган гарын үсэг нь сертификаттай тоон гарын үсэг биш. Тоон гарын үсэгтэй PDF-г одоогоор хамгаалж нээхээс татгалзана.

Хүснэгтийн эхний танилт нь энгийн бүтэцтэй хүснэгтэд чиглэсэн. Муу скан, merged-cell ихтэй хүснэгтийг гараар хянах шаардлагатай. Шахалт бүр файлыг жижигрүүлэхгүй.

## Хөгжүүлэлт
Python 3.12:
```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m pytest -q
python -m rainypdf
```
Source OCR/Office тестэд Tesseract mon/eng/osd болон LibreOffice шаардлагатай. End-user installer эдгээрийг хамтад нь агуулна.

Windows build: PowerShell 7, Inno Setup 6; `./build-tools/build_windows.ps1`.
CI нь dependency hash шалгах, test, packaged self-test, суулгах/устгах, GUI зураг, Print-to-PDF зэргийг шалгаад release гаргана. Бодит хэвлэгчийн hardware шалгалтыг Print-to-PDF-тэй адил гэж тооцохгүй.

## Лиценз
GNU AGPL v3. [Third-party notices](THIRD-PARTY-NOTICES.md). [Дизайн](docs/superpowers/specs/2026-10-15-rainy-pdf-design.md) · [Төлөвлөгөө](docs/superpowers/plans/2026-10-15-rainy-pdf.md).
