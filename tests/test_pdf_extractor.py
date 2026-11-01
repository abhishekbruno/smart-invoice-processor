import pytest
from pathlib import Path
from core.pdf_extractor import PDFExtractor, PDFExtractionError
from utils.validators import validate_pdf_file


def test_pdf_extractor_initialization():
    extractor = PDFExtractor()
    assert extractor is not None
    assert isinstance(extractor.is_ocr_supported, bool)


def test_extract_valid_sample_pdf():
    extractor = PDFExtractor()
    sample_file = Path("data/samples/AWS_INV_2024_8192.pdf")
    if not sample_file.exists():
        pytest.skip("Sample PDF not found, generate samples first.")

    doc = extractor.extract_from_file(sample_file)
    assert doc.page_count >= 1
    assert "Amazon Web" in doc.cleaned_text or "AWS" in doc.cleaned_text
    assert len(doc.pages) == doc.page_count
    assert not doc.is_scanned


def test_empty_pdf_raises_validation_error(tmp_path):
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")

    extractor = PDFExtractor()
    with pytest.raises(PDFExtractionError) as exc_info:
        extractor.extract_from_file(empty_file)
    assert "empty" in str(exc_info.value).lower()


def test_corrupt_pdf_handling(tmp_path):
    corrupt_file = tmp_path / "corrupt.pdf"
    corrupt_file.write_bytes(b"%PDF-1.4\nCorrupted binary junk data that is not a valid xref table")

    extractor = PDFExtractor()
    with pytest.raises(PDFExtractionError):
        extractor.extract_from_file(corrupt_file)


def test_invalid_extension_rejected(tmp_path):
    txt_file = tmp_path / "invoice.txt"
    txt_file.write_text("Invoice: 12345")

    extractor = PDFExtractor()
    with pytest.raises(PDFExtractionError):
        extractor.extract_from_file(txt_file)

