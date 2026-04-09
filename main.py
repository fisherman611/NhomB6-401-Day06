import os
import json
from pathlib import Path
from dotenv import load_dotenv

from src.engine.llm_service import LLMService
from src.agents.cv_analyzer import CVAnalyzer
from src.agents.jd_analyzer import JDAnalyzer
from src.agents.candidate_deep_analyzer import CandidateDeepAnalyzer
from src.agents.interview_question_generator import InterviewQuestionGenerator
from src.utils import rank_candidates

# Load environment variables (API Keys, etc.)
load_dotenv()

def main():
    print("🚀 --- SMART CV-JD MATCHING & INTERVIEW SELECTION PIPELINE --- 🚀\n")
    
    # 0. KHỞI TẠO SERVICES & AGENTS
    llm = LLMService(temperature=0.1)
    cv_agent = CVAnalyzer(llm_service=llm)
    jd_agent = JDAnalyzer(llm_service=llm)
    deep_agent = CandidateDeepAnalyzer(llm_service=llm)
    question_agent = InterviewQuestionGenerator(llm_service=llm)
    
    # Cấu hình đường đẫn
    cv_input_dir = Path("data/data_cv")
    jd_input_file = Path("data/data_jd/jd_ai_01.txt") # Giả định chọn 1 JD mẫu
    db_path = "data/interview_question_db.json"
    top_n_to_select = 3

    # 1. PHÂN TÍCH JD
    print(f"Step 1: Analyzing JD ({jd_input_file.name})...")
    if not jd_input_file.exists():
        print(f"[Error] JD file not found at {jd_input_file}")
        return
    jd_text = jd_input_file.read_text(encoding="utf-8")
    jd_analysis = jd_agent.analyze(jd_text)
    
    # 2. PHÂN TÍCH HÀNG LOẠT CV
    print(f"Step 2: Analyzing all CVs in {cv_input_dir}...")
    if not cv_input_dir.exists():
        print(f"[Error] CV directory not found at {cv_input_dir}")
        return
        
    analyzed_candidates = []
    cv_files = list(cv_input_dir.glob("*.txt"))
    
    for cv_file in cv_files:
        print(f"  - Analyzing candidate: {cv_file.name}")
        cv_text = cv_file.read_text(encoding="utf-8")
        cv_analysis = cv_agent.analyze(cv_text)
        
        # Lưu kết quả phân tích tạm thời để chuẩn bị cho bước ranking
        analyzed_candidates.append({
            "file_name": cv_file.name,
            "cv_analysis": cv_analysis
        })
    
    # 3. MATCHING & RANKING
    print(f"\nStep 3: Matching & Ranking candidates for position: {jd_analysis.get('job_title')}...")
    # Sử dụng hàm rank_candidates từ utils (Matching dựa trên keyword)
    ranked_candidates = rank_candidates(analyzed_candidates, jd_analysis)
    
    # Chọn Top-N
    top_n = ranked_candidates[:top_n_to_select]
    print(f"  - Selected Top {len(top_n)} candidates based on matching score.")
    for i, c in enumerate(top_n):
        print(f"    {i+1}. {c['cv_analysis'].get('full_name')} - Score: {c['matching_score']}%")

    # 4. DEEP ANALYSIS & INTERVIEW GENERATION (Chỉ thực hiện cho Top-N)
    print("\nStep 4: Deep Analysis & Generating Interview Questions for Top Candidates...")
    final_output = []
    
    for candidate in top_n:
        candidate_name = candidate['cv_analysis'].get('full_name')
        print(f"  - Processing: {candidate_name}...")
        
        # Phân tích sâu điểm mạnh/điểm yếu đối chiếu với JD
        deep_analysis = deep_agent.analyze(candidate['cv_analysis'], jd_analysis)
        
        # Gen bộ câu hỏi phỏng vấn tối ưu từ DB nội bộ
        interview_questions = question_agent.generate_questions(
            target_position=jd_analysis.get('job_title', "Candidate"),
            strengths=deep_analysis.get('strengths', ""),
            weaknesses=deep_analysis.get('weaknesses', ""),
            db_path=db_path
        )
        
        final_output.append({
            "name": candidate_name,
            "matching_score": candidate["matching_score"],
            "analysis": deep_analysis,
            "interview_questions": interview_questions
        })

    # 5. KẾT THÚC & HIỂN THỊ KẾT QUẢ CƠ BẢN
    print("\n" + "="*50)
    print("✅ PIPELINE EXECUTION COMPLETED!")
    print("="*50)
    
    for res in final_output:
        print(f"\nCANDIDATE: {res['name']} ({res['matching_score']}%)")
        print(f"  - Summary: Một trong {top_n_to_select} ứng viên tiềm năng nhất.")
        # print(f"  - Questions generated: {res['interview_questions']}") # In ra toàn bộ nếu cần

    # (Tùy chọn) Lưu kết quả cuối cùng ra file JSON
    output_path = Path("data/final_pipeline_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(final_output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[Info] Full results saved to: {output_path}")

if __name__ == "__main__":
    main()
