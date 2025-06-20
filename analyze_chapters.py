#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON 파일에서 장(chapter) 정보를 추출하여 정리하는 스크립트
"""

import json
from pathlib import Path

def analyze_chapters(json_file_path):
    """JSON 파일에서 모든 장 정보를 추출"""
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chapters = []
    
    # toc_tree에서 모든 장 정보 추출
    for page_num, page_items in data['toc_tree'].items():
        for item in page_items:
            if item.get('type') == 'chapter':
                chapters.append({
                    'title': item['title'],
                    'page': item['page'],
                    'source_page': page_num
                })
    
    # 페이지 번호로 정렬
    chapters.sort(key=lambda x: x['page'])
    
    print("=== 📋 장(Chapter) 정보 분석 결과 ===")
    print(f"총 장 수: {len(chapters)}개")
    print()
    
    print("📚 장 목록 (페이지 순):")
    for i, chapter in enumerate(chapters, 1):
        print(f"{i:2d}. {chapter['title']} (p.{chapter['page']}) - JSON 페이지: {chapter['source_page']}")
    
    print()
    print("🏗️ 부문별 분류:")
    
    # 부문별 분류
    sections = {
        "공통부문": [],
        "토목부문": [],
        "건축부문": [],
        "기계설비부문": [],
        "유지관리부문": []
    }
    
    for chapter in chapters:
        title = chapter['title']
        
        if "제1장 적용기준" in title:
            sections["공통부문"].append(chapter)
        elif any(keyword in title for keyword in ["가설공사", "토공사", "조경공사", "기초공사", "철근콘크리트공사", "돌공사", "건설기계", "도로포장공사", "하천공사", "터널공사", "궤도공사", "강구조공사", "관부설", "항만공사", "지반조사", "측량"]):
            sections["토목부문"].append(chapter)
        elif any(keyword in title for keyword in ["철골공사", "조적공사", "타일공사", "목공사", "수장공사", "방수공사", "지붕", "금속공사", "미장공사", "창호", "칠공사"]):
            sections["건축부문"].append(chapter)
        elif any(keyword in title for keyword in ["배관공사", "덕트공사", "보온공사", "펌프", "밸브설비", "측정기기", "위생기구", "공기조화", "소방설비", "가스설비", "자동제어", "플랜트설비"]):
            sections["기계설비부문"].append(chapter)
        elif "제1장 공 통" in title or "제2장 토 목" in title or "제3장 건 축" in title or "제4장 기계설비" in title:
            sections["유지관리부문"].append(chapter)
    
    for section_name, section_chapters in sections.items():
        if section_chapters:
            print(f"\n📁 {section_name} ({len(section_chapters)}개 장):")
            for chapter in section_chapters:
                print(f"  - {chapter['title']} (p.{chapter['page']})")
        else:
            print(f"\n📁 {section_name}: 장 없음")
    
    return chapters, sections

if __name__ == "__main__":
    json_file = "output/toc_tree_20250621_001431.json"
    
    if Path(json_file).exists():
        chapters, sections = analyze_chapters(json_file)
    else:
        print(f"❌ 파일을 찾을 수 없습니다: {json_file}") 