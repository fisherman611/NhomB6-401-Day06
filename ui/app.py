import streamlit as st
import json
import os
import sys
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
from src.utils import calculate_matching_score

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
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    .candidate-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #4CAF50;
    }
    .score-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        float: right;
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = None

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
    st.title("Settings")
    top_n = st.slider("Select Top-N for Deep Analysis", 1, 10, 3)
    db_path = st.text_input("Interview DB Path", "data/interview_question_db.json")
    st.divider()
    st.info("💡 Project hỗ trợ nhà tuyển dụng lọc CV và chuẩn bị phỏng vấn tự động.")

# --- MAIN UI ---
st.title("🎯 Smart CV-JD Matching System")
st.markdown("### Giải pháp tuyển dụng AI hỗ trợ Hackathon")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Bước 1: Job Description (JD)")
    jd_file = st.file_uploader("Upload JD (.txt)", type=["txt"])
    if jd_file:
        jd_text = jd_file.read().decode("utf-8")
        st.text_area("Nội dung JD preview", jd_text, height=150)

with col2:
    st.subheader("📄 Bước 2: Curricula Vitae (CVs)")
    cv_files = st.file_uploader("Upload multiple CVs (.txt)", type=["txt"], accept_multiple_files=True)
    if cv_files:
        st.write(f"Đã chọn {len(cv_files)} hồ sơ ứng viên.")

# --- PROCESSING ---
if st.button("🚀 Bắt đầu Matching & Ranking"):
    if not jd_file or not cv_files:
        st.error("Vui lòng tải lên cả JD và ít nhất một CV!")
    else:
        with st.status("Đang xử lý dữ liệu..."):
            # 1. Analyze JD
            st.write("Đang phân tích JD...")
            jd_analysis = jd_agent.analyze(jd_text)
            
            # 2. Analyze all CVs
            all_candidates = []
            progress_bar = st.progress(0)
            for idx, cv_file in enumerate(cv_files):
                st.write(f"Đang phân tích CV: {cv_file.name}")
                cv_text = cv_file.read().decode("utf-8")
                cv_analysis = cv_agent.analyze(cv_text)
                
                score = calculate_matching_score(cv_analysis, jd_analysis)
                
                all_candidates.append({
                    "name": cv_analysis.get("full_name", cv_file.name),
                    "analysis": cv_analysis,
                    "score": score
                })
                progress_bar.progress((idx + 1) / len(cv_files))
            
            # 3. Rank entries
            all_candidates.sort(key=lambda x: x["score"], reverse=True)
            
            # 4. Deep Analysis for Top-N
            st.write(f"Đang thực hiện phân tích sâu cho Top {top_n}...")
            results = []
            for i, candidate in enumerate(all_candidates[:top_n]):
                deep_res = deep_agent.analyze(candidate["analysis"], jd_analysis)
                
                # Generate Questions
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
            st.success("Hoàn tất xử lý!")

# --- DISPLAY RESULTS ---
if st.session_state.processed_results:
    res = st.session_state.processed_results
    
    st.divider()
    st.subheader(f"📊 Kết quả xếp hạng cho vị trí: {res['jd'].get('job_title')}")
    
    # Dashboard summary
    m1, m2, m3 = st.columns(3)
    m1.metric("Tổng số ứng viên", len(res['all_ranks']))
    m2.metric("Điểm cao nhất", f"{res['all_ranks'][0]['score']}%")
    m3.metric("Số lượng Top-N đã chọn", len(res['top_results']))

    # Tabs for different views
    tab1, tab2 = st.tabs(["🏆 Top-N Chi tiết", "📂 Bảng xếp hạng tổng quát"])
    
    with tab1:
        for idx, candidate in enumerate(res['top_results']):
            with st.container():
                st.markdown(f"""
                <div class="candidate-card">
                    <span class="score-badge">Score: {candidate['score']}%</span>
                    <h3>#{idx+1} {candidate['name']}</h3>
                    <p><b>Summary:</b> {candidate['analysis'].get('summary', 'No summary available.')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.success("🟢 **Điểm mạnh**")
                    st.write(candidate['deep_analysis'].get('strengths', 'Đang cập nhật...'))
                with col_b:
                    st.warning("🟡 **Điểm yếu / Khoảng cách**")
                    st.write(candidate['deep_analysis'].get('weaknesses', 'Đang cập nhật...'))
                
                with st.expander("📝 Xem bộ câu hỏi phỏng vấn đề xuất"):
                    # Questions are in JSON string format from the agent (List of objects)
                    if isinstance(candidate['questions'], dict) and "questions" in candidate['questions']:
                        for q in candidate['questions']['questions']:
                            st.write(f"❓ **{q.get('content')}**")
                            st.caption(f"*Mục tiêu:* {q.get('goal')}")
                            st.divider()
                    else:
                        st.write(candidate['questions']) # Fallback display
                st.write("")

    with tab2:
        st.dataframe(
            res['all_ranks'],
            column_config={
                "name": "Họ và Tên",
                "score": st.column_config.NumberColumn("Matching Score", format="%d%%"),
                "analysis": None # Ẩn cột raw json
            },
            hide_index=True,
            use_container_width=True
        )

st.divider()
st.caption("Developed by team Hackathon | Optimized by Google Gemini Model")
