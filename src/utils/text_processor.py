import re
from typing import List, Dict, Optional

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        텍스트 정제
        
        Args:
            text (str): 정제할 텍스트
            
        Returns:
            str: 정제된 텍스트
        """
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 특수문자 처리
        text = text.strip()
        return text
    
    @staticmethod
    def extract_section_number(text: str) -> Optional[str]:
        """
        섹션 번호 추출 (예: 1-1-2)
        
        Args:
            text (str): 섹션 번호가 포함된 텍스트
            
        Returns:
            Optional[str]: 추출된 섹션 번호
        """
        pattern = r'\d+-\d+-\d+'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    @staticmethod
    def split_into_sections(text: str) -> Dict[str, str]:
        """
        텍스트를 섹션별로 분리
        
        Args:
            text (str): 분리할 텍스트
            
        Returns:
            Dict[str, str]: 섹션 번호와 내용의 매핑
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in text.split('\n'):
            section_num = TextProcessor.extract_section_number(line)
            if section_num:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = section_num
                current_content = [line]
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    @staticmethod
    def find_related_tables(section_content: str, tables: List[Dict]) -> List[Dict]:
        """
        섹션 내용과 관련된 표 찾기
        
        Args:
            section_content (str): 섹션 내용
            tables (List[Dict]): 표 목록
            
        Returns:
            List[Dict]: 관련된 표 목록
        """
        related_tables = []
        # TODO: 표와 내용의 연관성 판단 로직 구현
        return related_tables 