import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.agents.cv_analyzer import CVAnalyzer


def main():
    parser = argparse.ArgumentParser(description="Batch test CVAnalyzer with CV text files")
    parser.add_argument("--input-dir", default="data/data_cv", help="Folder chứa CV .txt")
    parser.add_argument("--output-dir", default="data/cv_analysis_results", help="Folder lưu JSON kết quả")
    parser.add_argument("--pattern", default="*.txt", help="Pattern file CV")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        print(f"[ERROR] Input folder không tồn tại: {input_dir}")
        sys.exit(1)

    cv_files = sorted(input_dir.glob(args.pattern))
    if not cv_files:
        print(f"[ERROR] Không tìm thấy file nào theo pattern {args.pattern} trong {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    analyzer = CVAnalyzer()

    ok = 0
    fail = 0

    print(f"[INFO] Tổng số CV: {len(cv_files)}")
    for cv_file in cv_files:
        try:
            cv_text = cv_file.read_text(encoding="utf-8")
            result = analyzer.analyze(cv_text)

            out_file = output_dir / f"{cv_file.stem}.json"
            out_file.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            print(f"[OK] {cv_file.name} -> {out_file}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {cv_file.name}: {e}")
            fail += 1

    print("\n===== SUMMARY =====")
    print(f"Success: {ok}")
    print(f"Failed : {fail}")
    print(f"Output : {output_dir}")


if __name__ == "__main__":
    main()