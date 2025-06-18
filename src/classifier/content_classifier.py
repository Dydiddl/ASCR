from typing import Dict, List, Optional, Tuple
import os
import re
from pathlib import Path

class ContentClassifier:
    def __init__(self):
        self.sections = {
            '공통부문': '공통부문',
            '토목부문': '토목부문',
            '건축부문': '건축부문',
            '기계설비부문': '기계설비부문',
            '유지관리부문': '유지관리부문',
            '참고자료': '참고자료'
        }
        
        self.page_patterns = {
            'chapter_right': r'\(제\s*(\d+)\s*장\s+([^)]+?)\s+(\d+)\)',  # (제 1장 제목 1)
            'section_left': r'\((\d+)\s+([^)]+?부문)\)',                # (1 공통부문)
        }
        
        self.output_base = Path('input/division')
        self.current_chapter = None
        self.current_section = None
        self.chapter_pages = []
        
    def create_output_directories(self):
        """출력 디렉토리 구조를 생성합니다."""
        for section in self.sections.values():
            section_path = self.output_base / section
            section_path.mkdir(parents=True, exist_ok=True)
            
    def analyze_header(self, text: str) -> Tuple[Optional[Dict], Optional[str]]:
        """텍스트를 분석하여 장 정보와 부문 정보를 추출합니다.
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Tuple[Optional[Dict], Optional[str]]: (장 정보, 부문 정보)
            - 장 정보: {'number': int, 'title': str} 또는 None
            - 부문 정보: 부문명 또는 None
        """
        if not text:
            return None, None
            
        # 첫 줄의 앞부분만 추출 (최대 15자)
        first_line = text.split('\n')[0].strip()[:15]
        if not first_line:
            return None, None
            
        chapter_info = None
        section_info = None
        
        # 부문 정보 패턴 (숫자로 시작하고 부문명으로 끝나는 줄)
        section_match = re.match(r'^(\d+)\s*[\.\s]*([가-힣]+부문)\s*', first_line)
        if section_match:
            section_name = section_match.group(2)
            if section_name in self.sections:
                section_info = self.sections[section_name]
                
        # 장 정보 패턴 (제X장)
        chapter_match = re.match(r'^제\s*(\d+)\s*장', first_line)
        if chapter_match:
            # 장 번호 추출
            chapter_number = int(chapter_match.group(1))
            # 제목은 전체 첫 줄에서 추출
            full_first_line = text.split('\n')[0].strip()
            title_match = re.search(r'제\s*\d+\s*장\s+([가-힣A-Za-z0-9\s]+)', full_first_line)
            if title_match:
                chapter_info = {
                    'number': chapter_number,
                    'title': title_match.group(1).strip()
                }
                
        return chapter_info, section_info
        
    def is_new_chapter(self, chapter_info: Dict) -> bool:
        """새로운 장의 시작인지 확인합니다."""
        if not self.current_chapter:
            return True
        return chapter_info['number'] != self.current_chapter['number']
        
    def get_output_path(self, section: str, chapter: int, title: str) -> Path:
        """출력 파일 경로를 생성합니다."""
        filename = f"제{chapter}장_{self.sanitize_filename(title)}.pdf"
        return self.output_base / section / filename
        
    def sanitize_filename(self, filename: str) -> str:
        """파일명에서 특수문자를 제거하고 길이를 제한합니다."""
        sanitized = re.sub(r'[^\w\s가-힣]', '', filename)
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = sanitized.strip()
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized
