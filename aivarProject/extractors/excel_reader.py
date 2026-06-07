"""
excel_reader.py
Extracts text content from Excel (.xlsx) files using pandas.
"""

import pandas as pd
import streamlit as st
from typing import Optional


def extract_from_excel(file) -> Optional[str]:
    """
    Extract text from all sheets of an Excel file.

    Args:
        file: A file-like object (.xlsx).

    Returns:
        Combined text content from all sheets, or None on failure.
    """
    try:
        xl = pd.ExcelFile(file, engine="openpyxl")
        sheet_texts = []

        for sheet_name in xl.sheet_names:
            try:
                df = xl.parse(sheet_name)

                if df.empty:
                    continue

                # Fill NaN with empty string and stringify everything
                df = df.fillna("").astype(str)

                # Convert the dataframe to readable text
                sheet_text = f"[Sheet: {sheet_name}]\n"
                sheet_text += df.to_string(index=False)
                sheet_texts.append(sheet_text)

            except Exception as sheet_err:
                st.warning(f"⚠️ Could not read sheet '{sheet_name}': {sheet_err}")

        if not sheet_texts:
            st.warning("⚠️ No readable data found in the Excel file.")
            return None

        return "\n\n".join(sheet_texts)

    except Exception as e:
        st.error(f"❌ Failed to read Excel file: {e}")
        return None
