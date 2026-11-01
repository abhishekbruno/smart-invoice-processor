import hashlib
import os
import re
from pathlib import Path
from typing import Tuple, Union
from config.settings import settings


class ValidationError(Exception):
    """Custom exception raised for file validation errors."""
    pass


def calculate_file_hash(source: Union[str, Path, bytes]) -> str:
    """Computes SHA-256 hash of a file or byte stream."""
    sha256 = hashlib.sha256()
    if isinstance(source, bytes):
        sha256.update(source)
    else:
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(f"File not found for hash calculation: {path}")
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
    return sha256.hexdigest()


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to prevent path traversal and remove illegal characters.
    Keeps only alphanumeric characters, dashes, underscores, and dots.
    """
    # Extract only the basename (strips any path traversal like ../)
    clean_name = os.path.basename(filename)
    # Remove leading dots to prevent hidden files
    clean_name = clean_name.lstrip(".")
    # Replace any suspicious characters with an underscore
    clean_name = re.sub(r"[^\w\s\.-]", "_", clean_name)
    # Collapse consecutive spaces or underscores
    clean_name = re.sub(r"[\s_]+", "_", clean_name).strip("_")

    if not clean_name:
        clean_name = "unnamed_document.pdf"
    if not clean_name.lower().endswith(".pdf"):
        clean_name += ".pdf"
    return clean_name


def validate_pdf_file(
    source: Union[str, Path, bytes], original_name: str = ""
) -> Tuple[bool, str]:
    """
    Validates a PDF file:
    1. Checks if file exists or bytes are non-empty.
    2. Validates maximum file size limit.
    3. Checks extension (.pdf).
    4. Validates PDF magic header (%PDF-).
    Returns (is_valid, error_message).
    """
    if isinstance(source, bytes):
        data = source
        size = len(data)
        display_name = original_name or "uploaded_file.pdf"
    else:
        path = Path(source)
        display_name = original_name or path.name
        if not path.exists():
            return False, f"File does not exist: {path}"
        size = path.stat().st_size
        try:
            with open(path, "rb") as f:
                data = f.read(1024)
        except Exception as e:
            return False, f"Cannot read file '{display_name}': {e}"

    if size == 0:
        return False, f"File '{display_name}' is empty (0 bytes)."

    if size > settings.MAX_FILE_SIZE_BYTES:
        max_mb = settings.MAX_FILE_SIZE_MB
        actual_mb = size / (1024 * 1024)
        return False, f"File '{display_name}' exceeds maximum size of {max_mb} MB (actual: {actual_mb:.2f} MB)."

    if not display_name.lower().endswith(".pdf"):
        return False, f"File '{display_name}' does not have a .pdf extension."

    # Validate PDF magic header (%PDF-)
    # A standard PDF must start with %PDF- (within first 1024 bytes)
    if b"%PDF-" not in data[:1024]:
        return False, f"File '{display_name}' is not a valid PDF (missing %PDF- header)."

    return True, ""

