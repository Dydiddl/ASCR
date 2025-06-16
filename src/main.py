import os
from converter.pdf_converter import PDFConverter
from utils.file_handler import FileHandler

def main():
    # 입력/출력 디렉토리 설정
    input_dir = "input"
    output_dir = "output"
    
    # 출력 디렉토리 생성
    FileHandler.create_output_directory(output_dir)
    
    # PDF 파일 목록 가져오기
    pdf_files = FileHandler.get_pdf_files(input_dir)
    
    if not pdf_files:
        print("변환할 PDF 파일이 없습니다.")
        return
    
    # 각 PDF 파일 변환
    for pdf_file in pdf_files:
        print(f"\n변환 시작: {pdf_file}")
        
        # 출력 파일 경로 설정
        file_name = FileHandler.get_file_name_without_extension(pdf_file)
        output_file = os.path.join(output_dir, f"{file_name}.docx")
        
        # PDF 변환
        converter = PDFConverter(pdf_file, output_file)
        if converter.convert():
            print(f"변환 완료: {output_file}")
            
            # 표 추출 테스트
            tables = converter.extract_tables()
            if tables:
                print(f"추출된 표 개수: {len(tables)}")
            else:
                print("추출된 표가 없습니다.")
        else:
            print("변환 실패")

if __name__ == "__main__":
    main() 