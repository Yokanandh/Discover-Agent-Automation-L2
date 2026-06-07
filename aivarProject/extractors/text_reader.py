"""
text_reader.py
Extracts text from plain .txt files.
"""

import streamlit as st
from typing import Optional


def extract_from_text(file) -> Optional[str]:
    """
    Extract text from a plain text file.

    Args:
        file: A file-like object (.txt).

    Returns:
        The text content as a string, or None on failure.
    """
    try:
        # Try UTF-8 first, fallback to latin-1
        raw = file.read()

        if not raw:
            st.warning("⚠️ The uploaded text file is empty.")
            return None

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")

        return text.strip()

    except Exception as e:
        st.error(f"❌ Failed to read text file: {e}")
        return None
