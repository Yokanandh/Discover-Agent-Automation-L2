"""
app.py
Discovery Agent – AI-Powered Enterprise System Discovery
Main Streamlit application entry point.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from extractors import (
    extract_from_pdf,
    extract_from_image,
    extract_from_excel,
    extract_from_text,
)
from agents import detect_systems
from utils import (
    merge_texts,
    systems_to_dataframe,
    systems_to_json_str,
    systems_to_csv_bytes,
    compute_kpis,
    confidence_color,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Discovery Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load environment variables ────────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', 'Space Grotesk', sans-serif;
        background: #090909;
        color: #f8f8f2;
        line-height: 1.6;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
        letter-spacing: -0.02em;
    }

    .main-header {
        background: linear-gradient(135deg, #0b0b0b 0%, #151515 55%, #111111 100%);
        border-radius: 22px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(250, 204, 21, 0.24);
        box-shadow: 0 20px 60px rgba(250, 204, 21, 0.12);
    }
    .main-header h1 {
        color: #ffec99;
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
        text-shadow: 0 0 30px rgba(250, 204, 21, 0.3), 0 0 60px rgba(250, 204, 21, 0.15);
        font-family: 'Playfair Display', serif;
        line-height: 1.1;
    }
    .main-header p {
        color: #d6d3d1;
        font-size: 1.05rem;
        margin: 1rem 0 0 0;
        opacity: 0.88;
        font-weight: 400;
        letter-spacing: 0.4px;
        font-family: 'Poppins', sans-serif;
    }
    .main-header span {
        color: #facc15;
        font-weight: 700;
    }

    .kpi-card {
        background: #111111;
        border-radius: 18px;
        padding: 1.6rem 1.8rem;
        border: 1px solid rgba(250, 204, 21, 0.18);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 18px 40px rgba(250, 204, 21, 0.14);
    }
    .kpi-value {
        font-size: 2.6rem;
        font-weight: 800;
        color: #facc15;
        line-height: 1;
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.5px;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #d6d3d1;
        margin-top: 0.6rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-family: 'Space Grotesk', sans-serif;
    }
    .kpi-high  { color: #fb7185; }
    .kpi-med   { color: #fde047; }
    .kpi-low   { color: #34d399; }
    .kpi-conf  { color: #60a5fa; }

    .conf-badge {
        display: inline-block;
        border-radius: 999px;
        padding: 0.4rem 1rem;
        font-weight: 700;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        background: rgba(250, 204, 21, 0.14);
        color: #facc15;
        letter-spacing: 0.3px;
    }

    .section-heading {
        color: #fff8d1;
        font-size: 1.35rem;
        font-weight: 700;
        margin: 2rem 0 1.1rem 0;
        padding-bottom: 0.7rem;
        border-bottom: 2.5px solid rgba(250, 204, 21, 0.35);
        font-family: 'Playfair Display', serif;
        letter-spacing: -0.5px;
    }

    .status-ok {
        background: rgba(250, 204, 21, 0.12);
        color: #facc15;
        border: 1px solid rgba(250, 204, 21, 0.35);
        border-radius: 10px;
        padding: 7px 15px;
        font-size: 0.85rem;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
    }
    .status-err {
        background: rgba(248, 113, 113, 0.12);
        color: #f87171;
        border: 1px solid rgba(248, 113, 113, 0.35);
        border-radius: 10px;
        padding: 7px 15px;
        font-size: 0.85rem;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
    }

    .stButton > button {
        background: linear-gradient(135deg, #fde047 0%, #fbbf24 100%);
        color: #0f172a;
        border: none;
        border-radius: 14px;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.85rem 2rem;
        width: 100%;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        font-family: 'Poppins', sans-serif;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 30px rgba(250, 204, 21, 0.18);
    }

    .stDownloadButton > button {
        border-radius: 14px;
        font-weight: 700;
        background: #111111;
        color: #facc15;
        border: 1px solid rgba(250, 204, 21, 0.35);
        font-family: 'Poppins', sans-serif;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
    }

    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.06);
        font-family: 'Poppins', sans-serif;
    }
    .stDataFrame th {
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        color: #facc15;
    }
    .stDataFrame td {
        font-weight: 500;
        font-size: 0.9rem;
    }

    div[data-testid="stExpander"] {
        background: #131313;
        border: 1px solid rgba(250, 204, 21, 0.2);
        border-radius: 16px;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 700;
        font-size: 1rem;
        color: #fff8d1;
        font-family: 'Poppins', sans-serif;
        letter-spacing: 0.2px;
    }

    .stTextInput > div > input {
        background: #111111;
        border: 1px solid rgba(250, 204, 21, 0.15);
        color: #f8f8f2;
        border-radius: 12px;
        font-family: 'Poppins', sans-serif;
        font-size: 0.95rem;
        font-weight: 500;
    }
    .stTextInput > div > input::placeholder {
        color: #888888;
        font-weight: 400;
    }
    
    .stSelectbox > div {
        background: #111111;
        border: 1px solid rgba(250, 204, 21, 0.15);
        border-radius: 12px;
    }
    .stSelectbox select {
        color: #f8f8f2;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }

    .stTextInput > div > input:focus,
    .stSelectbox > div:focus {
        outline: 1px solid rgba(250, 204, 21, 0.5);
    }

    section[data-testid="stSidebar"] {
        background: #080808;
        border-right: 1px solid #1f1f1f;
        font-family: 'Poppins', sans-serif;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #f8f8f2;
    }
    section[data-testid="stSidebar"] h2 {
        font-size: 1.2rem;
        font-weight: 800;
        color: #facc15;
        letter-spacing: -0.3px;
        font-family: 'Playfair Display', serif;
    }
    section[data-testid="stSidebar"] h3 {
        font-size: 1rem;
        font-weight: 700;
        color: #fff8d1;
        font-family: 'Poppins', sans-serif;
        letter-spacing: 0.2px;
    }

    .stApp {
        background: radial-gradient(circle at top left, rgba(250, 204, 21, 0.12), transparent 28%),
                    radial-gradient(circle at bottom right, rgba(255, 255, 255, 0.05), transparent 25%),
                    #090909;
    }

    .stCaption {
        font-size: 0.88rem;
        color: #999999;
        font-weight: 500;
        font-family: 'Poppins', sans-serif;
        letter-spacing: 0.2px;
    }

    .stMetricLabel {
        font-weight: 700;
        font-size: 0.9rem;
        color: #d6d3d1;
        letter-spacing: 0.3px;
    }

    /* Icon hover scaling effects */
    .icon-scale {
        display: inline-block;
        transition: transform 0.3s ease, filter 0.3s ease;
        cursor: pointer;
    }
    .icon-scale:hover {
        transform: scale(1.25);
        filter: drop-shadow(0 0 12px rgba(250, 204, 21, 0.4));
    }

    /* KPI card icon hover */
    .kpi-card div:first-child {
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.3s ease;
    }
    .kpi-card:hover div:first-child {
        transform: scale(1.3) rotate(5deg);
        filter: drop-shadow(0 0 15px rgba(250, 204, 21, 0.5));
    }

    /* Section heading icon hover */
    .section-heading span {
        display: inline-block;
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.3s ease;
    }
    .section-heading:hover span {
        transform: scale(1.25);
        filter: drop-shadow(0 0 12px rgba(250, 204, 21, 0.4));
    }

    /* File upload icon hover */
    div[class*="file"] span, 
    div[class*="upload"] span {
        transition: transform 0.3s ease;
    }
    div[class*="file"]:hover span,
    div[class*="upload"]:hover span {
        transform: scale(1.2);
    }

    /* General emoji/icon hover */
    span[class*="icon"],
    div[class*="icon"] {
        transition: transform 0.3s ease, filter 0.3s ease;
    }
    span[class*="icon"]:hover,
    div[class*="icon"]:hover {
        transform: scale(1.2);
        filter: drop-shadow(0 0 10px rgba(250, 204, 21, 0.3));
    }

    /* Badge icon hover */
    .status-ok, .status-err {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .status-ok:hover, .status-err:hover {
        transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1><span class="icon-scale">🔍</span> Discovery Agent</h1>
        <p>AI-Powered Enterprise System Discovery &nbsp;·&nbsp; Powered by Google Gemini</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── Session state ─────────────────────────────────────────────────────────────
if "systems" not in st.session_state:
    st.session_state.systems = []
if "extraction_done" not in st.session_state:
    st.session_state.extraction_done = False


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## <span class='icon-scale'>🔍</span> Discovery Agent", unsafe_allow_html=True)
    st.markdown("---")

    # Gemini status
    st.markdown("### <span class='icon-scale'>🤖</span> Gemini Status", unsafe_allow_html=True)
    if GEMINI_API_KEY:
        st.markdown('<span class="status-ok">✅ API Key Loaded</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-err">❌ API Key Missing</span>', unsafe_allow_html=True)
        st.info("Add GEMINI_API_KEY to your .env file.")

    st.markdown("---")

    # File uploader
    st.markdown("### <span class='icon-scale'>📂</span> Upload Documents", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drag and drop files here",
        type=["pdf", "txt", "png", "jpg", "jpeg", "xlsx"],
        accept_multiple_files=True,
        help="Supported: PDF, TXT, PNG, JPG, JPEG, XLSX",
    )

    st.markdown("---")

    # Statistics
    if st.session_state.systems:
        kpis = compute_kpis(st.session_state.systems)
        st.markdown("### <span class='icon-scale'>📊</span> Session Stats", unsafe_allow_html=True)
        st.metric("Total Systems", kpis["total"])
        st.metric("Needs Review", kpis["needs_review"])
        st.metric("Avg Confidence", f"{kpis['avg_confidence']}%")

    st.markdown("---")
    st.markdown(
        "<small style='color:#475569;'>Discovery Agent v1.0 · Aivar Challenge</small>",
        unsafe_allow_html=True,
    )


# ── Main area ─────────────────────────────────────────────────────────────────
if not GEMINI_API_KEY:
    st.warning(
        "⚠️ **Gemini API key not found.** "
        "Create a `.env` file with `GEMINI_API_KEY=your_key_here` and restart the app."
    )

# ── Uploaded files preview ────────────────────────────────────────────────────
if uploaded_files:
    st.markdown('<p class="section-heading"><span class="icon-scale">📄</span> Uploaded Files</p>', unsafe_allow_html=True)
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, uf in enumerate(uploaded_files):
        with cols[idx % 4]:
            ext = uf.name.split(".")[-1].upper()
            size_kb = round(uf.size / 1024, 1)
            icon_map = {
                "PDF": "📕", "TXT": "📝", "XLSX": "📊",
                "PNG": "🖼️", "JPG": "🖼️", "JPEG": "🖼️",
            }
            icon = icon_map.get(ext, "📄")
            st.markdown(
                f"""
                <div class="kpi-card" style="text-align:left; padding:0.9rem 1rem;">
                    <div style="font-size:1.5rem; display:inline-block; transition: transform 0.3s ease;">{icon}</div>
                    <div style="color:#e2e8f0; font-weight:600; margin-top:0.3rem;
                                font-size:0.85rem; word-break:break-all;">{uf.name}</div>
                    <div style="color:#64748b; font-size:0.75rem;">{ext} · {size_kb} KB</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Analyse button ─────────────────────────────────────────────────────────
    col_btn, col_spacer = st.columns([2, 5])
    with col_btn:
        analyse_clicked = st.button("🚀 Analyse Documents", use_container_width=True)

    if analyse_clicked:
        if not GEMINI_API_KEY:
            st.error("❌ Cannot analyse without a valid Gemini API key.")
        else:
            # ── Text extraction ────────────────────────────────────────────────
            extracted_chunks = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, uf in enumerate(uploaded_files):
                status_text.text(f"Extracting text from: {uf.name} ...")
                ext = uf.name.rsplit(".", 1)[-1].lower()
                chunk = None

                if ext == "pdf":
                    chunk = extract_from_pdf(uf)
                elif ext in ("png", "jpg", "jpeg"):
                    chunk = extract_from_image(uf)
                elif ext == "xlsx":
                    chunk = extract_from_excel(uf)
                elif ext == "txt":
                    chunk = extract_from_text(uf)
                else:
                    st.warning(f"⚠️ Unsupported file type: {uf.name}")

                if chunk:
                    extracted_chunks.append(f"[Source: {uf.name}]\n{chunk}")

                progress_bar.progress((i + 1) / len(uploaded_files))

            status_text.empty()
            progress_bar.empty()

            if not extracted_chunks:
                st.error("❌ No text could be extracted from the uploaded files.")
            else:
                combined_text = merge_texts(extracted_chunks)
                st.success(
                    f"✅ Extracted text from {len(extracted_chunks)} file(s). "
                    f"Total context: {len(combined_text):,} characters."
                )

                # ── Gemini analysis ────────────────────────────────────────────
                systems = detect_systems(extracted_text=combined_text, api_key=GEMINI_API_KEY)

                if systems is not None:
                    st.session_state.systems = systems
                    st.session_state.extraction_done = True
                    if systems:
                        st.success(f"🎉 Discovered **{len(systems)}** software systems!")
                    else:
                        st.info("ℹ️ No software systems were found in the documents.")


# ── Results section ───────────────────────────────────────────────────────────
if st.session_state.extraction_done and st.session_state.systems:
    systems = st.session_state.systems
    kpis = compute_kpis(systems)

    # ── KPI Dashboard ──────────────────────────────────────────────────────────
    st.markdown('<p class="section-heading"><span class="icon-scale">📊</span> Discovery Dashboard</p>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    cards = [
        (k1, kpis["total"], "TOTAL SYSTEMS", "kpi-conf", "🔍"),
        (k2, kpis["high"],  "HIGH CRITICAL",  "kpi-high", "🔴"),
        (k3, kpis["medium"],"MED CRITICAL",   "kpi-med",  "🟡"),
        (k4, kpis["low"],   "LOW CRITICAL",   "kpi-low",  "🟢"),
        (k5, f"{kpis['avg_confidence']}%", "AVG CONFIDENCE", "kpi-conf", "📈"),
    ]
    for col, val, label, css_cls, icon in cards:
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div style="font-size:1.4rem; display:inline-block; transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.3s ease;">{icon}</div>
                    <div class="kpi-value {css_cls}">{val}</div>
                    <div class="kpi-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters ────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-heading"><span class="icon-scale">🔎</span> Filter & Search</p>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([3, 2, 2])

    with f1:
        search_query = st.text_input("🔍 Search by system name", placeholder="e.g. Salesforce")
    with f2:
        categories = ["All"] + sorted(set(s.get("category", "Other") for s in systems))
        cat_filter = st.selectbox("Filter by Category", categories)
    with f3:
        crit_filter = st.selectbox("Filter by Criticality", ["All", "High", "Medium", "Low"])

    # Apply filters
    filtered = systems
    if search_query:
        filtered = [s for s in filtered if search_query.lower() in s.get("system_name", "").lower()]
    if cat_filter != "All":
        filtered = [s for s in filtered if s.get("category") == cat_filter]
    if crit_filter != "All":
        filtered = [s for s in filtered if s.get("criticality") == crit_filter]

    st.caption(f"Showing {len(filtered)} of {len(systems)} systems")

    # ── Results table ──────────────────────────────────────────────────────────
    st.markdown('<p class="section-heading"><span class="icon-scale">📋</span> Systems Inventory</p>', unsafe_allow_html=True)

    if filtered:
        df = systems_to_dataframe(filtered)

        # Color-code confidence scores
        def style_confidence(val):
            try:
                score = int(val)
                color = confidence_color(score)
                return f"color: {color}; font-weight: bold;"
            except (ValueError, TypeError):
                return ""

        def style_criticality(val):
            if val == "High":
                return "color: #f87171; font-weight: 600;"
            elif val == "Medium":
                return "color: #fbbf24; font-weight: 600;"
            return "color: #34d399; font-weight: 600;"

        styled_df = df.style.map(
            style_confidence, subset=["Confidence Score"]
        ).map(
            style_criticality, subset=["Criticality"]
        )

        st.dataframe(styled_df, use_container_width=True, height=400)

        # ── JSON viewer ────────────────────────────────────────────────────────
        st.markdown('<p class="section-heading"><span class="icon-scale">🧾</span> JSON Output</p>', unsafe_allow_html=True)
        with st.expander("View raw JSON", expanded=False):
            st.json(filtered)

        # ── Download buttons ───────────────────────────────────────────────────
        st.markdown('<p class="section-heading"><span class="icon-scale">⬇️</span> Download Results</p>', unsafe_allow_html=True)
        dl1, dl2, dl3 = st.columns([2, 2, 4])

        with dl1:
            st.download_button(
                label="📥 Download JSON",
                data=systems_to_json_str(filtered),
                file_name="discovery_results.json",
                mime="application/json",
                use_container_width=True,
            )
        with dl2:
            st.download_button(
                label="📥 Download CSV",
                data=systems_to_csv_bytes(filtered),
                file_name="discovery_results.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.info("No systems match your current filters.")

elif st.session_state.extraction_done and not st.session_state.systems:
    st.info("ℹ️ The analysis is complete but no software systems were detected in the uploaded documents.")

elif not uploaded_files:
    # Empty state
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align:center; padding: 4rem 2rem; color:#475569;">
            <div style="font-size:4rem">📂</div>
            <h3 style="color:#64748b; margin-top:1rem;">Upload Documents to Begin</h3>
            <p>Supported formats: PDF, TXT, XLSX, PNG, JPG, JPEG</p>
            <p style="font-size:0.85rem;">The agent will identify every software system, tool, and platform mentioned in your documents.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
