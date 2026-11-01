"""PDF text extraction using pypdf."""

from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PDFExtractionError(Exception):
    """Raised when a PDF cannot be read or contains no selectable text."""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Return the combined text of every page in the PDF.

    Raises PDFExtractionError for corrupt, encrypted, or image-only PDFs.
    """
    if not pdf_bytes:
        raise PDFExtractionError("The uploaded file is empty.")

    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except (PdfReadError, ValueError, OSError) as exc:
        raise PDFExtractionError(
            "The file could not be read as a PDF. It may be corrupt."
        ) from exc

    if reader.is_encrypted:
        try:
            # Many "encrypted" PDFs only have an owner password and open with an empty one.
            if not reader.decrypt(""):
                raise PDFExtractionError(
                    "The PDF is password-protected. Please upload an unlocked copy."
                )
        except PDFExtractionError:
            raise
        except Exception as exc:
            raise PDFExtractionError(
                "The PDF is encrypted and could not be opened."
            ) from exc

    pages = []
    try:
        for page in reader.pages:
            pages.append(page.extract_text() or "")
    except Exception as exc:
        raise PDFExtractionError(
            "An error occurred while extracting text from the PDF."
        ) from exc

    text = "\n".join(pages).strip()
    if not text:
        raise PDFExtractionError(
            "No selectable text was found in the PDF. It may be a scanned or "
            "image-only document; OCR is not supported in this version."
        )
    return text
