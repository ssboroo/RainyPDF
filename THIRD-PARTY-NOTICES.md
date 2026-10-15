# Third-party software

RAINY PDF is distributed under GNU AGPL v3. Corresponding application source and build scripts: https://github.com/ssboroo/RainyPDF (use the tag matching the installer release).

- PyMuPDF / MuPDF: GNU AGPL v3, Artifex; https://github.com/pymupdf/PyMuPDF
- PySide6 / Qt: LGPLv3/GPL or commercial options. This distribution uses dynamically linked open-source Qt libraries. Replacement/relinking rights are not restricted by this application. https://www.qt.io/licensing/open-source-lgpl-obligations
- Tesseract and tessdata language models: Apache 2.0. Windows build by UB Mannheim, notices inside runtimes/tesseract. https://github.com/tesseract-ocr/tesseract and https://github.com/UB-Mannheim/tesseract
- LibreOffice: MPL 2.0 and included third-party licenses. Full notices and licenses are retained in runtimes/office. Source: https://www.libreoffice.org/download/download-libreoffice/ and https://www.libreoffice.org/licenses/
- pdf2docx: MIT (current version), with PyMuPDF dependency subject to its license. https://github.com/ArtifexSoftware/pdf2docx
- python-docx: MIT; openpyxl: MIT; Pillow: HPND; NumPy: BSD; OpenCV: Apache 2.0; associated notices are collected under licenses/.
- DejaVu Sans: Bitstream Vera and DejaVu terms; full font license accompanies the font in rainypdf/assets/FONT-LICENSE.txt.
- Python: PSF license. PyInstaller: GPL with bootloader exception.
- Windows runtime DLLs, if required: Microsoft runtime redistributables, governed by their own terms, not by this application's AGPL. Windows itself is not included.

Do not remove upstream license/source notices when redistributing. A commercial license is not required merely because users pay for an AGPL-compliant distribution; closed-source distribution would require a different licensing arrangement for applicable dependencies.
