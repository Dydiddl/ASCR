import os
from pathlib import Path
from src.converter.extract_PDF_pages import extract_pages_interactive
from src.classifier.pdf_processor import PDFProcessor
from src.utils.pdf_merger import merge_chapter_pdfs
from src.utils.pdf_to_lookup_table import PDFToLookupTable

# 설정 모듈 import
try:
    from config.settings import (
        INPUT_DIR, 
        OUTPUT_DIR, 
        ensure_directories, 
        get_input_files,
        print_settings_info,
        check_environment
    )
except ImportError:
    # 설정 모듈이 없는 경우 기본 경로 사용
    INPUT_DIR = Path("input")
    OUTPUT_DIR = Path("output")
    
    def ensure_directories():
        INPUT_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)
    
    def get_input_files(extension=".pdf"):
        return list(INPUT_DIR.glob(f"*{extension}"))
    
    def print_settings_info():
        print("설정 모듈을 사용할 수 없습니다.")
    
    def check_environment():
        return {"basic_mode": True}

def process_auto_classification():
    """자동 분류 기능을 실행합니다."""
    print("\n=== PDF 자동 분류 시작 ===")
    
    # 환경 확인
    print("환경 확인 중...")
    ensure_directories()
    environment_checks = check_environment()
    
    # 환경 문제가 있는지 확인
    failed_checks = [name for name, status in environment_checks.items() if not status]
    if failed_checks:
        print(f"경고: 다음 환경 설정에 문제가 있습니다: {failed_checks}")
    
    print("이 기능은 다음과 같이 동작합니다:")
    print("1. 표지는 '표지.pdf'로 저장됩니다.")
    print("2. 각 장은 해당 부문 폴더 아래에 저장됩니다.")
    print("3. 빈 페이지는 자동으로 건너뜁니다.")
    print("4. 같은 장의 PDF 파일들은 자동으로 병합됩니다.")
    print("\n")
    
    # 입력 PDF 파일 경로 받기
    input_pdf = input("분류할 PDF 파일의 경로를 입력하세요: ").strip()
    
    # 상대 경로인 경우 입력 디렉토리 기준으로 처리
    if not os.path.isabs(input_pdf):
        input_pdf = str(INPUT_DIR / input_pdf)
    
    if not os.path.exists(input_pdf):
        print(f"오류: 파일을 찾을 수 없습니다: {input_pdf}")
        print(f"입력 디렉토리: {INPUT_DIR}")
        
        # 입력 디렉토리의 PDF 파일 목록 표시
        pdf_files = get_input_files()
        if pdf_files:
            print("사용 가능한 PDF 파일들:")
            for i, file in enumerate(pdf_files, 1):
                print(f"  {i}. {file.name}")
        return
        
    try:
        # PDF 처리 시작
        processor = PDFProcessor()
        processor.process_pdf(input_pdf)
        
        # PDF 파일 병합
        merge_chapter_pdfs()
        
        print("\n=== PDF 분류가 완료되었습니다 ===")
        print(f"결과물은 {OUTPUT_DIR} 디렉토리에 저장되었습니다.")
        
    except Exception as e:
        print(f"\n오류가 발생했습니다: {str(e)}")

def show_project_info():
    """프로젝트 정보를 표시합니다."""
    print("\n=== 프로젝트 정보 ===")
    print_settings_info()
    
    # 입력 파일 목록
    pdf_files = get_input_files()
    if pdf_files:
        print(f"\n입력 디렉토리의 PDF 파일 ({len(pdf_files)}개):")
        for file in pdf_files:
            print(f"  - {file.name}")
    else:
        print("\n입력 디렉토리에 PDF 파일이 없습니다.")

def convert_debug_to_lookup_table():
    """PDF 디버그 파일을 룩업테이블로 변환하는 기능을 실행합니다."""
    print("\n=== PDF 디버그 파일을 룩업테이블로 변환 ===")
    
    # output 폴더의 디버그 파일 목록 확인
    output_dir = Path("output")
    if not output_dir.exists():
        print("output 폴더가 존재하지 않습니다.")
        return
    
    debug_files = list(output_dir.glob("pdf_debug_*.txt"))
    if not debug_files:
        print("output 폴더에 PDF 디버그 파일이 없습니다.")
        print("먼저 PDF 디버그 파일을 생성해주세요.")
        return
    
    print("사용 가능한 디버그 파일:")
    for i, debug_file in enumerate(debug_files, 1):
        print(f"  {i}. {debug_file.name}")
    
    try:
        choice = int(input(f"\n변환할 디버그 파일을 선택하세요 (1-{len(debug_files)}): ")) - 1
        if 0 <= choice < len(debug_files):
            debug_file_path = str(debug_files[choice])
            print(f"\n선택된 파일: {debug_file_path}")
            
            # 룩업테이블 생성
            converter = PDFToLookupTable()
            output_path = converter.process_debug_file(debug_file_path)
            print(f"\n룩업테이블이 성공적으로 생성되었습니다: {output_path}")
        else:
            print("잘못된 선택입니다.")
    except ValueError:
        print("숫자를 입력해주세요.")
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

def convert_lookup_table_to_config():
    """룩업테이블을 매핑 설정으로 변환하는 기능을 실행합니다."""
    print("\n=== 룩업테이블을 매핑 설정으로 변환 ===")
    
    # output 폴더의 룩업테이블 파일 목록 확인
    output_dir = Path("output")
    if not output_dir.exists():
        print("output 폴더가 존재하지 않습니다.")
        return
    
    lookup_files = list(output_dir.glob("lookup_table_*.csv"))
    if not lookup_files:
        print("output 폴더에 룩업테이블 파일이 없습니다.")
        print("먼저 PDF 디버그 파일을 룩업테이블로 변환해주세요.")
        return
    
    print("사용 가능한 룩업테이블 파일:")
    for i, lookup_file in enumerate(lookup_files, 1):
        print(f"  {i}. {lookup_file.name}")
    
    try:
        choice = int(input(f"\n변환할 룩업테이블 파일을 선택하세요 (1-{len(lookup_files)}): ")) - 1
        if 0 <= choice < len(lookup_files):
            lookup_file_path = str(lookup_files[choice])
            print(f"\n선택된 파일: {lookup_file_path}")
            
            # 매핑 설정 생성
            converter = PDFToLookupTable()
            output_path = converter.process_lookup_table_to_config(lookup_file_path)
            print(f"\n매핑 설정이 성공적으로 생성되었습니다: {output_path}")
        else:
            print("잘못된 선택입니다.")
    except ValueError:
        print("숫자를 입력해주세요.")
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

def main():
    while True:
        print("\n=== PDF 처리 도구 ===")
        print("1. 자동 분류 (부문별, 장별 자동 분류)")
        print("2. 페이지 지정 분리")
        print("3. PDF 파일 병합")
        print("4. 프로젝트 정보 보기")
        print("5. PDF 디버그 파일을 룩업테이블로 변환")
        print("6. 룩업테이블을 매핑 설정으로 변환")
        print("7. 종료")
        
        choice = input("\n작업 번호를 입력하세요 (1-7): ")
        
        if choice == "1":
            process_auto_classification()
        elif choice == "2":
            extract_pages_interactive()
        elif choice == "3":
            merge_chapter_pdfs()
        elif choice == "4":
            show_project_info()
        elif choice == "5":
            convert_debug_to_lookup_table()
        elif choice == "6":
            convert_lookup_table_to_config()
        elif choice == "7":
            print("\n프로그램을 종료합니다.")
            break
        else:
            print("\n잘못된 선택입니다. 1-7 중에서 선택해주세요.")

if __name__ == "__main__":
    main()