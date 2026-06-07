"""
mapping_engine.py
Data mapping engine for field transformation and validation.
"""

import json
from typing import Any, Dict, List, Optional

from pandas import DataFrame


def create_mapping_table(mappings: List[Dict[str, Any]]) -> DataFrame:
    """
    Convert raw mappings into a display-ready DataFrame.

    Args:
        mappings: List of mapping dictionaries.

    Returns:
        A pandas DataFrame for visualization.
    """
    import pandas as pd

    if not mappings:
        return pd.DataFrame()

    rows = []
    for idx, mapping in enumerate(mappings, 1):
        rows.append(
            {
                "No.": idx,
                "Source Field": mapping.get("source_field", ""),
                "Target Field": mapping.get("target_field", ""),
                "Transformation": mapping.get("transformation", "1:1 mapping"),
            }
        )

    return pd.DataFrame(rows)


def export_mappings_json(mappings: List[Dict[str, Any]]) -> str:
    """
    Export mappings as a JSON string.

    Args:
        mappings: List of mapping dictionaries.

    Returns:
        Pretty-printed JSON string.
    """
    export_data = {
        "version": "1.0",
        "mapping_count": len(mappings),
        "mappings": mappings,
    }
    return json.dumps(export_data, indent=2, ensure_ascii=False)


def validate_mapping_completeness(
    source_fields: List[str],
    target_fields: List[str],
    mappings: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Validate mapping coverage and completeness.

    Args:
        source_fields: Available source system fields.
        target_fields: Available target system fields.
        mappings: Current mapping definitions.

    Returns:
        Dictionary with validation results.
    """
    if not mappings:
        return {
            "coverage": 0.0,
            "unmapped_sources": source_fields,
            "unmapped_targets": target_fields,
            "is_complete": False,
            "message": "No mappings defined.",
        }

    mapped_sources = [m.get("source_field") for m in mappings if m.get("source_field")]
    mapped_targets = [m.get("target_field") for m in mappings if m.get("target_field")]

    unmapped_sources = [f for f in source_fields if f not in mapped_sources]
    unmapped_targets = [f for f in target_fields if f not in mapped_targets]

    coverage = (len(mapped_sources) / len(source_fields)) * 100 if source_fields else 0.0
    is_complete = len(unmapped_sources) == 0 and len(unmapped_targets) == 0

    return {
        "coverage": round(coverage, 1),
        "unmapped_sources": unmapped_sources,
        "unmapped_targets": unmapped_targets,
        "is_complete": is_complete,
        "message": (
            "All fields mapped successfully."
            if is_complete
            else f"{len(unmapped_sources)} source fields and {len(unmapped_targets)} target fields unmapped."
        ),
    }


def generate_transformation_hints(
    source_field: str,
    target_field: str,
) -> Optional[str]:
    """
    Generate transformation hints based on field names.

    Args:
        source_field: Source field name.
        target_field: Target field name.

    Returns:
        Suggested transformation or None.
    """
    hints = {
        ("Amount", "Total"): "Direct mapping",
        ("Price", "Cost"): "Direct mapping",
        ("First Name", "GivenName"): "Direct mapping",
        ("Last Name", "FamilyName"): "Direct mapping",
        ("Email", "EmailAddress"): "Direct mapping",
        ("Phone", "PhoneNumber"): "Direct mapping",
        ("Date", "Timestamp"): "Convert to ISO 8601",
        ("Amount", "NetAmount"): "Apply tax calculation",
        ("Quantity", "Units"): "Direct mapping",
        ("Status", "State"): "Enum mapping required",
    }

    for (source, target), hint in hints.items():
        if source.lower() in source_field.lower() and target.lower() in target_field.lower():
            return hint

    return "Custom transformation required"
