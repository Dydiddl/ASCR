import os
from pathlib import Path
from src.converter.extract_PDF_pages import extract_pages_interactive
from src.classifier.pdf_processor import PDFProcessor
from src.utils.pdf_merger import merge_chapter_pdfs

def process_auto_classification():
    """자동 분류 기능을 실행합니다."""
    print("\n=== PDF 자동 분류 시작 ===")
    print("이 기능은 다음과 같이 동작합니다:")
    print("1. 표지는 '표지.pdf'로 저장됩니다.")
    print("2. 각 장은 해당 부문 폴더 아래에 저장됩니다.")
    print("3. 빈 페이지는 자동으로 건너뜁니다.")
    print("4. 같은 장의 PDF 파일들은 자동으로 병합됩니다.")
    print("\n")
    
    # 입력 PDF 파일 경로 받기
    input_pdf = input("분류할 PDF 파일의 경로를 입력하세요: ").strip()
    
    if not os.path.exists(input_pdf):
        print("오류: 파일을 찾을 수 없습니다.")
        return
        
    try:
        # PDF 처리 시작
        processor = PDFProcessor()
        processor.process_pdf(input_pdf)
        
        # PDF 파일 병합
        merge_chapter_pdfs()
        
        print("\n=== PDF 분류가 완료되었습니다 ===")
        print(f"결과물은 {Path.cwd()}/output 디렉토리에 저장되었습니다.")
        
    except Exception as e:
        print(f"\n오류가 발생했습니다: {str(e)}")

def main():
    while True:
        print("\n=== PDF 처리 도구 ===")
        print("1. 자동 분류 (부문별, 장별 자동 분류)")
        print("2. 페이지 지정 분리")
        print("3. PDF 파일 병합")
        print("4. 종료")
        
        choice = input("\n작업 번호를 입력하세요 (1-4): ")
        
        if choice == "1":
            process_auto_classification()
        elif choice == "2":
            extract_pages_interactive()
        elif choice == "3":
            merge_chapter_pdfs()
        elif choice == "4":
            print("\n프로그램을 종료합니다.")
            break
        else:
            print("\n잘못된 선택입니다. 1-4 중에서 선택해주세요.")

if __name__ == "__main__":
    main()