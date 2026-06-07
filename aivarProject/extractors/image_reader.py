"""
image_reader.py
Extracts text from image files using pytesseract OCR.
"""

import pytesseract
from PIL import Image
import streamlit as st
from typing import Optional


def extract_from_image(file) -> Optional[str]:
    """
    Extract text from an image file using OCR.

    Args:
        file: A file-like object (PNG, JPG, JPEG).

    Returns:
        Extracted text as a string, or None on failure.
    """
    try:
        image = Image.open(file)

        # Convert to RGB if needed (e.g., RGBA or grayscale)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        text = pytesseract.image_to_string(image, lang="eng")

        if not text.strip():
            st.warning("⚠️ OCR found no readable text in the image.")
            return None

        return text.strip()

    except pytesseract.TesseractNotFoundError:
        st.error(
            "❌ Tesseract OCR engine not found. "
            "Please install it: https://github.com/tesseract-ocr/tesseract"
        )
        return None
    except Exception as e:
        st.error(f"❌ OCR failed: {e}")
        return None
