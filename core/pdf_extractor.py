import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from config.settings import settings
from utils.helpers import clean_extracted_text
from utils.logger import logger
from utils.validators import validate_pdf_file


class PDFExtractionError(Exception):
    """Raised when PDF extraction fails due to corruption, encryption, or format issues."""
    pass


@dataclass
class PageData:
    page_number: int  # 1-indexed
    text: str
    word_count: int
    is_ocr: bool = False


@dataclass
class ExtractedDocument:
    raw_text: str
    cleaned_text: str
    pages: List[PageData] = field(default_factory=list)
    page_count: int = 0
    is_scanned: bool = False
    used_ocr: bool = False
    ocr_available: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


class PDFExtractor:
    """Extracts text and metadata from PDF files using PyMuPDF with optional OCR fallback."""

    def __init__(self):
        self._tesseract_available = self._check_tesseract_availability()

    def _check_tesseract_availability(self) -> bool:
        """Checks if pytesseract and the tesseract executable are available."""
        try:
            import pytesseract

            # If user configured a specific path, set it
            if settings.TESSERACT_PATH and os.path.exists(settings.TESSERACT_PATH):
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

            # Check if tesseract binary can be found in PATH or configured location
            tess_cmd = getattr(pytesseract.pytesseract, "tesseract_cmd", "tesseract")
            found = shutil.which(tess_cmd) is not None or os.path.exists(tess_cmd)
            return bool(found)
        except Exception:
            return False

    @property
    def is_ocr_supported(self) -> bool:
        return self._tesseract_available

    def extract_from_file(self, file_path: Union[str, Path]) -> ExtractedDocument:
        """Extracts text, metadata, and pages from a PDF file path."""
        path = Path(file_path)
        is_valid, error_msg = validate_pdf_file(path)
        if not is_valid:
            raise PDFExtractionError(f"File validation failed: {error_msg}")

        try:
            with open(path, "rb") as f:
                pdf_bytes = f.read()
            return self.extract_from_bytes(pdf_bytes, file_name=path.name)
        except PDFExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error opening PDF {path.name}: {e}", exc_info=True)
            raise PDFExtractionError(f"Failed to read PDF file '{path.name}': {str(e)}")

    def extract_from_bytes(self, pdf_bytes: bytes, file_name: str = "document.pdf") -> ExtractedDocument:
        """Extracts text, metadata, and pages from PDF byte data."""
        is_valid, error_msg = validate_pdf_file(pdf_bytes, original_name=file_name)
        if not is_valid:
            raise PDFExtractionError(f"Validation failed: {error_msg}")

        try:
            import pymupdf as fitz  # PyMuPDF
        except ImportError:
            try:
                import fitz
            except ImportError:
                raise PDFExtractionError("PyMuPDF is not installed. Run 'pip install PyMuPDF'.")

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise PDFExtractionError(f"PyMuPDF failed to parse PDF: {str(e)}")

        try:
            if doc.is_encrypted:
                # Try with empty password
                unlocked = doc.authenticate("")
                if not unlocked:
                    raise PDFExtractionError("PDF is password protected and cannot be extracted.")

            page_count = len(doc)
            pages: List[PageData] = []
            all_text_pieces: List[str] = []
            warnings: List[str] = []
            used_ocr = False
            total_chars = 0

            # 1. Direct Text Extraction
            for i in range(page_count):
                page = doc[i]
                page_text = page.get_text("text") or ""
                cleaned_page_text = clean_extracted_text(page_text)
                word_count = len(cleaned_page_text.split()) if cleaned_page_text else 0
                total_chars += len(cleaned_page_text)

                pages.append(
                    PageData(
                        page_number=i + 1,
                        text=cleaned_page_text,
                        word_count=word_count,
                        is_ocr=False,
                    )
                )
                if cleaned_page_text:
                    all_text_pieces.append(cleaned_page_text)

            is_scanned = total_chars < (page_count * 30)  # less than ~30 chars per page indicates a scan/image

            # 2. Optional OCR Fallback if scanned
            if is_scanned:
                if settings.OCR_ENABLED and self._tesseract_available:
                    try:
                        import io
                        from PIL import Image
                        import pytesseract

                        ocr_text_pieces = []
                        pages = []

                        for i in range(page_count):
                            page = doc[i]
                            # Render page to an image
                            pix = page.get_pixmap(dpi=200)
                            img = Image.open(io.BytesIO(pix.tobytes("png")))
                            ocr_text = pytesseract.image_to_string(img)
                            cleaned_ocr = clean_extracted_text(ocr_text)

                            pages.append(
                                PageData(
                                    page_number=i + 1,
                                    text=cleaned_ocr,
                                    word_count=len(cleaned_ocr.split()) if cleaned_ocr else 0,
                                    is_ocr=True,
                                )
                            )
                            if cleaned_ocr:
                                ocr_text_pieces.append(cleaned_ocr)

                        all_text_pieces = ocr_text_pieces
                        used_ocr = True
                        logger.info(f"Applied OCR to scanned PDF: {file_name}")
                    except Exception as ocr_err:
                        logger.warning(f"OCR execution failed on {file_name}: {ocr_err}")
                        warnings.append(f"OCR attempt failed: {str(ocr_err)}")
                elif is_scanned:
                    warnings.append(
                        "Document appears to be a scanned image with minimal text. "
                        "OCR is currently disabled or Tesseract is not installed on the system."
                    )

            # Metadata extraction
            raw_metadata = doc.metadata or {}
            metadata = {
                "title": raw_metadata.get("title", ""),
                "author": raw_metadata.get("author", ""),
                "subject": raw_metadata.get("subject", ""),
                "creator": raw_metadata.get("creator", ""),
                "producer": raw_metadata.get("producer", ""),
                "creation_date": raw_metadata.get("creationDate", ""),
            }

            combined_raw = "\n\n".join([p.text for p in pages])
            combined_cleaned = clean_extracted_text(combined_raw)

            return ExtractedDocument(
                raw_text=combined_raw,
                cleaned_text=combined_cleaned,
                pages=pages,
                page_count=page_count,
                is_scanned=is_scanned,
                used_ocr=used_ocr,
                ocr_available=self._tesseract_available,
                metadata=metadata,
                warnings=warnings,
            )

        finally:
            doc.close()


# Global extractor singleton
pdf_extractor = PDFExtractor()
