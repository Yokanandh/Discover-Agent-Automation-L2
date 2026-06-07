"""
blueprint_generator.py
AI agent for generating integration blueprints from automation opportunities.
"""

import json
import re
import streamlit as st
import google.generativeai as genai
from typing import Any, Dict, List, Optional

BLUEPRINT_PROMPT = """
You are an enterprise integration architect specializing in system integration design.

Your task is to generate a comprehensive integration blueprint given:
1. Source system details
2. Target system details
3. An automation opportunity

Generate and return ONLY valid JSON. No markdown, no explanation, no code fences.

Return a JSON object with this exact structure:

{
  "blueprint": {
    "source_system": "",
    "target_system": "",
    "trigger": "",
    "action": "",
    "priority": "",
    "integration_type": "",
    "estimated_complexity": ""
  },
  "api_requirements": {
    "source_api": "",
    "target_api": "",
    "authentication": "",
    "required_endpoints": []
  },
  "data_mappings": [
    {
      "source_field": "",
      "target_field": "",
      "transformation": ""
    }
  ],
  "implementation_steps": [
    {
      "step": 1,
      "title": "",
      "description": ""
    }
  ],
  "risk_assessment": {
    "security_risk": "",
    "data_loss_risk": "",
    "failure_impact": "",
    "mitigation": ""
  }
}

Integration types: REST API, GraphQL, Webhook, File Transfer, Database Sync, Message Queue, Custom Connector
Complexity levels: Low, Medium, High, Very High
Priority levels: High, Medium, Low
Authentication types: OAuth2, API Key, Basic Auth, JWT, SAML, SSO
"""


def _build_user_message(
    source_system: str,
    target_system: str,
    automation_opportunity: Dict[str, Any],
) -> str:
    opportunity_json = json.dumps(automation_opportunity, indent=2, ensure_ascii=False)
    return (
        f"Source System: {source_system}\n"
        f"Target System: {target_system}\n\n"
        f"Automation Opportunity:\n{opportunity_json}\n\n"
        "Generate a comprehensive integration blueprint with API requirements, data mappings, implementation steps, and risk assessment. Return only valid JSON."
    )


def _parse_gemini_response(response_text: str) -> Dict[str, Any]:
    """Parse and validate Gemini blueprint response."""
    cleaned = re.sub(r"```(?:json)?", "", response_text, flags=re.IGNORECASE)
    cleaned = cleaned.strip().strip("`").strip()

    try:
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError:
        pass

    object_match = re.search(r"\{[\s\S]*\}", cleaned)
    if object_match:
        try:
            candidate = json.loads(object_match.group())
            return candidate
        except json.JSONDecodeError:
            pass

    st.error("❌ Could not parse Gemini blueprint response as JSON.")
    return {}


def _validate_blueprint_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize blueprint entry."""
    defaults = {
        "source_system": "Unknown",
        "target_system": "Unknown",
        "trigger": "Unknown",
        "action": "Unknown",
        "priority": "Medium",
        "integration_type": "REST API",
        "estimated_complexity": "Medium",
    }
    validated = {}
    for key, default in defaults.items():
        value = entry.get(key, default)
        validated[key] = str(value).strip() if value is not None else default
        if not validated[key]:
            validated[key] = default
    return validated


def _validate_api_requirements(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize API requirements."""
    defaults = {
        "source_api": "Unknown API",
        "target_api": "Unknown API",
        "authentication": "OAuth2",
        "required_endpoints": [],
    }
    validated = {}
    for key, default in defaults.items():
        value = entry.get(key, default)
        if key == "required_endpoints":
            if isinstance(value, list):
                validated[key] = [str(item).strip() for item in value if item]
            else:
                validated[key] = []
        else:
            validated[key] = str(value).strip() if value is not None else default
            if not validated[key]:
                validated[key] = default
    return validated


def _validate_data_mappings(mappings: Any) -> List[Dict[str, Any]]:
    """Validate and normalize data mappings."""
    if not isinstance(mappings, list):
        return []
    result = []
    for item in mappings:
        if isinstance(item, dict):
            result.append(
                {
                    "source_field": str(item.get("source_field", "")).strip() or "Unknown",
                    "target_field": str(item.get("target_field", "")).strip() or "Unknown",
                    "transformation": str(item.get("transformation", "")).strip() or "1:1 mapping",
                }
            )
    return result


def _validate_implementation_steps(steps: Any) -> List[Dict[str, Any]]:
    """Validate and normalize implementation steps."""
    if not isinstance(steps, list):
        return []
    result = []
    for index, item in enumerate(steps, 1):
        if isinstance(item, dict):
            result.append(
                {
                    "step": item.get("step", index),
                    "title": str(item.get("title", "")).strip() or f"Step {index}",
                    "description": str(item.get("description", "")).strip() or "No description provided.",
                }
            )
    return result


def _validate_risk_assessment(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize risk assessment."""
    defaults = {
        "security_risk": "Low",
        "data_loss_risk": "Low",
        "failure_impact": "Medium",
        "mitigation": "Standard integration practices recommended.",
    }
    validated = {}
    for key, default in defaults.items():
        value = entry.get(key, default)
        validated[key] = str(value).strip() if value is not None else default
        if not validated[key]:
            validated[key] = default
    return validated


def generate_integration_blueprint(
    source_system: str,
    target_system: str,
    automation_opportunity: Dict[str, Any],
    api_key: str,
    model_name: str = "gemini-2.5-flash",
) -> Optional[Dict[str, Any]]:
    """Generate a comprehensive integration blueprint."""
    if not api_key:
        st.error("❌ Gemini API key is missing. Please add GEMINI_API_KEY to .env.")
        return None

    if not source_system or not target_system or not automation_opportunity:
        st.error("❌ Source system, target system, and automation opportunity are required.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=BLUEPRINT_PROMPT,
        )
        user_message = _build_user_message(source_system, target_system, automation_opportunity)

        with st.spinner("🏗️ Generating integration blueprint..."):
            response = model.generate_content(
                user_message,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=8192,
                ),
            )

        raw_text = response.text
        with st.expander("🔍 Raw Blueprint Response", expanded=False):
            st.code(raw_text[:2000], language="text")

        parsed = _parse_gemini_response(raw_text)

        blueprint = _validate_blueprint_entry(parsed.get("blueprint", {}))
        api_requirements = _validate_api_requirements(parsed.get("api_requirements", {}))
        data_mappings = _validate_data_mappings(parsed.get("data_mappings", []))
        implementation_steps = _validate_implementation_steps(parsed.get("implementation_steps", []))
        risk_assessment = _validate_risk_assessment(parsed.get("risk_assessment", {}))

        return {
            "blueprint": blueprint,
            "api_requirements": api_requirements,
            "data_mappings": data_mappings,
            "implementation_steps": implementation_steps,
            "risk_assessment": risk_assessment,
        }

    except Exception as e:
        error_str = str(e)
        if "API_KEY_INVALID" in error_str or "401" in error_str:
            st.error("❌ Invalid Gemini API key.")
        elif "quota" in error_str.lower() or "429" in error_str:
            st.error("❌ Gemini API quota exceeded.")
        elif "404" in error_str:
            st.error(f"❌ Model '{model_name}' not found.")
        else:
            st.error(f"❌ Gemini API error: {e}")
        return None
