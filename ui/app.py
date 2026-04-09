import streamlit as st
import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Thêm project root vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.llm_service import LLMService
from src.agents.cv_analyzer import CVAnalyzer
from src.agents.jd_analyzer import JDAnalyzer
from src.agents.candidate_deep_analyzer import CandidateDeepAnalyzer
from src.agents.interview_question_generator import InterviewQuestionGenerator
from src.utils import calculate_matching_score_v2 

load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Smart CV-JD Matcher",
    page_icon="🎯",
    layout="wide",
)

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');
    
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    .candidate-card {
        background-color: #1a1f2e;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        margin-bottom: 25px;
        border: 1px solid #2d3748;
        border-left: 6px solid #3b82f6;
    }
    .score-badge {
        background: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        padding: 6px 16px;
        border-radius: 30px;
        font-weight: 700;
        border: 1px solid #3b82f6;
        float: right;
    }
    .log-window {
        background-color: #0d1117;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
    }
    .log-line {
        font-family: 'Fira Code', monospace;
        font-size: 13px;
        line-height: 1.6;
        margin-bottom: 4px;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .log-time { color: #8b949e; margin-right: 10px; }
    .log-msg-info { color: #58a6ff; }
    .log-msg-success { color: #3fb950; font-weight: bold; }
    .log-msg-warn { color: #d29922; }
    .log-msg-error { color: #f85149; font-weight: bold; }
    
    /* Hiệu ứng nhấp nháy cho con trỏ */
    .cursor {
        display: inline-block;
        width: 8px;
        height: 15px;
        background: #58a6ff;
        margin-left: 5px;
        animation: blink 1s infinite;
    }
    @keyframes blink { 
        0%, 100% { opacity: 1; } 
        50% { opacity: 0; } 
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = None
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(message, type="info"):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append({"time": timestamp, "msg": message, "type": type})
    if len(st.session_state.logs) > 100:
        st.session_state.logs.pop(0)

def render_logs(placeholder):
    log_html = '<div class="log-window">'
    for log in st.session_state.logs:
        cls = f"log-msg-{log['type']}"
        log_html += f'<div class="log-line"><span class="log-time">[{log["time"]}]</span><span class="{cls}">{log["msg"]}</span></div>'
    log_html += '<div class="cursor"></div></div>'
    placeholder.markdown(log_html, unsafe_allow_html=True)

# --- INITIALIZE AGENTS ---
@st.cache_resource
def get_agents():
    llm = LLMService(temperature=0.1)
    return (
        CVAnalyzer(llm_service=llm),
        JDAnalyzer(llm_service=llm),
        CandidateDeepAnalyzer(llm_service=llm),
        InterviewQuestionGenerator(llm_service=llm)
    )

cv_agent, jd_agent, deep_agent, question_agent = get_agents()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/000000/resume.png", width=100)
    st.title("Control Panel")
    top_n = st.slider("Select Top-N for Analysis", 1, 10, 3)
    db_path = st.text_input("Interview DB Path", "data/interview_question_db.json")
    if st.button("Clear Logs & Cache"):
        st.session_state.processed_results = None
        st.session_state.logs = []
        st.cache_resource.clear()
        st.rerun()
    st.divider()
    st.info("💡 Project hỗ trợ nhà tuyển dụng lọc CV và chuẩn bị phỏng vấn tự động.")

# --- MAIN UI ---
st.title("🎯 Smart CV-JD Matching System")
st.markdown("##### AI-Powered Recruitment Pipeline for Hackathons")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Bước 1: Job Description (JD)")
    jd_file = st.file_uploader("Upload 1 file JD (.txt)", type=["txt"], accept_multiple_files=False)
    if jd_file:
        jd_text = jd_file.read().decode("utf-8")
        st.info("JD đã được tải lên thành công.")

with col2:
    st.subheader("📄 Bước 2: Curricula Vitae (CVs)")
    cv_files = st.file_uploader("Upload danh sách CVs (.txt)", type=["txt"], accept_multiple_files=True)
    if cv_files:
        st.write(f"Đã chọn {len(cv_files)} hồ sơ ứng viên.")

# --- PROCESSING ---
if st.button("🚀 Bắt đầu Matching & Ranking"):
    if not jd_file or not cv_files:
        st.error("Vui lòng tải lên đúng 1 JD và ít nhất một CV!")
    else:
        st.session_state.logs = []
        st.divider()
        st.subheader("⚙️ System Pipeline Stream")
        log_placeholder = st.empty()
        
        try:
            # 1. Analyze JD
            add_log("Initializing JD Analysis Agent...", "info")
            render_logs(log_placeholder)
            
            jd_analysis = jd_agent.analyze(jd_text)
            add_log(f"Successfully processed JD: {jd_analysis.get('job_title')}", "success")
            render_logs(log_placeholder)
            
            # 2. Analyze all CVs
            add_log(f"Starting batch analysis for {len(cv_files)} candidates...", "info")
            render_logs(log_placeholder)
            
            all_candidates = []
            progress_bar = st.progress(0)
            
            for idx, cv_file in enumerate(cv_files):
                add_log(f"Scanning CV: {cv_file.name}", "info")
                render_logs(log_placeholder)
                
                cv_text = cv_file.read().decode("utf-8")
                cv_analysis = cv_agent.analyze(cv_text)
                
                score = calculate_matching_score_v2(cv_analysis, jd_analysis)
                add_log(f"  > Match Score for {cv_analysis.get('full_name', 'N/A')}: {score}%", "warn")
                render_logs(log_placeholder)
                
                all_candidates.append({
                    "name": cv_analysis.get("full_name", cv_file.name),
                    "analysis": cv_analysis,
                    "score": score,
                    "file_name": cv_file.name
                })
                progress_bar.progress((idx + 1) / len(cv_files))
            
            # 3. Rank entries
            add_log("Finalizing Ranking based on Semantic & Keyword scores...", "info")
            render_logs(log_placeholder)
            all_candidates.sort(key=lambda x: x["score"], reverse=True)
            
            # 4. Deep Analysis for Top-N
            add_log(f"Performing Deep Insight Analysis for Top {top_n} profiles...", "info")
            render_logs(log_placeholder)
            
            results = []
            for i, candidate in enumerate(all_candidates[:top_n]):
                add_log(f"Analyzing Gap/Strength for: {candidate['name']}", "info")
                render_logs(log_placeholder)
                
                deep_res = deep_agent.analyze(candidate["analysis"], jd_analysis)
                
                add_log(f"Generating custom interview strategy for: {candidate['name']}", "info")
                render_logs(log_placeholder)
                
                questions = question_agent.generate_questions(
                    target_position=jd_analysis.get("job_title", "Position"),
                    strengths=deep_res.get("strengths", ""),
                    weaknesses=deep_res.get("weaknesses", ""),
                    db_path=db_path
                )
                
                results.append({
                    **candidate,
                    "deep_analysis": deep_res,
                    "questions": questions
                })
            
            st.session_state.processed_results = {
                "top_results": results,
                "all_ranks": all_candidates,
                "jd": jd_analysis
            }
            add_log("⚡ Pipeline execution finished. Displaying insights...", "success")
            render_logs(log_placeholder)
            time.sleep(1) # Chờ 1 chút để xem log cuối
            st.rerun()
            
        except Exception as e:
            add_log(f"FATAL ERROR: {str(e)}", "error")
            render_logs(log_placeholder)
            st.error(f"Error: {e}")

# --- DISPLAY RESULTS ---
if st.session_state.processed_results:
    res = st.session_state.processed_results
    
    st.divider()
    st.subheader(f"📊 Market Insights: {res['jd'].get('job_title')}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Candidates Processed", len(res['all_ranks']))
    m2.metric("Highest Compatibility", f"{res['all_ranks'][0]['score']}%")
    m3.metric("Deep Analysis Count", len(res['top_results']))

    tab1, tab2 = st.tabs(["🏆 Elite Candidates (Deep Insight)", "📂 Comprehensive Ranking"])
    
    with tab1:
        for idx, candidate in enumerate(res['top_results']):
            with st.container():
                st.markdown(f"""
                <div class="candidate-card">
                    <span class="score-badge">{candidate['score']}% Match</span>
                    <h3 style="color: #60a5fa;">#{idx+1} {candidate['name']}</h3>
                    <p style="color: #94a3b8; font-style: italic;">{candidate['analysis'].get('summary', 'Profiling in progress...')}</p>
                    <hr style="border: 0.5px solid #2d3748; margin: 15px 0;">
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.success("🎯 **Key Strengths**")
                    st.write(candidate['deep_analysis'].get('strengths', 'N/A'))
                with col_b:
                    st.warning("🚧 **Critical Gaps**")
                    st.write(candidate['deep_analysis'].get('weaknesses', 'N/A'))
                
                with st.expander("🔍 Strategic Interview Questions"):
                    if isinstance(candidate['questions'], dict) and "questions" in candidate['questions']:
                        for q in candidate['questions']['questions']:
                            st.markdown(f"**Question:** {q.get('content')}")
                            st.info(f"**Target Goal:** {q.get('goal')}")
                            st.divider()
                    else:
                        st.write(candidate['questions'])
                st.write("")

    with tab2:
        table_data = []
        for c in res['all_ranks']:
            table_data.append({
                "Rank": res['all_ranks'].index(c) + 1,
                "Candidate": c['name'],
                "Compatibility": f"{c['score']}%",
                "Exp (Yrs)": c['analysis'].get('years_of_experience', 0),
                "Education": c['analysis'].get('education', 'N/A')
            })
        st.table(table_data)

st.divider()
st.caption("Developed by team Hackathon | Supercharged by Deep Learning & LLMs")
