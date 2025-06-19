from typing import List, Dict, Optional, Tuple
import os
from pathlib import Path
import pypdf
from .content_classifier import ContentClassifier
from ..utils.lookup_table import LookupTable
from tqdm import tqdm
import json
from datetime import datetime
import re

class PDFProcessor:
    def __init__(self, use_lookup_table: bool = True):
        self.classifier = ContentClassifier()
        self.lookup_table = LookupTable() if use_lookup_table else None
        self.analysis_log = []
        self.current_chapter_num = ''  # ex) 제1장
        self.current_chapter_title = ''  # ex) 적용기준
        
    def process_pdf(self, input_path: str) -> None:
        """PDF 파일을 처리하여 부문별, 장별로 분류합니다."""
        print(f"\n=== PDF 분류(로그 기록) 시작: {input_path} ===")
        
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
                first_page_text = pdf.pages[0].extract_text()
                first_line = first_page_text.split('\n')[0].strip() if first_page_text else ""
                self._log_page_analysis([1, "표지", first_line, '', ''])
                
                # 2페이지부터 분류
                for page_num in tqdm(range(1, total_pages), desc="진행률"):
                    page = pdf.pages[page_num]
                    page_text = page.extract_text()
                    first_line = page_text.split('\n')[0].replace(' ', '') if page_text else ""
                    search_area = first_line[:10]
                    if not first_line:
                        self._log_page_analysis([page_num+1, "빈페이지", '', '', ''])
                        continue
                    
                    # 룩업 테이블을 사용한 분류
                    if self.lookup_table:
                        chapter, section, title = self.lookup_table.classify_text(first_line)
                        if chapter != "0" or section != "00":
                            self._log_page_analysis([page_num+1, f"제{chapter}장", title, f"{section}부문", section])
                            continue
                    
                    # 기존 정규식 패턴 분류 (룩업 테이블에서 매칭되지 않은 경우)
                    # 장 패턴: 제X장 제목 숫자 (앞 10글자 내에서만)
                    m = re.search(r'(제\d+장)\s*([가-힣A-Za-z0-9]+)\s*(\d+)', search_area)
                    if m:
                        self.current_chapter_num = m.group(1)
                        self.current_chapter_title = m.group(2)
                        self._log_page_analysis([page_num+1, m.group(1), m.group(2), '', m.group(3)])
                        continue
                    # 부문 패턴: 숫자+부문 (앞 10글자 내에서만)
                    m = re.search(r'(\d+)\s*([가-힣]+부문)', search_area)
                    if m:
                        chapter_num = self.current_chapter_num if self.current_chapter_num else ''
                        chapter_title = self.current_chapter_title if self.current_chapter_title else ''
                        self._log_page_analysis([page_num+1, chapter_num, chapter_title, m.group(2), m.group(1)])
                        continue
                    # 목차 패턴: 숫자+목차 또는 목차+숫자 (띄어쓰기 무시)
                    if re.search(r'(\d+목차|목차\d+)', search_area):
                        self._log_page_analysis([page_num+1, "목차", first_line, '', ''])
                        continue
                    # 중간 표지(내용 있음)
                    # 다음 페이지의 부문명 추출
                    next_bumun = ''
                    if page_num + 1 < total_pages:
                        next_page = pdf.pages[page_num + 1]
                        next_text = next_page.extract_text()
                        next_first_line = next_text.split('\n')[0].replace(' ', '') if next_text else ""
                        next_search_area = next_first_line[:10]
                        m_next = re.search(r'(\d+)\s*([가-힣]+부문)', next_search_area)
                        if m_next:
                            next_bumun = m_next.group(2)
                    self._log_page_analysis([page_num+1, "중간표지", next_bumun, ''])
                
                # 분석 로그 저장
                self._save_analysis_log(output_dir)
                
        except Exception as e:
            print(f"\n오류가 발생했습니다: {str(e)}")
            return
            
        print("\n=== PDF 분류(로그 기록) 완료 ===")
    
    def add_custom_mapping(self, rule_type: str, pattern: str, chapter: str = "", section: str = "", title: str = ""):
        """사용자 정의 매핑 규칙을 추가합니다."""
        if self.lookup_table:
            self.lookup_table.add_mapping_rule(rule_type, pattern, chapter, section, title)
        else:
            print("룩업 테이블이 비활성화되어 있습니다.")
    
    def get_mapping_rules(self) -> Dict:
        """현재 매핑 규칙을 반환합니다."""
        if self.lookup_table:
            return self.lookup_table.get_all_patterns()
        return {}
        
    def _log_page_analysis(self, log_entry) -> None:
        """페이지 분석 결과를 로그에 추가합니다."""
        self.analysis_log.append(log_entry)
        
    def _save_analysis_log(self, output_dir: Path) -> None:
        """분석 로그를 파일로 저장합니다."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = output_dir / f"analysis_log_{timestamp}.txt"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=== PDF 페이지 분석 로그 ===\n\n")
            for entry in self.analysis_log:
                f.write(str(entry) + "\n")
                
        print(f"\n분석 로그가 저장되었습니다: {log_file}")
        
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
        sanitized = re.sub(r'[^\w\s가-힣]', '', filename)
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = sanitized.strip()
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized 