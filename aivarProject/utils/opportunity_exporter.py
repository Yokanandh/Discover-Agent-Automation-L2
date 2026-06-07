"""
opportunity_exporter.py
Utility functions for exporting automation opportunity reports.
"""

import io
import json
from typing import Any, Dict, List

import pandas as pd


def _normalize_opportunities(opportunities: Any) -> List[Dict[str, Any]]:
    if isinstance(opportunities, dict):
        return opportunities.get("automation_opportunities", []) or []
    if isinstance(opportunities, list):
        return opportunities
    return []


def opportunities_to_dataframe(opportunities: Any) -> pd.DataFrame:
    opportunities_list = _normalize_opportunities(opportunities)
    rows = []
    for item in opportunities_list:
        rows.append(
            {
                "Automation Name": item.get("automation_name", ""),
                "Source System": item.get("source_system", ""),
                "Target System": item.get("target_system", ""),
                "Related Systems": ", ".join(item.get("related_systems", [])),
                "Data Entities": ", ".join(item.get("data_entities", [])),
                "Priority": item.get("priority", ""),
                "Confidence Score": item.get("confidence_score", 0),
                "Business Impact": item.get("business_impact", ""),
                "Recommended Solution": item.get("recommended_solution", ""),
            }
        )
    return pd.DataFrame(rows)


def opportunities_to_json_str(opportunities: Any) -> str:
    opportunities_list = _normalize_opportunities(opportunities)
    return json.dumps(opportunities_list, indent=2, ensure_ascii=False)


def opportunities_to_csv_bytes(opportunities: Any) -> bytes:
    df = opportunities_to_dataframe(opportunities)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")
