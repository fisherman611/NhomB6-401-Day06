# Smart CV-JD Matching

Hệ thống AI hỗ trợ tuyển dụng theo hướng augmentation: tự động phân tích JD và CV, chấm điểm matching, xếp hạng ứng viên, phân tích sâu điểm mạnh/yếu và sinh câu hỏi phỏng vấn phù hợp.

## 1. Muc tieu du an

- Giam thoi gian screening CV cho HR.
- Tang do nhat quan trong viec danh gia ung vien theo JD.
- Ho tro chuan bi bo cau hoi phong van co dinh huong theo tung ung vien.

## 2. Tinh nang chinh

- Phan tich JD thanh du lieu cau truc (job title, required/preferred skills, summary...).
- Phan tich CV thanh du lieu cau truc (ho ten, kinh nghiem, technical skills, summary...).
- Tinh diem matching theo thuat toan ket hop keyword + fuzzy + semantic summary.
- Xep hang ung vien va chon Top-N.
- Deep analysis cho Top-N de tim strengths/weaknesses so voi JD.
- Sinh bo cau hoi phong van dua tren deep analysis va database noi bo.
- Demo UI bang Streamlit va pipeline CLI end-to-end.

## 3. Kien truc tong quan

Pipeline gom 5 buoc:

1. Analyze JD
2. Analyze batch CV
3. Matching + Ranking
4. Deep Analysis cho Top-N
5. Interview Question Generation

Thanh phan chinh:

- LLM service: [src/engine/llm_service.py](src/engine/llm_service.py)
- CV analyzer: [src/agents/cv_analyzer.py](src/agents/cv_analyzer.py)
- JD analyzer: [src/agents/jd_analyzer.py](src/agents/jd_analyzer.py)
- Deep analyzer: [src/agents/candidate_deep_analyzer.py](src/agents/candidate_deep_analyzer.py)
- Interview question generator: [src/agents/interview_question_generator.py](src/agents/interview_question_generator.py)
- Matching utility: [src/utils.py](src/utils.py)
- CLI pipeline: [main.py](main.py)
- Streamlit UI: [ui/app.py](ui/app.py)

## 4. Cau truc thu muc quan trong

- Du lieu dau vao CV: [data/data_cv](data/data_cv)
- Du lieu dau vao JD: [data/data_jd](data/data_jd)
- Ket qua pipeline tong: [data/final_pipeline_results.json](data/final_pipeline_results.json)
- Ket qua test theo tung buoc:
	- [data/cv_analysis_results](data/cv_analysis_results)
	- [data/jd_analysis_results](data/jd_analysis_results)
	- [data/deep_analysis_results](data/deep_analysis_results)
	- [data/interview_questions](data/interview_questions)
- DB cau hoi phong van: [data/interview_question_db.json](data/interview_question_db.json)

## 5. Yeu cau moi truong

- Python 3.10+ (khuyen nghi 3.11)
- API key cho NVIDIA OpenAI-compatible endpoint

## 6. Cai dat nhanh

```bash
git clone https://github.com/fisherman611/NhomB6-401-Day06.git
cd NhomB6-401-Day06
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 7. Cau hinh bien moi truong

1. Tao file .env tu mau [.env.example](.env.example)
2. Dien gia tri thuc te:

```env
NVIDIA_API_KEY=your_key
NVIDIA_BASE_URL=your_base_url
DATABASE_PATH=data/interview_question_db.json
TOP_N=3
```

Luu y: Pipeline hien tai doc truc tiep tham so trong code va UI; DATABASE_PATH/TOP_N trong .env co the duoc dung de mo rong ve sau.

## 8. Chay ung dung

### 8.1 Chay pipeline CLI

```bash
python main.py
```

Ket qua tong hop duoc luu tai [data/final_pipeline_results.json](data/final_pipeline_results.json).

### 8.2 Chay giao dien Streamlit

```bash
streamlit run ui/app.py
```

Flow tren UI:

1. Upload 1 file JD (.txt)
2. Upload nhieu file CV (.txt)
3. Chon Top-N o sidebar
4. Nhan nut chay pipeline
5. Xem ranking, deep analysis va interview questions

## 9. Chay test theo tung module

Du an hien co cac test script batch (khong phai full unit test suite). Chay tu thu muc goc du an.

### CV Analyzer

```bash
python test/test_cv_analyzer.py \
	--input-dir data/data_cv \
	--output-dir data/cv_analysis_results
```

### JD Analyzer

```bash
python test/test_jd_analyzer.py \
	--input-dir data/data_jd \
	--output-dir data/jd_analysis_results
```

### Candidate Deep Analyzer

```bash
python test/test_candidate_deep_analyzer.py \
	--cv-dir data/cv_analysis_results \
	--jd-file data/jd_analysis_results/jd_ai_01.json \
	--output-dir data/deep_analysis_results
```

### Interview Question Generator

```bash
python test/test_interview_question_generator.py \
	--input-dir data/deep_analysis_results \
	--output-dir data/interview_questions \
	--db-path data/interview_question_db.json \
	--pos "Giang vien Tri tue Nhan tao"
```

## 10. Cong nghe su dung

- Python
- OpenAI Python SDK (goi NVIDIA OpenAI-compatible endpoint)
- Pydantic
- Streamlit
- python-dotenv
- pandas

## 11. Han che hien tai

- Chua co bo metric danh gia chat luong matching/deep analysis co ground truth.
- Chua co feedback loop tu thao tac HR de tu dong cai tien scoring.
- Error handling batch tren UI co the cai tien them de skip tung CV loi thay vi dung toan bo process.

## 12. Tai lieu lien quan

- Prototype summary + phan cong: [GROUP_REPORT/prototype-readme.md](GROUP_REPORT/prototype-readme.md)
- SPEC hackathon: [GROUP_REPORT/SPEC_final.md](GROUP_REPORT/SPEC_final.md)

## 13. Team

- Nguyen Nhu Giap
- Luong Huu Thanh
- Vu Nhu Duc
- Nguyen Tien Thang
- Hoang Van Bac
- Tran Anh Tu
- Vu Phuc Thanh