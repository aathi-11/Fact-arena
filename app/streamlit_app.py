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
    page_title="Veritas Agents - Multi-Agent Fact Checker",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    /* Dark glassmorphism container styles */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
        margin-bottom: 1.5rem;
    }
    .verdict-card {
        padding: 1.8rem;
        border-radius: 16px;
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 2rem;
    }
    .verdict-badge-true {
        background-color: #059669;
        color: #ecfdf5;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.2rem;
        display: inline-block;
    }
    .verdict-badge-false {
        background-color: #dc2626;
        color: #fef2f2;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.2rem;
        display: inline-block;
    }
    .verdict-badge-unverifiable {
        background-color: #d97706;
        color: #fffbeb;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.2rem;
        display: inline-block;
    }
    .pro-card {
        background: rgba(6, 78, 59, 0.3);
        border-left: 4px solid #10b981;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .con-card {
        background: rgba(127, 29, 29, 0.3);
        border-left: 4px solid #ef4444;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .subclaim-pill {
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(129, 140, 248, 0.4);
        color: #e0e7ff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 4px 6px 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Pre-configured Benchmark Scenarios
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric/100/scales.png", width=70)
st.sidebar.title("Veritas Agents")
st.sidebar.markdown("**Multi-Agent Debate & Fact-Checking Framework**")

benchmark_claims = {
    "Select a pre-set claim...": "",
    "1. Clear False": "The Great Wall of China is visible from space with the naked eye.",
    "2. Clear True": "Regular exercise reduces the risk of cardiovascular disease.",
    "3. Genuinely Ambiguous": "Moderate coffee consumption increases the risk of heart disease.",
    "4. Misleading Statistic": "Global average temperature increase of 1.5C has no impact on extreme weather events.",
    "5. Time-Sensitive": "Global lithium ion battery production volume doubled in the past 24 months."
}

selected_preset = st.sidebar.selectbox("🎯 Quick-Select Benchmark Scenario", list(benchmark_claims.keys()))
default_input = benchmark_claims[selected_preset] if selected_preset and benchmark_claims[selected_preset] else ""

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Engine Parameters")

# Number input + quick dropdown for debate rounds
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
- **Active Rounds**: `{rounds_input}`
- **Judge Model**: `{JUDGE_MODEL}`
- **Debater Model**: `{DEBATER_MODEL}`
- **Search Engine**: Tavily Live Web API
- **Guardrail**: Strict Evidence Grounding
""")

st.sidebar.divider()
st.sidebar.info("💡 **Cost & Speed Architecture**: Fast LPU models generate adversarial turns; 70B/120B model handles judicial synthesis.")

# ---------------------------------------------------------
# Main UI Layout
# ---------------------------------------------------------
st.markdown('<div class="main-header"><div class="main-title">⚖️ Veritas Agents</div><div class="sub-title">Autonomous Multi-Agent Fact-Checking System (Claim → Pro ⇄ Con → Supreme Judge)</div></div>', unsafe_allow_html=True)

claim_input = st.text_input(
    "Ask your question or claim to verify:",
    value=default_input,
    placeholder="Ask your question or claim here..."
)

col_btn1, col_btn2 = st.columns([1, 4])
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
        
        # Merge updated state keys
        for k, v in node_output.items():
            final_state[k] = v
            
        if node_name == "normalize":
            status_container.write(f"🧩 **Claim Decomposed**: {len(final_state.get('sub_claims', []))} atomic sub-claims")
        elif node_name == "pro_turn":
            cur_r = final_state.get("round", 1)
            status_container.write(f"🟢 **Pro Agent Round {cur_r}**: Retrieved live web evidence & generated supporting argument")
        elif node_name == "con_turn":
            cur_r = final_state.get("round", 1)
            status_container.write(f"🔴 **Con Agent Round {cur_r}**: Retrieved live web evidence & generated refuting argument")
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
        st.markdown(f"#### 🔔 Round {r}")
        col_pro, col_con = st.columns(2)
        
        # Pro Turn
        with col_pro:
            st.markdown(f"**🟢 PRO Agent (Supporting Stance)**")
            r_pro = [t for t in pro_turns if t.get("round") == r]
            if r_pro:
                pt = r_pro[0]
                st.markdown(f'<div class="pro-card">{pt.get("argument")}</div>', unsafe_allow_html=True)
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
            st.markdown(f"**🔴 CON Agent (Refuting Stance)**")
            r_con = [t for t in con_turns if t.get("round") == r]
            if r_con:
                ct = r_con[0]
                st.markdown(f'<div class="con-card">{ct.get("argument")}</div>', unsafe_allow_html=True)
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
    st.markdown("### 🏛️ Final Judicial Verdict")
    verdict_data = debate_result.get("verdict") or {}
    verdict_str = str(verdict_data.get("verdict", "unverifiable")).lower()
    confidence = verdict_data.get("confidence", 50)
    rationale = verdict_data.get("rationale", "")
    uncertainty_note = verdict_data.get("uncertainty_note")
    guardrail_report = verdict_data.get("guardrail_report", {})

    badge_class = f"verdict-badge-{verdict_str}" if verdict_str in ["true", "false", "unverifiable"] else "verdict-badge-unverifiable"
    
    st.markdown(f"""
    <div class="verdict-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <span style="font-size: 0.9rem; color: #94a3b8; font-weight: 600;">VERDICT LABEL</span><br/>
                <span class="{badge_class}">{verdict_str.upper()}</span>
            </div>
            <div style="text-align: right; width: 40%;">
                <span style="font-size: 0.9rem; color: #94a3b8; font-weight: 600;">CALIBRATED CONFIDENCE: {confidence}%</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.progress(confidence / 100.0)
    
    st.markdown(f"**Judicial Rationale:**\n\n{rationale}")
    
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
        c4.metric("Supreme Judge (70B/120B)", f"{lat.get('judge_seconds', 0)}s")
        st.caption(f"Total Execution Time: **{lat.get('total_seconds', 0)} seconds** across {len(evidence_pool)} retrieved web sources.")
