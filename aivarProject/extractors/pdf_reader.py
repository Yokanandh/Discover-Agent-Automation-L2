"""
pdf_reader.py
Extracts text from PDF files using pdfplumber.
"""

import pdfplumber
import streamlit as st
from typing import Optional


def extract_from_pdf(file) -> Optional[str]:
    """
    Extract text from a PDF file object.

    Args:
        file: A file-like object (e.g., from Streamlit uploader).

    Returns:
        Extracted text as a string, or None on failure.
    """
    try:
        text_parts = []
        with pdfplumber.open(file) as pdf:
            if len(pdf.pages) == 0:
                st.warning("⚠️ The uploaded PDF has no pages.")
                return None

            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"[Page {page_num}]\n{page_text}")
                except Exception as page_err:
                    st.warning(f"⚠️ Could not read page {page_num}: {page_err}")

        if not text_parts:
            st.warning("⚠️ No readable text found in the PDF.")
            return None

        return "\n\n".join(text_parts)

    except Exception as e:
        st.error(f"❌ Failed to read PDF: {e}")
        return None
