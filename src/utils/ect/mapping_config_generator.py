#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 목차에서 mapping_config.json 생성기
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF

# 설정 모듈 import
try:
    from config.settings import INPUT_DIR, OUTPUT_DIR, ensure_directories
except ImportError:
    INPUT_DIR = Path("input")
    OUTPUT_DIR = Path("output")
    
    def ensure_directories():
        INPUT_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)

def extract_toc_from_pdf(pdf_path: Path, max_pages: int = 100) -> List[Dict]:
    """
    PDF에서 목차를 추출합니다.
    
    Args:
        pdf_path: PDF 파일 경로
        max_pages: 검색할 최대 페이지 수
        
    Returns:
        목차 항목들의 리스트
    """
    entries = []
    
    # 정규표현식 패턴 (개선된 버전)
    # 번호-번호 형태, 제목, 점선, 페이지 번호
    pattern = re.compile(r"(?P<number>(\d+-)+\d+)\s+(?P<title>.+?)\s+\.{3,}\s+(?P<page>\d+)\s*$")
    
    try:
        with fitz.open(str(pdf_path)) as doc:
            print(f"PDF 파일 열기 성공: {pdf_path}")
            print(f"총 페이지 수: {len(doc)}")
            
            # 앞쪽 페이지에서 목차 검색
            search_pages = min(max_pages, len(doc))
            print(f"목차 검색 페이지: 1-{search_pages}")
            
            for page_num in range(search_pages):
                page = doc.load_page(page_num)
                lines = page.get_text().split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    match = pattern.search(line)
                    if match:
                        entry = {
                            "번호": match.group("number"),
                            "제목": match.group("title").strip(),
                            "페이지": int(match.group("page")),
                            "발견페이지": page_num + 1,
                            "발견라인": line_num
                        }
                        entries.append(entry)
                        print(f"목차 항목 발견: {entry['번호']} - {entry['제목']}")
            
            print(f"총 {len(entries)}개의 목차 항목을 발견했습니다.")
            
    except FileNotFoundError:
        print(f"오류: PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return []
    except Exception as e:
        print(f"오류: PDF 파일 처리 중 오류 발생: {e}")
        return []
    
    return entries

def extract_levels(code: str) -> Dict[str, str]:
    """
    번호 코드를 계층별로 분리합니다.
    
    Args:
        code: 번호 코드 (예: "1-2-3")
        
    Returns:
        계층별 분리된 딕셔너리
    """
    parts = code.split("-")
    
    return {
        "대분류": parts[0] if parts else "",
        "중분류": "-".join(parts[:2]) if len(parts) > 1 else "",
        "소분류": "-".join(parts[2:]) if len(parts) > 2 else ""
    }

def create_mapping_config(entries: List[Dict]) -> Dict[str, Any]:
    """
    목차 항목들로부터 mapping_config.json 형식을 생성합니다.
    
    Args:
        entries: 목차 항목들의 리스트
        
    Returns:
        mapping_config.json 형식의 딕셔너리
    """
    if not entries:
        print("경고: 처리할 목차 항목이 없습니다.")
        return {}
    
    # 대분류별로 그룹화
    sections = {}
    chapters = []
    
    for entry in entries:
        levels = extract_levels(entry["번호"])
        
        # 대분류 정보 수집
        section_key = levels["대분류"]
        if section_key not in sections:
            sections[section_key] = {
                "section": section_key,
                "title": f"{section_key}부문",
                "chapters": []
            }
        
        # 장 정보 생성
        chapter_info = {
            "pattern": f"제{levels['대분류']}장",
            "chapter": levels["대분류"],
            "title": entry["제목"],
            "number": entry["번호"],
            "page": entry["페이지"],
            "subsections": []
        }
        
        # 중분류가 있으면 하위 섹션으로 추가
        if levels["중분류"] and levels["중분류"] != levels["대분류"]:
            subsection = {
                "pattern": levels["중분류"],
                "title": entry["제목"],
                "number": entry["번호"],
                "page": entry["페이지"]
            }
            chapter_info["subsections"].append(subsection)
        
        # 중복 제거하면서 장 정보 추가
        existing_chapter = next((ch for ch in sections[section_key]["chapters"] 
                               if ch["chapter"] == levels["대분류"]), None)
        if not existing_chapter:
            sections[section_key]["chapters"].append(chapter_info)
        else:
            # 기존 장에 하위 섹션 추가
            if chapter_info["subsections"]:
                existing_chapter["subsections"].extend(chapter_info["subsections"])
    
    # mapping_config.json 형식으로 변환
    mapping_config = {
        "chapter_patterns": [],
        "section_patterns": [],
        "special_cases": {
            "첫페이지": {"chapter": "0", "section": "00", "title": "목차"},
            "부록": {"chapter": "99", "section": "99", "title": "부록"}
        }
    }
    
    # 장 패턴 생성
    for section_key, section_data in sections.items():
        for chapter in section_data["chapters"]:
            mapping_config["chapter_patterns"].append({
                "pattern": chapter["pattern"],
                "chapter": chapter["chapter"],
                "title": chapter["title"]
            })
    
    # 부문 패턴 생성
    for section_key, section_data in sections.items():
        mapping_config["section_patterns"].append({
            "pattern": f"{section_key.zfill(2)}부문",
            "section": section_key.zfill(2),
            "title": section_data["title"]
        })
    
    return mapping_config

def save_mapping_config(config: Dict[str, Any], output_path: Path) -> bool:
    """
    mapping_config를 JSON 파일로 저장합니다.
    
    Args:
        config: 저장할 설정 딕셔너리
        output_path: 저장할 파일 경로
        
    Returns:
        저장 성공 여부
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"mapping_config.json이 저장되었습니다: {output_path}")
        return True
        
    except Exception as e:
        print(f"오류: 파일 저장 중 오류 발생: {e}")
        return False

def analyze_mapping_config(config: Dict[str, Any]) -> None:
    """
    생성된 mapping_config를 분석합니다.
    
    Args:
        config: 분석할 설정 딕셔너리
    """
    print("\n=== mapping_config 분석 결과 ===")
    
    if "chapter_patterns" in config:
        print(f"장 패턴 수: {len(config['chapter_patterns'])}")
        for i, chapter in enumerate(config['chapter_patterns'][:5], 1):
            print(f"  {i}. {chapter['pattern']} - {chapter['title']}")
        if len(config['chapter_patterns']) > 5:
            print(f"  ... 외 {len(config['chapter_patterns']) - 5}개")
    
    if "section_patterns" in config:
        print(f"\n부문 패턴 수: {len(config['section_patterns'])}")
        for section in config['section_patterns']:
            print(f"  {section['pattern']} - {section['title']}")

def main():
    """메인 함수"""
    print("=== PDF 목차에서 mapping_config.json 생성 ===")
    
    # 필요한 디렉토리 생성
    ensure_directories()
    
    # 입력 파일 경로
    pdf_filename = "split_3_49.pdf"
    pdf_path = INPUT_DIR / pdf_filename
    
    if not pdf_path.exists():
        print(f"오류: PDF 파일을 찾을 수 없습니다: {pdf_path}")
        print(f"입력 디렉토리: {INPUT_DIR}")
        
        # 입력 디렉토리의 PDF 파일 목록 표시
        pdf_files = list(INPUT_DIR.glob("*.pdf"))
        if pdf_files:
            print("사용 가능한 PDF 파일들:")
            for i, file in enumerate(pdf_files, 1):
                print(f"  {i}. {file.name}")
        return
    
    # 목차 추출
    print(f"\n1. PDF에서 목차 추출 중: {pdf_filename}")
    entries = extract_toc_from_pdf(pdf_path)
    
    if not entries:
        print("목차를 추출할 수 없습니다. 프로그램을 종료합니다.")
        return
    
    # mapping_config 생성
    print("\n2. mapping_config.json 생성 중...")
    config = create_mapping_config(entries)
    
    # 분석
    analyze_mapping_config(config)
    
    # 파일 저장
    print("\n3. 파일 저장 중...")
    output_path = OUTPUT_DIR / "mapping_config_generated.json"
    if save_mapping_config(config, output_path):
        print("\n=== mapping_config.json 생성 완료 ===")
        print(f"저장 위치: {output_path}")
        print("\n사용 방법:")
        print("1. 생성된 파일을 config/mapping_config.json로 복사")
        print("2. 필요에 따라 수동으로 편집")
    else:
        print("\n=== mapping_config.json 생성 실패 ===")

if __name__ == "__main__":
    main() 