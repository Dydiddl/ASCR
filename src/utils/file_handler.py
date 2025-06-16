import os
from typing import List, Optional
from pathlib import Path

class FileHandler:
    @staticmethod
    def get_pdf_files(directory: str) -> List[str]:
        """
        디렉토리에서 PDF 파일 목록을 가져옴
        
        Args:
            directory (str): 검색할 디렉토리 경로
            
        Returns:
            List[str]: PDF 파일 경로 목록
        """
        pdf_files = []
        try:
            for file in os.listdir(directory):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(directory, file))
            return pdf_files
        except Exception as e:
            print(f"PDF 파일 검색 중 오류 발생: {str(e)}")
            return []
    
    @staticmethod
    def create_output_directory(directory: str) -> bool:
        """
        출력 디렉토리 생성
        
        Args:
            directory (str): 생성할 디렉토리 경로
            
        Returns:
            bool: 생성 성공 여부
        """
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"디렉토리 생성 중 오류 발생: {str(e)}")
            return False
    
    @staticmethod
    def get_file_name_without_extension(file_path: str) -> str:
        """
        파일 경로에서 확장자를 제외한 파일명 추출
        
        Args:
            file_path (str): 파일 경로
            
        Returns:
            str: 확장자를 제외한 파일명
        """
        return os.path.splitext(os.path.basename(file_path))[0]
    
    @staticmethod
    def ensure_directory_exists(file_path: str) -> bool:
        """
        파일 경로의 디렉토리가 존재하는지 확인하고 없으면 생성
        
        Args:
            file_path (str): 파일 경로
            
        Returns:
            bool: 디렉토리 존재/생성 성공 여부
        """
        try:
            directory = os.path.dirname(file_path)
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"디렉토리 확인/생성 중 오류 발생: {str(e)}")
            return False 