"""
code_generator.py
AI agent for generating sample integration code implementations.
"""

import re
import streamlit as st
import google.generativeai as genai
from typing import Optional

CODE_GENERATION_PROMPT = """
You are an expert Python developer specializing in enterprise integration patterns.

Your task is to generate sample Python integration code for a blueprint.

Important rules:
- Generate ONLY production-quality Python code.
- NO real credentials, API keys, or passwords.
- Use placeholder values like <SALESFORCE_INSTANCE_URL>, <API_KEY>, etc.
- Include comprehensive error handling and logging.
- Include docstrings and comments.
- Do NOT make real API calls.
- Use industry best practices.
- Include proper exception handling.
- Return ONLY valid Python code.

Generate a complete, well-commented Python integration module that demonstrates:
1. Authentication (placeholder)
2. Reading from source system
3. Data transformation
4. Writing to target system
5. Error handling and logging
6. Retry logic

The code should be educational and production-grade, but with all credentials and URLs as placeholders.
"""


def _parse_gemini_code_response(response_text: str) -> str:
    """Extract and clean Python code from Gemini response."""
    cleaned = re.sub(r"```python", "", response_text, flags=re.IGNORECASE)
    cleaned = re.sub(r"```", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned


def generate_integration_code(
    source_system: str,
    target_system: str,
    data_mappings: list,
    api_key: str,
    model_name: str = "gemini-2.5-flash",
) -> Optional[str]:
    """Generate sample Python integration code."""
    if not api_key:
        st.error("❌ Gemini API key is missing.")
        return None

    if not source_system or not target_system:
        st.error("❌ Source and target systems are required.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=CODE_GENERATION_PROMPT,
        )

        mapping_description = "\n".join(
            [f"  {m.get('source_field', '')} → {m.get('target_field', '')}" for m in data_mappings[:5]]
        )

        user_message = (
            f"Generate sample Python integration code for:\n\n"
            f"Source System: {source_system}\n"
            f"Target System: {target_system}\n\n"
            f"Data Mappings:\n{mapping_description}\n\n"
            "Generate production-quality Python code with error handling, logging, and placeholder credentials."
        )

        with st.spinner("💻 Generating integration code..."):
            response = model.generate_content(
                user_message,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=4096,
                ),
            )

        raw_code = response.text
        return _parse_gemini_code_response(raw_code)

    except Exception as e:
        error_str = str(e)
        if "API_KEY_INVALID" in error_str or "401" in error_str:
            st.error("❌ Invalid Gemini API key.")
        elif "quota" in error_str.lower() or "429" in error_str:
            st.error("❌ Gemini API quota exceeded.")
        else:
            st.error(f"❌ Gemini API error: {e}")
        return None
