import re
import json
import pandas as pd
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime

class PDFToLookupTable:
    """
    PDF 디버그 파일을 파싱하여 룩업테이블을 생성하는 클래스
    """
    
    def __init__(self, mapping_config_path: str = "config/mapping_config.json"):
        self.mapping_config_path = mapping_config_path
        self.mapping_config = self._load_mapping_config()
        
    def _load_mapping_config(self) -> Dict:
        """매핑 설정 파일 로드"""
        try:
            with open(self.mapping_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"매핑 설정 파일을 찾을 수 없습니다: {self.mapping_config_path}")
            return {}
        except json.JSONDecodeError:
            print(f"매핑 설정 파일 형식이 잘못되었습니다: {self.mapping_config_path}")
            return {}
    
    def parse_pdf_debug_file(self, debug_file_path: str) -> List[Dict]:
        """
        PDF 디버그 파일을 파싱하여 구조화된 데이터로 변환
        
        Returns:
            List[Dict]: 파싱된 항목들의 리스트
        """
        with open(debug_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 페이지별로 분리
        pages = content.split('=== 페이지')
        parsed_items = []
        
        for page in pages[1:]:  # 첫 번째는 빈 문자열이므로 제외
            page_items = self._parse_page(page)
            parsed_items.extend(page_items)
        
        return parsed_items
    
    def _parse_page(self, page_content: str) -> List[Dict]:
        """개별 페이지 내용을 파싱"""
        lines = page_content.strip().split('\n')
        
        # 페이지 번호 추출
        page_match = re.search(r'(\d+) ===', lines[0])
        page_num = int(page_match.group(1)) if page_match else 0
        
        items = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('줄') or line.startswith('미리보기') or line.startswith('텍스트'):
                continue
            
            # 목차 항목 패턴 매칭 (예: 1-1-1 목적················································································································· 3)
            item_match = re.match(r'^(\d+-\d+(-\d+)?)\s+(.+?)\s*[·\s]*(\d+)$', line)
            if item_match:
                number = item_match.group(1)
                title = item_match.group(3).strip()
                page_ref = int(item_match.group(4))
                
                items.append({
                    'number': number,
                    'title': title,
                    'page': page_ref,
                    'source_page': page_num
                })
        
        return items
    
    def classify_item(self, item: Dict) -> Dict:
        """
        매핑 설정을 사용하여 항목을 분류
        
        Args:
            item: 파싱된 항목 딕셔너리
            
        Returns:
            Dict: 분류된 항목 딕셔너리
        """
        number = item['number']
        title = item['title']
        
        # 번호 패턴 분석 (예: 1-1-1 -> chapter=1, section=1, subsection=1)
        parts = number.split('-')
        
        if len(parts) >= 2:
            chapter_num = parts[0]
            section_num = parts[1]
            subsection_num = parts[2] if len(parts) > 2 else ""
            
            # 매핑 설정에서 장 정보 찾기
            chapter_title = self._find_chapter_title(chapter_num)
            section_title = self._find_section_title(section_num)
            
            return {
                '대분류': chapter_title,
                '중분류': section_title,
                '소분류': subsection_num if subsection_num else "",
                '번호': number,
                '제목': title,
                '페이지': item['page']
            }
        
        return {
            '대분류': '미분류',
            '중분류': '',
            '소분류': '',
            '번호': number,
            '제목': title,
            '페이지': item['page']
        }
    
    def _find_chapter_title(self, chapter_num: str) -> str:
        """장 번호에 해당하는 제목 찾기"""
        for pattern_info in self.mapping_config.get('chapter_patterns', []):
            if pattern_info.get('chapter') == chapter_num:
                return pattern_info.get('title', f'제{chapter_num}장')
        return f'제{chapter_num}장'
    
    def _find_section_title(self, section_num: str) -> str:
        """부문 번호에 해당하는 제목 찾기"""
        for pattern_info in self.mapping_config.get('section_patterns', []):
            if pattern_info.get('section') == section_num:
                return pattern_info.get('title', f'{section_num}부문')
        return f'{section_num}부문'
    
    def create_lookup_table(self, debug_file_path: str, output_path: str = None) -> pd.DataFrame:
        """
        PDF 디버그 파일로부터 룩업테이블 생성
        
        Args:
            debug_file_path: PDF 디버그 파일 경로
            output_path: 출력 파일 경로 (선택사항)
            
        Returns:
            pd.DataFrame: 생성된 룩업테이블
        """
        # PDF 디버그 파일 파싱
        parsed_items = self.parse_pdf_debug_file(debug_file_path)
        
        # 각 항목 분류
        classified_items = []
        for item in parsed_items:
            classified_item = self.classify_item(item)
            classified_items.append(classified_item)
        
        # DataFrame 생성
        df = pd.DataFrame(classified_items)
        
        # 출력 파일 저장
        if output_path:
            self._save_lookup_table(df, output_path)
        
        return df
    
    def _save_lookup_table(self, df: pd.DataFrame, output_path: str):
        """룩업테이블을 파일로 저장"""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Excel 파일로 저장
        excel_path = output_path.replace('.csv', '.xlsx')
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"룩업테이블이 저장되었습니다: {excel_path}")
        
        # CSV 파일로도 저장
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"룩업테이블이 저장되었습니다: {output_path}")
    
    def create_mapping_config(self, lookup_table_path: str, output_path: str = None) -> Dict:
        """
        룩업테이블로부터 mapping_config.json 형식 생성
        
        Args:
            lookup_table_path: 룩업테이블 파일 경로 (CSV)
            output_path: 출력 파일 경로 (선택사항)
            
        Returns:
            Dict: 생성된 매핑 설정
        """
        # CSV 파일 읽기
        df = pd.read_csv(lookup_table_path)
        
        # 기존 매핑 설정 로드
        mapping_config = self._load_mapping_config()
        
        # 새로운 장 패턴 추가
        new_chapter_patterns = []
        existing_chapters = {pattern['chapter'] for pattern in mapping_config.get('chapter_patterns', [])}
        
        for _, row in df.iterrows():
            chapter_num = row['번호'].split('-')[0]
            if chapter_num not in existing_chapters:
                new_chapter_patterns.append({
                    "pattern": f"제{chapter_num}장",
                    "chapter": chapter_num,
                    "title": row['대분류']
                })
                existing_chapters.add(chapter_num)
        
        # 새로운 부문 패턴 추가
        new_section_patterns = []
        existing_sections = {pattern['section'] for pattern in mapping_config.get('section_patterns', [])}
        
        for _, row in df.iterrows():
            parts = row['번호'].split('-')
            if len(parts) >= 2:
                section_num = parts[1].zfill(2)  # 2자리로 패딩
                if section_num not in existing_sections:
                    new_section_patterns.append({
                        "pattern": f"{section_num}부문",
                        "section": section_num,
                        "title": row['중분류']
                    })
                    existing_sections.add(section_num)
        
        # 매핑 설정 업데이트
        if new_chapter_patterns:
            mapping_config.setdefault('chapter_patterns', []).extend(new_chapter_patterns)
        
        if new_section_patterns:
            mapping_config.setdefault('section_patterns', []).extend(new_section_patterns)
        
        # 출력 파일 저장
        if output_path:
            self._save_mapping_config(mapping_config, output_path)
        
        return mapping_config
    
    def _save_mapping_config(self, mapping_config: Dict, output_path: str):
        """매핑 설정을 JSON 파일로 저장"""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_config, f, ensure_ascii=False, indent=2)
        
        print(f"매핑 설정이 저장되었습니다: {output_path}")
    
    def process_debug_file(self, debug_file_path: str) -> str:
        """
        디버그 파일을 처리하여 룩업테이블 생성 (메인 함수)
        
        Args:
            debug_file_path: PDF 디버그 파일 경로
            
        Returns:
            str: 생성된 룩업테이블 파일 경로
        """
        # 출력 파일 경로 생성
        debug_file_name = Path(debug_file_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/lookup_table_{debug_file_name}_{timestamp}.csv"
        
        # 룩업테이블 생성
        df = self.create_lookup_table(debug_file_path, output_path)
        
        print(f"총 {len(df)}개의 항목이 처리되었습니다.")
        print(f"대분류별 분포:")
        print(df['대분류'].value_counts())
        
        return output_path
    
    def process_lookup_table_to_config(self, lookup_table_path: str) -> str:
        """
        룩업테이블을 처리하여 매핑 설정 생성
        
        Args:
            lookup_table_path: 룩업테이블 파일 경로
            
        Returns:
            str: 생성된 매핑 설정 파일 경로
        """
        # 출력 파일 경로 생성
        lookup_file_name = Path(lookup_table_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"config/mapping_config_{lookup_file_name}_{timestamp}.json"
        
        # 매핑 설정 생성
        mapping_config = self.create_mapping_config(lookup_table_path, output_path)
        
        print(f"매핑 설정이 생성되었습니다: {output_path}")
        print(f"새로 추가된 장 패턴: {len([p for p in mapping_config.get('chapter_patterns', []) if p.get('pattern', '').startswith('제')])}개")
        print(f"새로 추가된 부문 패턴: {len([p for p in mapping_config.get('section_patterns', []) if p.get('pattern', '').endswith('부문')])}개")
        
        return output_path


def main():
    """메인 실행 함수"""
    # PDF 디버그 파일 경로
    debug_file_path = "output/pdf_debug_20250619_211344.txt"
    
    # 룩업테이블 생성기 초기화
    converter = PDFToLookupTable()
    
    # 룩업테이블 생성
    output_path = converter.process_debug_file(debug_file_path)
    
    print(f"\n룩업테이블이 성공적으로 생성되었습니다: {output_path}")


if __name__ == "__main__":
    main() 