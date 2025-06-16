from pdf2docx import Converter
import os
from typing import Optional

class PDFConverter:
    def __init__(self, input_path: str, output_path: str):
        """
        PDF to Word 변환을 위한 클래스 초기화
        
        Args:
            input_path (str): 입력 PDF 파일 경로
            output_path (str): 출력 Word 파일 경로
        """
        self.input_path = input_path
        self.output_path = output_path
        self.converter = Converter(input_path)
    
    def convert(self) -> bool:
        """
        PDF를 Word로 변환
        
        Returns:
            bool: 변환 성공 여부
        """
        try:
            self.converter.convert(self.output_path)
            self.converter.close()
            return True
        except Exception as e:
            print(f"변환 중 오류 발생: {str(e)}")
            return False
    
    def extract_tables(self) -> Optional[list]:
        """
        PDF에서 표 추출
        
        Returns:
            Optional[list]: 추출된 표 목록
        """
        try:
            tables = self.converter.extract_tables()
            return tables
        except Exception as e:
            print(f"표 추출 중 오류 발생: {str(e)}")
            return None 