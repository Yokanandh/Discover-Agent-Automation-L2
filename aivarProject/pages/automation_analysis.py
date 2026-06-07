import os
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv

from agents.automation_analyzer import analyze_automation_opportunities
from utils.opportunity_exporter import (
    opportunities_to_csv_bytes,
    opportunities_to_dataframe,
    opportunities_to_json_str,
)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


st.set_page_config(
    page_title="Automation Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .page-title {
        color: #facc15;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
        line-height: 1.05;
        font-family: 'Playfair Display', serif;
    }
    .section-subtitle {
        color: #cbd5e1;
        margin-top: 0.3rem;
        margin-bottom: 1.4rem;
        font-size: 1rem;
        line-height: 1.6;
        font-family: 'Poppins', sans-serif;
    }
    .analysis-card {
        background: #111111;
        border: 1px solid rgba(250, 204, 21, 0.18);
        border-radius: 18px;
        padding: 1.4rem 1.4rem;
        margin-bottom: 1.25rem;
    }
    .flow-node {
        background: rgba(250, 204, 21, 0.12);
        border: 1px solid rgba(250, 204, 21, 0.4);
        border-radius: 18px;
        color: #f8f8f2;
        padding: 1rem 1.25rem;
        margin: 0.5rem auto;
        text-align: center;
        font-weight: 700;
        width: min(320px, 100%);
    }
    .flow-arrow {
        color: #facc15;
        font-size: 2rem;
        text-align: center;
        margin: 0.2rem auto 0.2rem auto;
    }
    .opportunity-table {
        border-radius: 18px;
        overflow: hidden;
    }
    .small-note {
        color: #94a3b8;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='page-title'>Automation Analyzer</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-subtitle'>Analyze business requirements against discovered systems, detect integration gaps, and generate automation opportunities with confidence scoring.</div>",
    unsafe_allow_html=True,
)

if "systems" not in st.session_state or not st.session_state.systems:
    st.warning(
        "⚠️ No discovered systems are available. Run the Discovery Agent page first to extract systems from your documents."
    )

business_requirement = st.text_area(
    "Business Requirement",
    value=st.session_state.get("automation_request", ""),
    placeholder="When a Salesforce opportunity is marked Closed Won, automatically create an invoice in NetSuite.",
    height=170,
)
st.session_state.automation_request = business_requirement

analyze_clicked = st.button("⚡ Analyze Automation Opportunity", type="primary")

if analyze_clicked:
    if not business_requirement.strip():
        st.error("Please enter a business requirement before analyzing.")
    elif not st.session_state.systems:
        st.error("No discovered systems are available. Run system discovery first.")
    else:
        automation_data = analyze_automation_opportunities(
            business_requirement,
            st.session_state.systems,
            GEMINI_API_KEY,
        )
        if automation_data is not None:
            st.session_state.automation_results = automation_data

automation_results = st.session_state.get("automation_results", {})
automation_opportunities = automation_results.get("automation_opportunities", [])
integration_analysis = automation_results.get("integration_analysis", [])
gap_analysis = automation_results.get("gap_analysis", {})


def compute_opportunity_kpis(opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(opportunities)
    high = sum(1 for item in opportunities if item.get("priority") == "High")
    medium = sum(1 for item in opportunities if item.get("priority") == "Medium")
    low = sum(1 for item in opportunities if item.get("priority") == "Low")
    scores = [item.get("confidence_score", 0) for item in opportunities]
    avg_confidence = round(sum(scores) / len(scores), 1) if scores else 0.0
    return {
        "total": total,
        "high": high,
        "medium": medium,
        "low": low,
        "avg_confidence": avg_confidence,
    }


def render_flow_block(integration: List[Dict[str, Any]], opportunities: List[Dict[str, Any]]) -> None:
    if integration:
        flow_source = integration[0].get("source_system", "")
        flow_target = integration[0].get("target_system", "")
        if flow_source and flow_target:
            flow_nodes = [flow_source, flow_target]
        else:
            flow_nodes = []
    elif opportunities:
        first = opportunities[0]
        if first.get("source_system") and first.get("target_system"):
            flow_nodes = [first["source_system"], first["target_system"]]
        else:
            flow_nodes = []
    else:
        flow_nodes = []

    if flow_nodes:
        flow_html = ""
        for index, node in enumerate(flow_nodes):
            flow_html += f"<div class='flow-node'>{node}</div>"
            if index < len(flow_nodes) - 1:
                flow_html += "<div class='flow-arrow'>↓</div>"
        st.markdown(flow_html, unsafe_allow_html=True)
    else:
        st.info("No visual integration flow is available yet. Analyze a business requirement to generate a flow.")


if automation_opportunities or gap_analysis:
    st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.12);'>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Automation recommendation results are shown below.</div>", unsafe_allow_html=True)

    if automation_opportunities:
        kpis = compute_opportunity_kpis(automation_opportunities)
        cols = st.columns(5)
        card_values = [
            (cols[0], kpis["total"], "Total Opportunities", "#facc15"),
            (cols[1], kpis["high"], "High Priority", "#f87171"),
            (cols[2], kpis["medium"], "Medium Priority", "#fbbf24"),
            (cols[3], kpis["low"], "Low Priority", "#34d399"),
            (cols[4], f"{kpis['avg_confidence']}%", "Average Confidence", "#60a5fa"),
        ]
        for col, value, label, color in card_values:
            with col:
                st.markdown(
                    f"<div class='analysis-card'><div style='font-size:2rem; font-weight:800; color:{color};'>{value}</div>"
                    f"<div style='margin-top:0.55rem; color:#cbd5e1; font-weight:700;'>{label}</div></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#facc15; margin-bottom:0.5rem;'>Integration Flow</h4>", unsafe_allow_html=True)
        render_flow_block(integration_analysis, automation_opportunities)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#facc15; margin-bottom:0.75rem;'>Integration Analysis</h4>", unsafe_allow_html=True)
        if integration_analysis:
            integration = integration_analysis[0]
            st.markdown(
                f"<strong>Source System:</strong> {integration.get('source_system', 'Unknown')}<br>"
                f"<strong>Target System:</strong> {integration.get('target_system', 'Unknown')}<br>"
                f"<strong>Data Flow Direction:</strong> {integration.get('data_flow_direction', 'Unknown')}<br>"
                f"<strong>Required Data Entities:</strong> {', '.join(integration.get('required_data_entities', []))}<br>"
                f"**Integration Requirement:** {integration.get('integration_requirement', 'N/A')}"
            )
        else:
            st.info("No detailed integration analysis was produced for this requirement.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#facc15; margin-bottom:0.75rem;'>Opportunity Table</h4>", unsafe_allow_html=True)
        df = opportunities_to_dataframe(automation_opportunities)
        st.dataframe(df, use_container_width=True, height=380)
        st.markdown("</div>", unsafe_allow_html=True)

        cols = st.columns([2, 2, 4])
        with cols[0]:
            st.download_button(
                label="📥 Download Report JSON",
                data=opportunities_to_json_str(automation_opportunities),
                file_name="automation_opportunities.json",
                mime="application/json",
                use_container_width=True,
            )
        with cols[1]:
            st.download_button(
                label="📥 Download Report CSV",
                data=opportunities_to_csv_bytes(automation_opportunities),
                file_name="automation_opportunities.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with cols[2]:
            st.markdown("<div class='small-note'>Export the automation opportunity report for review or integration planning.</div>", unsafe_allow_html=True)

    else:
        st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#facc15; margin-bottom:0.75rem;'>Automation Gap Analysis</h4>", unsafe_allow_html=True)
        st.markdown(
            "<div style='line-height:1.7;'>"
            f"<strong>Gap Description:</strong> {gap_analysis.get('gap_description', 'N/A')}<br>"
            f"<strong>Risk Level:</strong> {gap_analysis.get('risk_level', 'N/A')}<br>"
            f"<strong>Business Impact:</strong> {gap_analysis.get('business_impact', 'N/A')}<br>"
            f"<strong>Recommended Automation:</strong> {gap_analysis.get('recommended_automation', 'N/A')}"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#facc15; margin-bottom:0.75rem;'>Export Recommendation</h4>", unsafe_allow_html=True)
        st.markdown("<div class='small-note'>No opportunity report is available because no integration path was detected. Update your requirement or discovered systems and try again.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Enter a business requirement and click Analyze to generate automation opportunities.")
    if not GEMINI_API_KEY:
        st.warning("Gemini API key is required for Automation Analyzer. Add GEMINI_API_KEY to your .env file.")
