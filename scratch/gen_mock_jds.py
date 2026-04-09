import os

data_dir = "data/data_jd"
os.makedirs(data_dir, exist_ok=True)

jds = [
    {
        "filename": "jd_ai_01.txt",
        "content": """Vị trí: Giảng viên Cao cấp Trí tuệ Nhân tạo (Senior AI Instructor)

Mô tả công việc:
Chúng tôi đang tìm kiếm một Giảng viên Cao cấp đam mê và giàu kinh nghiệm để dẫn dắt các khóa học về AI và Machine Learning.

Trách nhiệm chính:
- Thiết kế và giảng dạy các chương trình đào tạo chuyên sâu về AI, Deep Learning và Reinforcement Learning.
- Hướng dẫn sinh viên thực hiện các dự án nghiên cứu và đồ án tốt nghiệp trong lĩnh vực thị giác máy tính.
- Cập nhật giáo trình thường xuyên để phản ánh những tiến bộ mới nhất trong ngành công nghiệp AI.
- Tham gia các hoạt động nghiên cứu khoa học và công bố bài báo quốc tế.
- Cố vấn cho các nhóm khởi nghiệp công nghệ trong trường.

Yêu cầu ứng viên:
- Trình độ: Tiến sĩ chuyên ngành AI, Computer Science hoặc các lĩnh vực liên quan.
- Ít nhất 5 năm kinh nghiệm làm việc hoặc nghiên cứu trong lĩnh vực AI (Senior level).
- Kỹ năng bắt buộc: Python, PyTorch/TensorFlow, Kiến thức chuyên sâu về CNN/RNN/Transformers.
- Có khả năng đọc hiểu tài liệu tiếng Anh chuyên ngành tốt.

Ưu tiên:
- Có kinh nghiệm triển khai dự án AI thực tế trong doanh nghiệp.
- Kỹ năng sư phạm tốt và khả năng truyền cảm hứng.
- Đã có các công bố trên các hội nghị/tạp chí uy tín (NIPS, ICML, CVPR)."""
    },
    {
        "filename": "jd_ai_02.txt",
        "content": """Tuyển dụng Giảng viên AI & Machine Learning

Vị trí: Giảng viên (Lecturer)

Nhiệm vụ:
- Giảng dạy các môn học cơ sở về Machine Learning và Xử lý ngôn ngữ tự nhiên (NLP).
- Xây dựng hệ thống bài tập thực hành trên nền tảng Cloud (AWS/GCP).
- Tổ chức các buổi workshop chia sẻ kiến thức về AI cho sinh viên và cộng đồng.

Yêu cầu:
- Tốt nghiệp Thạc sĩ trở lên chuyên ngành CNTT hoặc Toán tin.
- Có kinh nghiệm làm việc với các thư viện Scikit-learn, Keras, HuggingFace.
- Cấp độ: Junior/Middle (Tối thiểu 2 năm kinh nghiệm).
- Có chứng chỉ về AI/Data Science từ các tổ chức uy tín là một điểm cộng.

Kỹ năng ưu tiên:
- Biết sử dụng Docker và Kubernetes.
- Có kinh nghiệm về MLOps.
- Kỹ năng giao tiếp và trình bày xuất sắc."""
    },
    {
        "filename": "jd_ai_03.txt",
        "content": """Giảng viên Chuyên gia về Thị giác Máy tính (Computer Vision Specialist)

Mô tả:
Vị trí này tập trung vào đào tạo các kỹ sư AI chuyên biệt về lĩnh vực Computer Vision.

Trách nhiệm:
- Giảng dạy chuyên đề Image Processing, Object Detection, và Generative AI (Stable Diffusion/GANs).
- Phát triển các bộ dữ liệu mẫu phục vụ giảng dạy.
- Kết nối doanh nghiệp để tạo cơ hội thực tập cho sinh viên.

Yêu cầu bắt buộc:
- Kinh nghiệm 3+ năm trong lĩnh vực Thị giác máy tính.
- Thành thạo OpenCV, C++ hoặc Python.
- Hiểu biết sâu về các kiến trúc YOLO, ResNet, ViT.
- Kinh nghiệm giảng dạy là một lợi thế lớn.

Kinh nghiệm: Middle.
Kỹ năng ưu tiên: Tiếng Anh IELTS 6.5+, có kinh nghiệm làm các dự án Edge AI."""
    },
    {
        "filename": "jd_cs_01.txt",
        "content": """Vị trí: Giảng viên Khoa học Máy tính (Core CS Lecturer)

Mô tả:
Giảng dạy các môn học nền tảng của ngành Khoa học máy tính.

Trách nhiệm:
- Giảng dạy Cấu trúc dữ liệu và Giải thuật, Hệ điều hành, và Kiến trúc máy tính.
- Soạn thảo và chấm thi các kỳ thi học thuật cấp trường.
- Hỗ trợ xây dựng khung chương trình đào tạo đạt chuẩn kiểm định quốc tế.

Yêu cầu:
- Trình độ: Thạc sĩ/Tiến sĩ Khoa học máy tính.
- Nắm vững các nguyên lý khoa học máy tính cơ bản.
- Kỹ năng lập trình tốt với C/C++ và Java.
- Kinh nghiệm: Senior (Tối thiểu 4 năm giảng dạy).

Ưu tiên:
- Có kinh nghiệm làm việc tại các công ty phần mềm lớn.
- Biết về Parallel Computing hoặc Distributed Systems."""
    },
    {
        "filename": "jd_cs_02.txt",
        "content": """Giảng viên Kỹ thuật Phần mềm (Software Engineering Instructor)

Nhiệm vụ:
- Đào tạo về quy trình phát triển phần mềm (Agile/Scrum), Design Patterns và Microservices.
- Giám sát các đồ án thực tế của sinh viên theo mô hình dự án thực thụ.
- Phối hợp với phòng quan hệ doanh nghiệp để cập nhật xu hướng công nghệ.

Yêu cầu:
- 3 năm kinh nghiệm trong vai trò Senior Software Engineer hoặc Tech Lead.
- Thành thạo ít nhất một framework (Spring Boot, .NET Core, React).
- Hiểu biết về CI/CD và Unit Testing.
- Kinh nghiệm: Middle/Senior.

 Ưu tiên:
- Có chứng chỉ Scrum Master hoặc Cloud Architect.
- Khả năng giảng dạy bằng tiếng Anh."""
    },
    {
        "filename": "jd_cs_03.txt",
        "content": """Giảng viên An toàn thông tin và Mạng máy tính

Công việc chính:
- Giảng dạy các khóa học về Network Security, Cryptography và Ethical Hacking.
- Quản lý phòng lab thực hành mạng của khoa.
- Tư vấn về bảo mật cho các hệ thống nội bộ của trường.

Yêu cầu:
- Có các chứng chỉ bảo mật uy tín như CEH, CISSP hoặc CCNP Security.
- Hiểu biết về lỗ hổng OWASP và Pentesting.
- Kỹ năng xử lý sự cố mạng tốt.
- Kinh nghiệm: 2-3 năm (Middle).

Kỹ năng ưu tiên:
- Từng tham gia các giải đấu CTF.
- Có kinh nghiệm về Cloud Security (Azure/Google Cloud)."""
    },
    {
        "filename": "jd_cs_04.txt",
        "content": """Lecturer in Computer Science (International Program)

Location: Hanoi/HCMC.
Role: Delivering CS curriculum in English to international students.

Key Responsibilities:
- Teach Database Management Systems, Web Development, and Software Requirements.
- Mentor students in English-speaking environments.
- Coordinate with partner universities abroad.

Requirements:
- Master's degree in CS from an English-speaking country.
- High English proficiency (IELTS 7.5 or equivalent).
- Strong coding skills in JavaScript/TypeScript and SQL.
- Experience Level: Junior/Middle.

Preferred:
- Experience with modern web stacks (MERN/Next.js).
- Familiarity with international accreditation standards like ABET."""
    },
    {
        "filename": "jd_math_01.txt",
        "content": """Vị trí: Giảng viên Toán ứng dụng (Applied Mathematics Lecturer)

Mô tả:
Giảng dạy Toán học phục vụ cho các ngành kỹ thuật và công nghệ.

Trách nhiệm:
- Giảng dạy Giải tích, Đại số tuyến tính và Lý thuyết đồ thị.
- Phát triển các ví dụ ứng dụng toán học trong lập trình và tối ưu hóa.
- Tham gia nghiên cứu trong các nhóm chuyên môn của Viện Toán.

Yêu cầu:
- Tốt nghiệp Tiến sĩ chuyên ngành Toán học hoặc Toán ứng dụng.
- Khả năng tư duy logic và trừu tượng cực tốt.
- Thành thạo các công cụ Matlab hoặc Mathematica.
- Kinh nghiệm: Senior.

Kỹ năng ưu tiên:
- Biết lập trình Python hoặc R để minh họa toán học.
- Có niềm đam mê với việc ứng dụng toán vào giải quyết các vấn đề thực tế."""
    },
    {
        "filename": "jd_math_02.txt",
        "content": """Giảng viên Toán cho AI và Khoa học Dữ liệu

Nhiệm vụ:
- Đào tạo kiến thức Toán nền tảng cho AI: Đại số tuyến tính cho ML, Xác suất cho DS và Tối ưu hóa.
- Xây dựng bài tập thực hành toán học bằng Python.
- Hướng dẫn sinh viên hiểu bản chất thuật toán qua các công thức toán học.

Yêu cầu:
- Thạc sĩ Toán tin hoặc Thống kê.
- Hiểu biết sâu về Linear Algebra, Calculus, và Optimization.
- Kỹ năng lập trình cơ bản với Python (NumPy, Scipy).
- Cấp độ: Middle.

Ưu tiên:
- Đã từng làm các dự án Data Science thực tế.
- Khả năng đơn giản hóa các khái niệm toán học phức tạp cho sinh viên CNTT."""
    },
    {
        "filename": "jd_math_03.txt",
        "content": """Giảng viên Xác suất Thống kê và Phân tích Dữ liệu

Nhiệm vụ trọng tâm:
- Giảng dạy Xác suất Thống kê, Quy hoạch tuyến tính và Phân tích dữ liệu đa biến.
- Hỗ trợ sinh viên sử dụng phần mềm thống kê (SPSS/R).
- Biên soạn tài liệu học tập và ngân hàng câu hỏi trắc nghiệm.

Yêu cầu bắt buộc:
- Tốt nghiệp chuyên ngành Thống kê hoặc Toán kinh tế.
- Thành thạo ngôn ngữ R hoặc phần mềm SPSS.
- Có kỹ năng sư phạm và phương pháp giảng dạy hiện đại.
- Kinh nghiệm: 1-2 năm (Junior/Early Middle).

Kỹ năng ưu tiên:
- Có kiến thức về Big Data Analytics.
- Tiếng Anh tốt là một lợi thế."""
    }
]

for jd in jds:
    file_path = os.path.join(data_dir, jd["filename"])
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(jd["content"])
    print(f"Created {file_path}")
