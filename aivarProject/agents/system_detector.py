"""
system_detector.py
Core AI agent that uses the Gemini API to detect software systems
from extracted document text and returns structured inventory data.
"""

import json
import re
import streamlit as st
import google.generativeai as genai
from typing import List, Dict, Any, Optional


# ── Prompt template ──────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert Enterprise Architect and IT Systems Analyst.

Your task is to analyze the provided document text and identify EVERY software system,
tool, platform, or application mentioned — directly or by inference.

For EACH discovered system, return a JSON object with these exact fields:

{
  "system_name": "<name of the software>",
  "category": "<one of: ERP | CRM | Finance | Payment Systems | Project Management | Support Platforms | Communication | Design Tools | Analytics | Security | DevOps | HR | Other>",
  "authentication_method": "<e.g. SSO, OAuth2, SAML, API Key, Username/Password, Unknown>",
  "key_data_entities": ["<list>", "<of>", "<main>", "<data>", "<objects>"],
  "business_process": "<the business process this system supports>",
  "criticality": "<High | Medium | Low>",
  "confidence_score": <integer 0-100>,
  "manual_review": <true | false>,
  "source_evidence": "<the exact phrase or sentence from the text that revealed this system>"
}

CRITICALITY RULES (apply strictly):
- High: ERP, CRM, Finance, Payment Systems
- Medium: Project Management, Support Platforms
- Low: Communication, Design Tools, Analytics, Security, DevOps, HR, Other

CONFIDENCE RULES (apply strictly):
- 95-100: System name is explicitly and clearly mentioned
- 70-90: Strong contextual inference
- Below 70: Weak inference — also set manual_review = true

IMPORTANT:
- Return ONLY a valid JSON array. No markdown, no explanation, no code fences, no preamble.
- Start your response with [ and end with ]
- If no systems are found, return []
- Do not duplicate systems.
"""


def _build_user_message(text: str) -> str:
    max_chars = 30_000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... text truncated ...]"
    return f"Analyze the following document text and extract all software systems:\n\n{text}"


def _parse_gemini_response(response_text: str) -> List[Dict[str, Any]]:
    """
    Parse the JSON response from Gemini with multiple fallback strategies.
    Shows the raw response in a debug expander.
    """
    # Show raw response for debugging
    with st.expander("🔍 Raw Gemini Response (debug)", expanded=False):
        st.code(response_text[:3000], language="text")

    # Clean markdown fences
    cleaned = re.sub(r"```(?:json)?", "", response_text, flags=re.IGNORECASE)
    cleaned = cleaned.strip().strip("`").strip()

    # Attempt 1: direct JSON parse of cleaned text
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("systems", "results", "data", "software_systems", "inventory"):
                if key in data and isinstance(data[key], list):
                    return data[key]
            if "system_name" in data:
                return [data]
    except json.JSONDecodeError:
        pass

    # Attempt 2: find JSON array anywhere in the text (greedy)
    match = re.search(r"\[[\s\S]*\]", cleaned)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    # Attempt 3: find first JSON object (single item response)
    match = re.search(r"\{[\s\S]*?\}", cleaned)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, dict) and "system_name" in data:
                return [data]
        except json.JSONDecodeError:
            pass

    st.error(
        "❌ Could not parse Gemini response as JSON. "
        "Check the raw response in the expander above."
    )
    return []


def _validate_and_fix_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate each system entry and apply business rules.
    """
    defaults = {
        "system_name": "Unknown",
        "category": "Other",
        "authentication_method": "Unknown",
        "key_data_entities": [],
        "business_process": "N/A",
        "criticality": "Low",
        "confidence_score": 50,
        "manual_review": False,
        "source_evidence": "",
    }

    for key, default in defaults.items():
        if key not in entry or entry[key] is None:
            entry[key] = default

    try:
        entry["confidence_score"] = int(entry["confidence_score"])
    except (ValueError, TypeError):
        entry["confidence_score"] = 50

    entry["confidence_score"] = max(0, min(100, entry["confidence_score"]))

    if entry["confidence_score"] < 70:
        entry["manual_review"] = True

    category = entry.get("category", "Other")
    high_cats = {"ERP", "CRM", "Finance", "Payment Systems"}
    medium_cats = {"Project Management", "Support Platforms"}
    if category in high_cats:
        entry["criticality"] = "High"
    elif category in medium_cats:
        entry["criticality"] = "Medium"
    else:
        entry["criticality"] = "Low"

    if not isinstance(entry["key_data_entities"], list):
        entry["key_data_entities"] = [str(entry["key_data_entities"])]

    return entry


def detect_systems(
    extracted_text: str,
    api_key: str,
    model_name: str = "gemini-2.5-flash",
) -> Optional[List[Dict[str, Any]]]:
    """
    Send extracted text to Gemini and return a structured list of detected systems.
    """
    if not api_key:
        st.error("❌ Gemini API key is missing.")
        return None

    if not extracted_text or not extracted_text.strip():
        st.error("❌ No text was extracted from the documents.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_PROMPT,
        )

        user_message = _build_user_message(extracted_text)

        with st.spinner("🤖 Gemini is analyzing your documents..."):
            response = model.generate_content(
                user_message,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=8192,
                ),
            )

        raw_text = response.text
        systems = _parse_gemini_response(raw_text)
        validated = [_validate_and_fix_entry(entry) for entry in systems]
        return validated

    except Exception as e:
        error_str = str(e)
        if "API_KEY_INVALID" in error_str or "401" in error_str:
            st.error("❌ Invalid Gemini API key. Please check your .env file.")
        elif "quota" in error_str.lower() or "429" in error_str:
            st.error("❌ Gemini API quota exceeded. Please wait or upgrade your plan.")
        elif "404" in error_str:
            st.error(f"❌ Model '{model_name}' not found. Try 'gemini-2.0-flash-lite' or 'gemini-pro'.")
        else:
            st.error(f"❌ Gemini API error: {e}")
        return None
