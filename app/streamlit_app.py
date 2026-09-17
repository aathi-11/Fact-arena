import sys
import os
import json
import streamlit as st

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph.debate_graph import get_debate_graph
from src.config import MAX_DEBATE_ROUNDS, JUDGE_MODEL, DEBATER_MODEL

# ---------------------------------------------------------
# Page Config & Custom Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Veritas Agents - AI Fact Checker",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-aesthetic Light Theme CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Clean Light Theme Background */
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        color: #0f172a;
    }

    /* Custom Header Hero Container */
    .hero-container {
        text-align: center;
        padding: 2.2rem 1rem 1.4rem 1rem;
        background: #ffffff;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        color: #0284c7;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 50%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
        line-height: 1.15;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #475569;
        max-width: 700px;
        margin: 0 auto;
        font-weight: 400;
        line-height: 1.6;
    }

    /* Input Box Styling */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 12px !important;
        color: #0f172a !important;
        font-size: 1.05rem !important;
        padding: 0.8rem 1.2rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.25s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #0284c7 !important;
        box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.15) !important;
    }

    /* Primary Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 0.75rem 1.8rem !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(2, 132, 199, 0.4) !important;
    }

    /* Sub-claim Pills */
    .subclaim-pill {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        color: #1e293b;
        padding: 8px 18px;
        border-radius: 9999px;
        font-size: 0.95rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin: 4px 8px 6px 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }

    /* Light Theme Stance Cards */
    .pro-card {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-left: 5px solid #10b981;
        border-radius: 14px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);
        color: #064e3b;
    }

    .con-card {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 5px solid #ef4444;
        border-radius: 14px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.08);
        color: #7f1d1d;
    }

    .stance-header-pro {
        color: #047857;
        font-weight: 700;
        font-size: 1.05rem;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.6rem;
    }

    .stance-header-con {
        color: #b91c1c;
        font-weight: 700;
        font-size: 1.05rem;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.6rem;
    }

    /* Light Theme Verdict Card */
    .verdict-card {
        background: #ffffff;
        border-radius: 18px;
        border: 1px solid #e2e8f0;
        padding: 1.8rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
    }

    .verdict-badge-true {
        background: #10b981;
        color: #ffffff;
        padding: 8px 22px;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 1.25rem;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    .verdict-badge-false {
        background: #ef4444;
        color: #ffffff;
        padding: 8px 22px;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 1.25rem;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    .verdict-badge-unverifiable {
        background: #f59e0b;
        color: #ffffff;
        padding: 8px 22px;
        border-radius: 9999px;
        font-weight: 800;
        font-size: 1.25rem;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    /* Sidebar Light Customization */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Pre-configured Benchmark Scenarios
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric/100/scales.png", width=65)
st.sidebar.title("Veritas Agents")
st.sidebar.markdown("<span style='color: #64748b; font-size: 0.9rem;'>Multi-Agent Adversarial Fact Checker</span>", unsafe_allow_html=True)

benchmark_claims = {
    "Select a benchmark preset...": "",
    "1. Clear False": "The Great Wall of China is visible from space with the naked eye.",
    "2. Clear True": "Regular exercise reduces the risk of cardiovascular disease.",
    "3. Genuinely Ambiguous": "Moderate coffee consumption increases the risk of heart disease.",
    "4. Misleading Statistic": "Global average temperature increase of 1.5C has no impact on extreme weather events.",
    "5. Time-Sensitive": "Global lithium ion battery production volume doubled in the past 24 months."
}

selected_preset = st.sidebar.selectbox("🎯 Quick Benchmark Preset", list(benchmark_claims.keys()))
default_input = benchmark_claims[selected_preset] if selected_preset and benchmark_claims[selected_preset] else ""

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Engine Parameters")

rounds_mode = st.sidebar.radio(
    "Debate Round Mode:",
    ["1 Round (Fast ~3s)", "2 Rounds (Balanced)", "3 Rounds (Deep Debate)", "Custom Number"],
    index=0
)

if rounds_mode == "1 Round (Fast ~3s)":
    rounds_input = 1
elif rounds_mode == "2 Rounds (Balanced)":
    rounds_input = 2
elif rounds_mode == "3 Rounds (Deep Debate)":
    rounds_input = 3
else:
    rounds_input = st.sidebar.number_input("Custom Rounds (1-5)", min_value=1, max_value=5, value=1, step=1)

st.sidebar.markdown(f"""
- ⚡ **Debater Model**: `{DEBATER_MODEL}`
- 🏛️ **Judge Model**: `{JUDGE_MODEL}`
- 🌐 **Live Search**: Tavily Advanced + DDGS
- 🛡️ **Guardrail**: Active Grounding Verification
""")

st.sidebar.divider()
st.sidebar.info("💡 **Cost & Speed Architecture**: Fast LPU models generate adversarial turns; 120B model handles judicial synthesis.")

# ---------------------------------------------------------
# Main UI Layout
# ---------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">✨ Autonomous Fact-Checking Graph</div>
    <div class="hero-title">⚖️ Veritas Agents</div>
    <div class="hero-subtitle">
        Multi-Agent Adversarial Debate System — Decomposes complex claims, executes parallel live web retrieval, and synthesizes calibrated judicial verdicts.
    </div>
</div>
""", unsafe_allow_html=True)

claim_input = st.text_input(
    "Ask your question or claim to verify:",
    value=default_input,
    placeholder="Ask your question or claim here..."
)

col_btn1, col_btn2 = st.columns([1.2, 3.8])
with col_btn1:
    run_button = st.button("🚀 Execute Fact Check", type="primary", use_container_width=True)

if run_button and claim_input.strip():
    # Stream real-time progress using st.status
    status_container = st.status("🚀 Initializing Multi-Agent Graph...", expanded=True)
    
    graph = get_debate_graph()
    initial_state = {
        "claim": claim_input.strip(),
        "sub_claims": [],
        "round": 1,
        "max_rounds": rounds_input,
        "pro_turns": [],
        "con_turns": [],
        "evidence_pool": {},
        "verdict": None,
        "latency_log": {}
    }
    
    final_state = dict(initial_state)
    
    for step in graph.stream(initial_state):
        node_name = list(step.keys())[0]
        node_output = step[node_name]
        
        for k, v in node_output.items():
            final_state[k] = v
            
        if node_name == "normalize":
            status_container.write(f"🧩 **Claim Decomposed**: {len(final_state.get('sub_claims', []))} atomic sub-claims")
        elif node_name == "pro_turn":
            cur_r = final_state.get("round", 1)
            status_container.write(f"🟢 **Pro Agent Round {cur_r}**: Retrieved 100% real web evidence & generated supporting argument")
        elif node_name == "con_turn":
            cur_r = final_state.get("round", 1)
            status_container.write(f"🔴 **Con Agent Round {cur_r}**: Retrieved 100% real web evidence & generated refuting argument")
        elif node_name == "advance_round":
            status_container.write(f"🔄 **Advancing to Round {final_state.get('round', 1)}**")
        elif node_name == "judge":
            status_container.write("🏛️ **Supreme Judge**: Verification guardrail passed & verdict rendered!")

    status_container.update(label="✅ Fact Check Execution Complete!", state="complete", expanded=False)
    
    debate_result = final_state

    # ---------------------------------------------------------
    # 1. Atomic Sub-Claims Section
    # ---------------------------------------------------------
    st.markdown("### 🧩 Decomposed Sub-Claims")
    sub_claims = debate_result.get("sub_claims", [])
    if sub_claims:
        sub_html = "".join([f'<span class="subclaim-pill">🔹 {sc}</span>' for sc in sub_claims])
        st.markdown(sub_html, unsafe_allow_html=True)
    st.divider()

    # ---------------------------------------------------------
    # 2. Side-by-Side Debate Transcript
    # ---------------------------------------------------------
    st.markdown("### ⚔️ Adversarial Debate Transcript")
    
    pro_turns = debate_result.get("pro_turns", [])
    con_turns = debate_result.get("con_turns", [])
    evidence_pool = debate_result.get("evidence_pool", {})

    max_r = max([t.get("round", 1) for t in pro_turns + con_turns] or [1])
    
    for r in range(1, max_r + 1):
        st.markdown(f"#### 🔔 Debate Round {r}")
        col_pro, col_con = st.columns(2)
        
        # Pro Turn
        with col_pro:
            r_pro = [t for t in pro_turns if t.get("round") == r]
            if r_pro:
                pt = r_pro[0]
                st.markdown(f'''
                <div class="pro-card">
                    <div class="stance-header-pro">🟢 PRO AGENT (Supporting Stance)</div>
                    <div>{pt.get("argument")}</div>
                </div>
                ''', unsafe_allow_html=True)
                cited = pt.get("cited_evidence_ids", [])
                if cited:
                    with st.expander(f"📚 Cited Sources ({len(cited)})"):
                        for cid in cited:
                            ev = evidence_pool.get(cid)
                            if ev:
                                st.markdown(f"**[{cid}] [{ev['title']}]({ev['url']})**")
                                st.caption(f'"{ev["snippet"]}"')
                            else:
                                st.warning(f"[{cid}] (Unresolved Evidence ID)")
        
        # Con Turn
        with col_con:
            r_con = [t for t in con_turns if t.get("round") == r]
            if r_con:
                ct = r_con[0]
                st.markdown(f'''
                <div class="con-card">
                    <div class="stance-header-con">🔴 CON AGENT (Refuting Stance)</div>
                    <div>{ct.get("argument")}</div>
                </div>
                ''', unsafe_allow_html=True)
                cited = ct.get("cited_evidence_ids", [])
                if cited:
                    with st.expander(f"📚 Cited Sources ({len(cited)})"):
                        for cid in cited:
                            ev = evidence_pool.get(cid)
                            if ev:
                                st.markdown(f"**[{cid}] [{ev['title']}]({ev['url']})**")
                                st.caption(f'"{ev["snippet"]}"')
                            else:
                                st.warning(f"[{cid}] (Unresolved Evidence ID)")

    st.divider()

    # ---------------------------------------------------------
    # 3. Judicial Verdict Card
    # ---------------------------------------------------------
    st.markdown("### 🏛️ Supreme Judicial Verdict")
    verdict_data = debate_result.get("verdict") or {}
    verdict_str = str(verdict_data.get("verdict", "unverifiable")).lower()
    confidence = verdict_data.get("confidence", 50)
    rationale = verdict_data.get("rationale", "")
    uncertainty_note = verdict_data.get("uncertainty_note")
    guardrail_report = verdict_data.get("guardrail_report", {})

    badge_class = f"verdict-badge-{verdict_str}" if verdict_str in ["true", "false", "unverifiable"] else "verdict-badge-unverifiable"
    
    st.markdown(f"""
    <div class="verdict-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
            <div>
                <span style="font-size: 0.85rem; color: #64748b; font-weight: 700; letter-spacing: 1px;">VERDICT LABEL</span><br/>
                <span class="{badge_class}">{verdict_str.upper()}</span>
            </div>
            <div style="text-align: right; width: 45%;">
                <span style="font-size: 0.85rem; color: #64748b; font-weight: 700; letter-spacing: 1px;">CALIBRATED CONFIDENCE: {confidence}%</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.progress(confidence / 100.0)
    
    st.markdown(f"<div style='margin-top: 1rem; color: #1e293b; line-height: 1.7;'><strong>Judicial Rationale:</strong><br/>{rationale}</div>", unsafe_allow_html=True)
    
    if uncertainty_note:
        st.warning(f"⚠️ **Uncertainty & Ambiguity Note:** {uncertainty_note}")
        
    if guardrail_report and not guardrail_report.get("is_clean"):
        st.error(f"🛡️ **Guardrail Report:** {guardrail_report.get('warning_summary')}")
        
    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 4. Execution Metrics & Latency
    # ---------------------------------------------------------
    with st.expander("⚡ Execution Latency & Model Tiering Summary"):
        lat = debate_result.get("latency_log") or {}
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Normalize Claim", f"{lat.get('normalize_seconds', 0)}s")
        c2.metric("Pro Turns Total", f"{sum(lat.get('pro_turns_seconds', [])):.2f}s")
        c3.metric("Con Turns Total", f"{sum(lat.get('con_turns_seconds', [])):.2f}s")
        c4.metric("Supreme Judge", f"{lat.get('judge_seconds', 0)}s")
        st.caption(f"Total Execution Time: **{lat.get('total_seconds', 0)} seconds** across {len(evidence_pool)} retrieved real web sources.")
