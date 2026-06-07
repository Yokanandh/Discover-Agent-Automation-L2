"""
helper.py
Utility functions for data transformation and KPI computation.
"""

import json
import io
from typing import List, Dict, Any, Optional

import pandas as pd


def merge_texts(text_chunks: List[Optional[str]]) -> str:
    """
    Merge a list of extracted text strings into one context block.

    Args:
        text_chunks: List of text strings (may contain None values).

    Returns:
        Combined text string.
    """
    valid = [chunk for chunk in text_chunks if chunk and chunk.strip()]
    return "\n\n---\n\n".join(valid)


def systems_to_dataframe(systems: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of system dicts into a display-ready DataFrame.

    Args:
        systems: List of system dictionaries from the detector agent.

    Returns:
        A pandas DataFrame.
    """
    if not systems:
        return pd.DataFrame()

    rows = []
    for s in systems:
        rows.append(
            {
                "System Name": s.get("system_name", ""),
                "Category": s.get("category", ""),
                "Criticality": s.get("criticality", ""),
                "Auth Method": s.get("authentication_method", ""),
                "Business Process": s.get("business_process", ""),
                "Confidence Score": s.get("confidence_score", 0),
                "Manual Review": "⚠️ Yes" if s.get("manual_review") else "✅ No",
                "Key Data Entities": ", ".join(s.get("key_data_entities", [])),
                "Source Evidence": s.get("source_evidence", ""),
            }
        )

    return pd.DataFrame(rows)


def systems_to_json_str(systems: List[Dict[str, Any]]) -> str:
    """
    Serialize systems list to a pretty-printed JSON string.

    Args:
        systems: List of system dicts.

    Returns:
        JSON string.
    """
    return json.dumps(systems, indent=2, ensure_ascii=False)


def systems_to_csv_bytes(systems: List[Dict[str, Any]]) -> bytes:
    """
    Convert systems list to CSV bytes for download.

    Args:
        systems: List of system dicts.

    Returns:
        CSV content as bytes.
    """
    df = systems_to_dataframe(systems)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def compute_kpis(systems: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute KPI metrics from the list of detected systems.

    Args:
        systems: List of system dicts.

    Returns:
        Dictionary of KPI values.
    """
    if not systems:
        return {
            "total": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "avg_confidence": 0.0,
            "needs_review": 0,
        }

    total = len(systems)
    high = sum(1 for s in systems if s.get("criticality") == "High")
    medium = sum(1 for s in systems if s.get("criticality") == "Medium")
    low = sum(1 for s in systems if s.get("criticality") == "Low")
    scores = [s.get("confidence_score", 0) for s in systems]
    avg_confidence = round(sum(scores) / len(scores), 1) if scores else 0.0
    needs_review = sum(1 for s in systems if s.get("manual_review"))

    return {
        "total": total,
        "high": high,
        "medium": medium,
        "low": low,
        "avg_confidence": avg_confidence,
        "needs_review": needs_review,
    }


def confidence_color(score: int) -> str:
    """
    Return a color hex string based on confidence score.

    Args:
        score: Confidence score (0–100).

    Returns:
        A hex color string.
    """
    if score >= 90:
        return "#22c55e"   # Green
    elif score >= 70:
        return "#eab308"   # Yellow
    else:
        return "#ef4444"   # Red
