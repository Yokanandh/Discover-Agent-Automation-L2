import os
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv

from agents.blueprint_generator import generate_integration_blueprint
from agents.code_generator import generate_integration_code
from utils.mapping_engine import create_mapping_table, export_mappings_json
from utils.risk_analyzer import analyze_integration_risks

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(
    page_title="Integration Blueprint",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .blueprint-title {
        color: #facc15;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
        line-height: 1.05;
        font-family: 'Playfair Display', serif;
    }
    .blueprint-subtitle {
        color: #cbd5e1;
        margin-top: 0.3rem;
        margin-bottom: 1.4rem;
        font-size: 1rem;
        line-height: 1.6;
        font-family: 'Poppins', sans-serif;
    }
    .blueprint-card {
        background: #111111;
        border: 1px solid rgba(250, 204, 21, 0.18);
        border-radius: 18px;
        padding: 1.4rem;
        margin-bottom: 1.25rem;
    }
    .blueprint-section-title {
        color: #facc15;
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        font-family: 'Playfair Display', serif;
    }
    .architecture-diagram {
        background: rgba(250, 204, 21, 0.08);
        border: 1px solid rgba(250, 204, 21, 0.2);
        border-radius: 14px;
        padding: 2rem 1.5rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    .arch-box {
        background: rgba(250, 204, 21, 0.15);
        border: 2px solid rgba(250, 204, 21, 0.4);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        color: #f8f8f2;
        font-weight: 700;
        margin: 0.5rem auto;
        width: fit-content;
    }
    .arch-arrow {
        color: #facc15;
        font-size: 1.8rem;
        margin: 0.3rem 0;
    }
    .risk-high {
        background: rgba(248, 113, 113, 0.15);
        border-left: 4px solid #f87171;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .risk-medium {
        background: rgba(251, 191, 36, 0.15);
        border-left: 4px solid #fbbf24;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .risk-low {
        background: rgba(52, 211, 153, 0.15);
        border-left: 4px solid #34d399;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .small-note {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='blueprint-title'>Integration Blueprint Generator</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='blueprint-subtitle'>Design comprehensive integration architectures with API requirements, data mappings, implementation plans, and risk assessments.</div>",
    unsafe_allow_html=True,
)

if "automation_results" not in st.session_state or not st.session_state.automation_results:
    st.warning(
        "⚠️ No automation opportunity is available. Run the Automation Analyzer page first to identify an automation opportunity."
    )
    st.stop()

automation_results = st.session_state.automation_results
opportunities = automation_results.get("automation_opportunities", [])

if not opportunities:
    st.info("No automation opportunities found. Analyze a business requirement first.")
    st.stop()

opportunity = opportunities[0]
source_system = opportunity.get("source_system", "Unknown")
target_system = opportunity.get("target_system", "Unknown")

st.markdown("<div class='blueprint-card'>", unsafe_allow_html=True)
st.markdown("<div class='blueprint-section-title'>📋 Selected Opportunity</div>", unsafe_allow_html=True)
st.markdown(
    f"<div style='line-height:1.7;'>"
    f"<strong>Automation:</strong> {opportunity.get('automation_name', 'Unknown')}<br>"
    f"<strong>Source:</strong> {source_system}<br>"
    f"<strong>Target:</strong> {target_system}<br>"
    f"<strong>Priority:</strong> {opportunity.get('priority', 'Unknown')}<br>"
    f"<strong>Business Impact:</strong> {opportunity.get('business_impact', 'Unknown')}"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

col_generate, col_spacer = st.columns([2, 5])
with col_generate:
    generate_clicked = st.button("🏗️ Generate Blueprint", type="primary", use_container_width=True)

if generate_clicked:
    blueprint_data = generate_integration_blueprint(
        source_system,
        target_system,
        opportunity,
        GEMINI_API_KEY,
    )
    if blueprint_data:
        st.session_state.blueprint_data = blueprint_data

blueprint_data = st.session_state.get("blueprint_data", {})

if blueprint_data:
    blueprint = blueprint_data.get("blueprint", {})
    api_requirements = blueprint_data.get("api_requirements", {})
    data_mappings = blueprint_data.get("data_mappings", [])
    implementation_steps = blueprint_data.get("implementation_steps", [])
    risk_assessment = blueprint_data.get("risk_assessment", {})

    st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.12);'>", unsafe_allow_html=True)

    st.markdown("<div class='blueprint-card'>", unsafe_allow_html=True)
    st.markdown("<div class='blueprint-section-title'>🏗️ Integration Blueprint</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='line-height:1.8;'>"
        f"<strong>Integration Type:</strong> {blueprint.get('integration_type', 'Unknown')}<br>"
        f"<strong>Trigger:</strong> {blueprint.get('trigger', 'Unknown')}<br>"
        f"<strong>Action:</strong> {blueprint.get('action', 'Unknown')}<br>"
        f"<strong>Estimated Complexity:</strong> {blueprint.get('estimated_complexity', 'Unknown')}<br>"
        f"<strong>Priority:</strong> {blueprint.get('priority', 'Unknown')}"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='blueprint-card'>", unsafe_allow_html=True)
    st.markdown("<div class='blueprint-section-title'>🏛️ Architecture Diagram</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='architecture-diagram'>"
        f"<div class='arch-box'>{source_system}</div>"
        "<div class='arch-arrow'>↓</div>"
        "<div class='arch-box'>API Layer</div>"
        "<div class='arch-arrow'>↓</div>"
        "<div class='arch-box'>Transformation Engine</div>"
        "<div class='arch-arrow'>↓</div>"
        f"<div class='arch-box'>{target_system}</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='blueprint-card'>", unsafe_allow_html=True)
    st.markdown("<div class='blueprint-section-title'>🔌 API Requirements</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='line-height:1.8;'>"
        f"<strong>Source API:</strong> {api_requirements.get('source_api', 'Unknown')}<br>"
        f"<strong>Target API:</strong> {api_requirements.get('target_api', 'Unknown')}<br>"
        f"<strong>Authentication:</strong> {api_requirements.get('authentication', 'Unknown')}<br>"
        f"<strong>Required Endpoints:</strong> {', '.join(api_requirements.get('required_endpoints', []))}"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='blueprint-card'>", unsafe_allow_html=True)
    st.markdown("<div class='blueprint-section-title'>🗺️ Data Mapping</div>", unsafe_allow_html=True)
    if data_mappings:
        mapping_df = create_mapping_table(data_mappings)
        st.dataframe(mapping_df, use_container_width=True, hide_index=True)
    else:
        st.info("No data mappings generated.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='blueprint-card'>", unsafe_allow_html=True)
    st.markdown("<div class='blueprint-section-title'>📝 Implementation Steps</div>", unsafe_allow_html=True)
    if implementation_steps:
        steps_html = ""
        for step in implementation_steps:
            steps_html += (
                f"<div style='margin-bottom:1rem;'>"
                f"<strong style='color:#facc15;'>Step {step.get('step', '')}:</strong> {step.get('title', '')}<br>"
                f"<span style='color:#cbd5e1; font-size:0.9rem;'>{step.get('description', '')}</span>"
                "</div>"
            )
        st.markdown(steps_html, unsafe_allow_html=True)
    else:
        st.info("No implementation steps generated.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='blueprint-card'>", unsafe_allow_html=True)
    st.markdown("<div class='blueprint-section-title'>⚠️ Risk Assessment</div>", unsafe_allow_html=True)
    risk_level_color = {
        "High": "#f87171",
        "Medium": "#fbbf24",
        "Low": "#34d399",
    }
    for risk_key, risk_value in risk_assessment.items():
        risk_class = f"risk-{risk_value.lower()}"
        display_key = risk_key.replace("_", " ").title()
        st.markdown(f"<div class='{risk_class}'><strong>{display_key}:</strong> {risk_value}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("🔐 Detailed Risk Analysis", expanded=False):
        risk_details = analyze_integration_risks(
            source_system,
            target_system,
            data_sensitivity="Medium",
            integration_type=blueprint.get("integration_type", "REST API"),
        )
        st.json(risk_details)

    with st.expander("💻 Sample Implementation Code", expanded=False):
        code = generate_integration_code(
            source_system,
            target_system,
            data_mappings,
            GEMINI_API_KEY,
        )
        if code:
            st.code(code, language="python")
        else:
            st.info("Could not generate sample code.")

    cols = st.columns([2, 2, 2, 4])
    with cols[0]:
        st.download_button(
            label="📥 Blueprint JSON",
            data=st.session_state.get("blueprint_json", "{}"),
            file_name="integration_blueprint.json",
            mime="application/json",
            use_container_width=True,
        )
    with cols[1]:
        st.download_button(
            label="📥 Mappings JSON",
            data=export_mappings_json(data_mappings),
            file_name="data_mappings.json",
            mime="application/json",
            use_container_width=True,
        )
    with cols[2]:
        st.download_button(
            label="📥 Code Template",
            data=generate_integration_code(source_system, target_system, data_mappings, GEMINI_API_KEY) or "# Code generation failed",
            file_name="integration_template.py",
            mime="text/plain",
            use_container_width=True,
        )
    with cols[3]:
        st.markdown("<div class='small-note'>Export blueprint, mappings, and code template for your development team.</div>", unsafe_allow_html=True)

else:
    st.info("Click 'Generate Blueprint' to create a comprehensive integration blueprint for the selected opportunity.")
