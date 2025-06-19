import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# 설정 모듈 import
try:
    from config.settings import get_mapping_config_path, config_file_exists
except ImportError:
    # 설정 모듈이 없는 경우 기본 경로 사용
    def get_mapping_config_path():
        return Path("mapping_config.json")
    
    def config_file_exists():
        return Path("mapping_config.json").exists()

class LookupTable:
    """
    수동 매핑을 위한 룩업 테이블 클래스
    """
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            self.config_file = str(get_mapping_config_path())
        else:
            self.config_file = config_file
        self.mapping_rules = self._load_mapping_rules()
    
    def _load_mapping_rules(self) -> Dict:
        """매핑 규칙을 JSON 파일에서 로드"""
        if config_file_exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"경고: {self.config_file} 파일 형식이 잘못되었습니다.")
                return self._get_default_rules()
        else:
            print(f"매핑 설정 파일이 없습니다. 기본 규칙을 사용합니다: {self.config_file}")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict:
        """기본 매핑 규칙 반환"""
        return {
            "chapter_patterns": [
                {"pattern": "제1장", "chapter": "1", "title": "총칙"},
                {"pattern": "제2장", "chapter": "2", "title": "일반사항"},
                {"pattern": "제3장", "chapter": "3", "title": "토공"},
                {"pattern": "제4장", "chapter": "4", "title": "콘크리트"},
                {"pattern": "제5장", "chapter": "5", "title": "철근콘크리트"},
                {"pattern": "제6장", "chapter": "6", "title": "철골"},
                {"pattern": "제7장", "chapter": "7", "title": "목공"},
                {"pattern": "제8장", "chapter": "8", "title": "조적"},
                {"pattern": "제9장", "chapter": "9", "title": "도장"},
                {"pattern": "제10장", "chapter": "10", "title": "지붕"},
                {"pattern": "제11장", "chapter": "11", "title": "창호"},
                {"pattern": "제12장", "chapter": "12", "title": "미장"},
                {"pattern": "제13장", "chapter": "13", "title": "타일"},
                {"pattern": "제14장", "chapter": "14", "title": "석공"},
                {"pattern": "제15장", "chapter": "15", "title": "방수"},
                {"pattern": "제16장", "chapter": "16", "title": "창호"},
                {"pattern": "제17장", "chapter": "17", "title": "철물"},
                {"pattern": "제18장", "chapter": "18", "title": "가설"},
                {"pattern": "제19장", "chapter": "19", "title": "조경"},
                {"pattern": "제20장", "chapter": "20", "title": "기타"}
            ],
            "section_patterns": [
                {"pattern": "01부문", "section": "01", "title": "준비공사"},
                {"pattern": "02부문", "section": "02", "title": "토공사"},
                {"pattern": "03부문", "section": "03", "title": "기초공사"},
                {"pattern": "04부문", "section": "04", "title": "구조공사"},
                {"pattern": "05부문", "section": "05", "title": "마감공사"},
                {"pattern": "06부문", "section": "06", "title": "설비공사"},
                {"pattern": "07부문", "section": "07", "title": "전기공사"},
                {"pattern": "08부문", "section": "08", "title": "소방공사"},
                {"pattern": "09부문", "section": "09", "title": "가설공사"},
                {"pattern": "10부문", "section": "10", "title": "기타공사"}
            ],
            "special_cases": {
                "첫페이지": {"chapter": "0", "section": "00", "title": "목차"},
                "부록": {"chapter": "99", "section": "99", "title": "부록"}
            }
        }
    
    def save_mapping_rules(self):
        """현재 매핑 규칙을 JSON 파일로 저장"""
        try:
            # 설정 디렉토리 생성
            config_dir = Path(self.config_file).parent
            config_dir.mkdir(exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.mapping_rules, f, ensure_ascii=False, indent=2)
            print(f"매핑 규칙이 {self.config_file}에 저장되었습니다.")
        except Exception as e:
            print(f"매핑 규칙 저장 중 오류: {e}")
    
    def classify_text(self, text: str) -> Tuple[str, str, str]:
        """
        텍스트를 분석하여 장, 부문, 제목을 분류
        
        Returns:
            Tuple[str, str, str]: (chapter, section, title)
        """
        text = text.strip()
        
        # 특수 케이스 먼저 확인
        for key, value in self.mapping_rules["special_cases"].items():
            if key in text:
                return value["chapter"], value["section"], value["title"]
        
        # 장 패턴 확인
        chapter_info = None
        for pattern_info in self.mapping_rules["chapter_patterns"]:
            if pattern_info["pattern"] in text:
                chapter_info = pattern_info
                break
        
        # 부문 패턴 확인
        section_info = None
        for pattern_info in self.mapping_rules["section_patterns"]:
            if pattern_info["pattern"] in text:
                section_info = pattern_info
                break
        
        # 결과 반환
        chapter = chapter_info["chapter"] if chapter_info else "0"
        section = section_info["section"] if section_info else "00"
        title = chapter_info["title"] if chapter_info else "미분류"
        
        return chapter, section, title
    
    def add_mapping_rule(self, rule_type: str, pattern: str, chapter: str = "", section: str = "", title: str = ""):
        """새로운 매핑 규칙 추가"""
        if rule_type == "chapter":
            self.mapping_rules["chapter_patterns"].append({
                "pattern": pattern,
                "chapter": chapter,
                "title": title
            })
        elif rule_type == "section":
            self.mapping_rules["section_patterns"].append({
                "pattern": pattern,
                "section": section,
                "title": title
            })
        elif rule_type == "special":
            self.mapping_rules["special_cases"][pattern] = {
                "chapter": chapter,
                "section": section,
                "title": title
            }
        
        self.save_mapping_rules()
        print(f"새로운 {rule_type} 규칙이 추가되었습니다: {pattern}")
    
    def get_all_patterns(self) -> Dict:
        """모든 매핑 패턴 반환"""
        return self.mapping_rules 