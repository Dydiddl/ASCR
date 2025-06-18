from typing import List, Dict, Optional, Tuple
import os
from pathlib import Path
import pypdf
from .content_classifier import ContentClassifier
from tqdm import tqdm

class PDFProcessor:
    def __init__(self):
        self.classifier = ContentClassifier()
        
    def process_pdf(self, input_path: str) -> None:
        """PDF 파일을 처리하여 부문별, 장별로 분류합니다."""
        print(f"\n=== PDF 처리 시작: {input_path} ===")
        
        # 입력 파일 존재 확인
        if not os.path.exists(input_path):
            print(f"오류: 입력 파일이 존재하지 않습니다: {input_path}")
            return
            
        # 출력 디렉토리 생성
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        print("출력 디렉토리 생성 완료")
        
        try:
            with open(input_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)
                total_pages = len(pdf.pages)
                print(f"총 페이지 수: {total_pages}")
                
                # 표지 처리 (첫 페이지)
                self._save_cover_page(pdf, output_dir)
                
                # 장별로 페이지를 모으기 위한 딕셔너리
                # Key: (부문, 장번호, 장제목), Value: 페이지 번호 리스트
                chapter_pages = {}
                current_section = None
                current_chapter = None
                
                # 2페이지부터 끝까지 처리
                print("\n페이지 분석 및 분류 중...")
                for page_num in tqdm(range(1, total_pages), desc="진행률"):
                    # 빈 페이지 건너뛰기
                    if self._is_empty_page(pdf.pages[page_num]):
                        continue
                        
                    # 페이지 텍스트 추출
                    page_text = pdf.pages[page_num].extract_text()
                    chapter_info, section_info = self.classifier.analyze_header(page_text)
                    
                    # 부문 정보 업데이트
                    if section_info:
                        current_section = section_info
                        
                    # 장 정보 업데이트
                    if chapter_info:
                        current_chapter = chapter_info
                        
                    # 현재 장이 있으면 페이지 추가
                    if current_chapter and current_section:
                        key = (current_section, current_chapter['number'], current_chapter['title'])
                        if key not in chapter_pages:
                            chapter_pages[key] = []
                        chapter_pages[key].append(page_num)
                        
                # 모든 장을 저장
                print("\n파일 저장 중...")
                for (section, chapter_num, chapter_title), pages in chapter_pages.items():
                    section_dir = output_dir / section
                    section_dir.mkdir(exist_ok=True)
                    
                    filename = f"제{chapter_num}장_{self._sanitize_filename(chapter_title)}.pdf"
                    output_path = section_dir / filename
                    
                    try:
                        writer = pypdf.PdfWriter()
                        for page_num in pages:
                            writer.add_page(pdf.pages[page_num])
                            
                        with open(output_path, 'wb') as outfile:
                            writer.write(outfile)
                            
                    except Exception as e:
                        print(f"\n오류: {filename} 저장 중 오류 발생 - {str(e)}")
                    
        except Exception as e:
            print(f"\n오류가 발생했습니다: {str(e)}")
            return
            
        print("\n=== PDF 분류가 완료되었습니다 ===")
        
    def _save_cover_page(self, pdf: pypdf.PdfReader, output_dir: Path) -> None:
        """표지 페이지를 저장합니다."""
        output_path = output_dir / "표지.pdf"
        writer = pypdf.PdfWriter()
        writer.add_page(pdf.pages[0])
        
        with open(output_path, 'wb') as file:
            writer.write(file)
        print("표지 저장 완료")
        
    def _is_empty_page(self, page: pypdf.PageObject) -> bool:
        """페이지가 비어있는지 확인합니다."""
        text = page.extract_text().strip()
        return not text
        
    def _sanitize_filename(self, filename: str) -> str:
        """파일 이름에서 사용할 수 없는 문자를 제거합니다."""
        import re
        sanitized = re.sub(r'[^\w\s가-힣]', '', filename)
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = sanitized.strip()
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized 