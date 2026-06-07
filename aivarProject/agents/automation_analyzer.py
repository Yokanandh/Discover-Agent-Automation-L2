"""
automation_analyzer.py
AI agent for comparing discovered systems to business requirements and recommending automation opportunities.
"""

import json
import re
import streamlit as st
import google.generativeai as genai
from typing import Any, Dict, List, Optional

AUTOMATION_PROMPT = """
You are an expert automation architect and business systems analyst.

Your task is to analyze the business requirement and the discovered software systems inventory.
Compare the inventory against the requirement and identify automation opportunities, integration requirements, and gaps.

You must return ONLY valid JSON. No markdown, no explanation, no code fences.

Return a JSON object with the exact structure:
{
  "automation_opportunities": [
    {
      "automation_name": "",
      "source_system": "",
      "target_system": "",
      "related_systems": [],
      "data_entities": [],
      "priority": "",
      "business_impact": "",
      "recommended_solution": "",
      "confidence_score": 0
    }
  ],
  "integration_analysis": [
    {
      "source_system": "",
      "target_system": "",
      "data_flow_direction": "",
      "required_data_entities": [],
      "integration_requirement": ""
    }
  ],
  "gap_analysis": {
      "gap_description": "",
      "risk_level": "",
      "business_impact": "",
      "recommended_automation": ""
  }
}

Use the following priority rules:
- HIGH: Revenue, Finance, CRM, ERP, Customer Data
- MEDIUM: Operations, HR, Support
- LOW: Internal Communication, Reporting

If integration is detected, populate automation_opportunities and integration_analysis.
If no integration is detected, return automation_opportunities as [] and populate gap_analysis.
"""


def _build_user_message(requirement: str, systems: List[Dict[str, Any]]) -> str:
    system_list = json.dumps(systems, indent=2, ensure_ascii=False)
    trimmed_requirement = requirement.strip()
    return (
        f"Business requirement:\n{trimmed_requirement}\n\n"
        f"Discovered systems inventory:\n{system_list}\n\n"
        "Analyze the systems and requirement to identify automation opportunities, integration gaps,"
        " and recommended workflows. Return only valid JSON as described above."
    )


def _clean_response_text(response_text: str) -> str:
    cleaned = re.sub(r"```(?:json)?", "", response_text, flags=re.IGNORECASE)
    cleaned = cleaned.strip().strip("`").strip()
    return cleaned


def _parse_gemini_response(response_text: str) -> Any:
    cleaned = _clean_response_text(response_text)

    try:
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError:
        pass

    array_match = re.search(r"\[[\s\S]*\]", cleaned)
    if array_match:
        try:
            candidate = json.loads(array_match.group())
            return candidate
        except json.JSONDecodeError:
            pass

    object_match = re.search(r"\{[\s\S]*\}", cleaned)
    if object_match:
        try:
            candidate = json.loads(object_match.group())
            return candidate
        except json.JSONDecodeError:
            pass

    st.error(
        "❌ Could not parse Gemini automation analyzer response. "
        "Open the raw response expander to inspect the returned text."
    )
    return {}


def _normalize_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if item is not None and str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in re.split(r",|;|\n", value) if item.strip()]
    if value is None:
        return []
    return [str(value).strip()]


def _normalize_priority(priority: Any) -> str:
    if not priority:
        return "Medium"
    label = str(priority).lower()
    high_keywords = ["high", "revenue", "finance", "crm", "erp", "customer"]
    medium_keywords = ["medium", "operations", "hr", "support"]
    low_keywords = ["low", "communication", "reporting"]
    if any(keyword in label for keyword in high_keywords):
        return "High"
    if any(keyword in label for keyword in medium_keywords):
        return "Medium"
    if any(keyword in label for keyword in low_keywords):
        return "Low"
    return "Medium"


def _validate_opportunity(entry: Dict[str, Any]) -> Dict[str, Any]:
    defaults = {
        "automation_name": "Automation Opportunity",
        "source_system": "Unknown",
        "target_system": "Unknown",
        "related_systems": [],
        "data_entities": [],
        "priority": "Medium",
        "business_impact": "No impact description provided.",
        "recommended_solution": "No recommended solution provided.",
        "confidence_score": 0,
    }

    validated: Dict[str, Any] = {}
    for key, default in defaults.items():
        value = entry.get(key, default)
        if key in ["related_systems", "data_entities"]:
            validated[key] = _normalize_list(value)
        elif key == "priority":
            validated[key] = _normalize_priority(value)
        elif key == "confidence_score":
            try:
                validated[key] = max(0, min(100, int(value)))
            except (TypeError, ValueError):
                validated[key] = 0
        else:
            text_value = str(value).strip()
            validated[key] = text_value if text_value else default

    if not validated["automation_name"] or validated["automation_name"].lower() == "automation opportunity":
        validated["automation_name"] = (
            f"{validated['source_system']} to {validated['target_system']} Automation".strip()
        )

    return validated


def _validate_integration(entry: Dict[str, Any]) -> Dict[str, Any]:
    defaults = {
        "source_system": "Unknown",
        "target_system": "Unknown",
        "data_flow_direction": "Unknown",
        "required_data_entities": [],
        "integration_requirement": "No integration requirement provided.",
    }
    validated = {}
    for key, default in defaults.items():
        value = entry.get(key, default)
        if key == "required_data_entities":
            validated[key] = _normalize_list(value)
        else:
            validated[key] = str(value).strip() if value is not None else default
            if not validated[key]:
                validated[key] = default
    return validated


def _validate_gap(entry: Dict[str, Any]) -> Dict[str, Any]:
    defaults = {
        "gap_description": "No gap description provided.",
        "risk_level": "Medium",
        "business_impact": "No business impact provided.",
        "recommended_automation": "No recommended automation provided.",
    }
    validated = {}
    for key, default in defaults.items():
        value = entry.get(key, default)
        validated[key] = str(value).strip() if value is not None else default
        if not validated[key]:
            validated[key] = default
    return validated


def analyze_automation_opportunities(
    business_requirement: str,
    systems: List[Dict[str, Any]],
    api_key: str,
    model_name: str = "gemini-2.5-flash",
) -> Optional[Dict[str, Any]]:
    if not api_key:
        st.error("❌ Gemini API key is missing. Please add GEMINI_API_KEY to your .env file.")
        return None

    requirement = business_requirement.strip()
    if not requirement:
        st.error("❌ Enter a business requirement to analyze automation opportunity.")
        return None

    if not systems:
        st.error("❌ No discovered systems are available. Run system discovery first.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=AUTOMATION_PROMPT,
        )
        user_message = _build_user_message(requirement, systems)

        with st.spinner("⚡ Analyzing business requirements and discovered systems..."):
            response = model.generate_content(
                user_message,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=8192,
                ),
            )

        raw_text = response.text
        with st.expander("🔍 Raw Automation Analyzer Response", expanded=False):
            st.code(raw_text[:3000], language="text")

        parsed = _parse_gemini_response(raw_text)
        automation_opportunities: List[Dict[str, Any]] = []
        integration_analysis: List[Dict[str, Any]] = []
        gap_analysis: Dict[str, Any] = {
            "gap_description": "No integration gap detected.",
            "risk_level": "Low",
            "business_impact": "No business impact identified.",
            "recommended_automation": "No recommended automation required.",
        }

        if isinstance(parsed, dict):
            automation_opportunities = parsed.get("automation_opportunities", []) or []
            integration_analysis = parsed.get("integration_analysis", []) or []
            gap_analysis = _validate_gap(parsed.get("gap_analysis", {}) if isinstance(parsed.get("gap_analysis", {}), dict) else {})
        elif isinstance(parsed, list):
            automation_opportunities = parsed
        else:
            st.error("❌ Gemini returned an unsupported response structure.")
            return None

        validated_opportunities = [_validate_opportunity(entry) for entry in automation_opportunities]
        validated_integration = [_validate_integration(entry) for entry in integration_analysis]

        return {
            "automation_opportunities": validated_opportunities,
            "integration_analysis": validated_integration,
            "gap_analysis": gap_analysis,
        }

    except Exception as e:
        error_str = str(e)
        if "API_KEY_INVALID" in error_str or "401" in error_str:
            st.error("❌ Invalid Gemini API key. Please verify the key in .env.")
        elif "quota" in error_str.lower() or "429" in error_str:
            st.error("❌ Gemini API quota exceeded. Please wait or upgrade your plan.")
        elif "404" in error_str:
            st.error(f"❌ Model '{model_name}' not found. Try updating the model name.")
        else:
            st.error(f"❌ Gemini API error: {e}")
        return None
