#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 부문별/장별 분할 스크립트
JSON 파일의 목차 구조를 기반으로 PDF를 분할합니다.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from pypdf import PdfReader, PdfWriter
import re
from datetime import datetime

class PDFChapterSplitter:
    """PDF 장별 분할 클래스"""
    
    def __init__(self, json_file_path: str, pdf_file_path: str):
        """
        초기화
        
        Args:
            json_file_path: 목차 구조가 포함된 JSON 파일 경로
            pdf_file_path: 분할할 PDF 파일 경로
        """
        self.json_file_path = Path(json_file_path)
        self.pdf_file_path = Path(pdf_file_path)
        self.output_dir = Path("output/split_pdfs")
        self.toc_data = None
        self.pdf_reader = None
        
        # 부문 매핑 정의
        self.section_mapping = {
            "제1장 적용기준": "공통부문",
            "제2장 가설공사": "토목부문",
            "제3장 토공사": "토목부문",
            "제4장 조경공사": "토목부문",
            "제5장 기초공사": "토목부문",
            "제6장 철근콘크리트공사": "토목부문",
            "제7장 돌공사": "토목부문",
            "제8장 건설기계": "토목부문",
            "제1장 도로포장공사": "토목부문",
            "제2장 하천공사": "토목부문",
            "제3장 터널공사": "토목부문",
            "제4장 궤도공사": "토목부문",
            "제5장 강구조공사": "토목부문",
            "제6장 관부설 및 접합공사": "토목부문",
            "제7장 항만공사": "토목부문",
            "제8장 지반조사": "토목부문",
            "제9장 측 량": "토목부문",
            "제1장 철골공사": "건축부문",
            "제2장 조적공사": "건축부문",
            "제3장 타일공사": "건축부문",
            "제4장 목공사": "건축부문",
            "제5장 수장공사": "건축부문",
            "제6장 방수공사": "건축부문",
            "제7장 지붕 및 홈통공사": "건축부문",
            "제8장 금속공사": "건축부문",
            "제9장 미장공사": "건축부문",
            "제10장 창호 및 유리공사": "건축부문",
            "제11장 칠공사": "건축부문",
            "제1장 배관공사": "기계설비부문",
            "제2장 덕트공사": "기계설비부문",
            "제3장 보온공사": "기계설비부문",
            "제4장 펌프 및 공기설비공사": "기계설비부문",
            "제5장 밸브설비공사": "기계설비부문",
            "제6장 측정기기공사": "기계설비부문",
            "제7장 위생기구설비공사": "기계설비부문",
            "제8장 공기조화설비공사": "기계설비부문",
            "제9장 기타공사": "기계설비부문",
            "제10장 소방설비공사": "기계설비부문",
            "제11장 가스설비공사": "기계설비부문",
            "제12장 자동제어설비공사": "기계설비부문",
            "제13장 플랜트설비공사": "기계설비부문",
            "제1장 공 통": "유지관리부문",
            "제2장 토 목": "유지관리부문",
            "제3장 건 축": "유지관리부문",
            "제4장 기계설비": "유지관리부문"
        }
    
    def load_json_data(self) -> bool:
        """JSON 파일 로드"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.toc_data = json.load(f)
            print(f"✅ JSON 파일 로드 완료: {self.json_file_path}")
            return True
        except Exception as e:
            print(f"❌ JSON 파일 로드 실패: {e}")
            return False
    
    def load_pdf(self) -> bool:
        """PDF 파일 로드"""
        try:
            self.pdf_reader = PdfReader(self.pdf_file_path)
            print(f"✅ PDF 파일 로드 완료: {self.pdf_file_path}")
            print(f"📄 총 페이지 수: {len(self.pdf_reader.pages)}")
            return True
        except Exception as e:
            print(f"❌ PDF 파일 로드 실패: {e}")
            return False
    
    def extract_chapters(self) -> Dict[str, List[Dict[str, Any]]]:
        """JSON에서 장 정보 추출"""
        chapters_by_section = {
            "공통부문": [],
            "토목부문": [],
            "건축부문": [],
            "기계설비부문": [],
            "유지관리부문": []
        }
        
        # toc_tree에서 모든 장 정보 추출
        for page_num, page_items in self.toc_data['toc_tree'].items():
            for item in page_items:
                if item.get('type') == 'chapter':
                    title = item['title']
                    page = item['page']
                    
                    # 부문 매핑 - 공통부문에 8장까지 포함
                    if title in ["제1장 적용기준", "제2장 가설공사", "제3장 토공사", "제4장 조경공사", 
                                "제5장 기초공사", "제6장 철근콘크리트공사", "제7장 돌공사", "제8장 건설기계"]:
                        section = "공통부문"
                    elif title in ["제1장 도로포장공사", "제2장 하천공사", "제3장 터널공사", "제4장 궤도공사",
                                  "제5장 강구조공사", "제6장 관부설 및 접합공사", "제7장 항만공사", 
                                  "제8장 지반조사", "제9장 측 량"]:
                        section = "토목부문"
                    elif title in ["제1장 철골공사", "제2장 조적공사", "제3장 타일공사", "제4장 목공사",
                                  "제5장 수장공사", "제6장 방수공사", "제7장 지붕 및 홈통공사", 
                                  "제8장 금속공사", "제9장 미장공사", "제10장 창호 및 유리공사", "제11장 칠공사"]:
                        section = "건축부문"
                    elif title in ["제1장 배관공사", "제2장 덕트공사", "제3장 보온공사", "제4장 펌프 및 공기설비공사",
                                  "제5장 밸브설비공사", "제6장 측정기기공사", "제7장 위생기구설비공사",
                                  "제8장 공기조화설비공사", "제9장 기타공사", "제10장 소방설비공사",
                                  "제11장 가스설비공사", "제12장 자동제어설비공사", "제13장 플랜트설비공사"]:
                        section = "기계설비부문"
                    elif title in ["제1장 공 통", "제2장 토 목", "제3장 건 축", "제4장 기계설비"]:
                        section = "유지관리부문"
                    else:
                        section = "기타"
                    
                    if section != "기타":
                        chapters_by_section[section].append({
                            'title': title,
                            'page': page,
                            'source_page': page_num
                        })
        
        # 각 부문 내에서 페이지 순으로 정렬
        for section in chapters_by_section:
            chapters_by_section[section].sort(key=lambda x: x['page'])
        
        return chapters_by_section
    
    def calculate_page_ranges(self, chapters: List[Dict[str, Any]], total_pages: int) -> List[Dict[str, Any]]:
        """장별 페이지 범위 계산"""
        chapters_with_ranges = []
        
        for i, chapter in enumerate(chapters):
            start_page = chapter['page']
            
            # 끝 페이지 계산
            if i < len(chapters) - 1:
                # 다음 장의 시작 페이지 - 1
                end_page = chapters[i + 1]['page'] - 1
            else:
                # 마지막 장은 PDF 끝까지
                end_page = total_pages
            
            # 페이지 범위 검증
            if start_page > total_pages:
                print(f"⚠️ 경고: {chapter['title']} 시작 페이지({start_page})가 PDF 총 페이지({total_pages})를 초과합니다.")
                continue
            
            if end_page > total_pages:
                end_page = total_pages
                print(f"⚠️ 경고: {chapter['title']} 끝 페이지를 PDF 총 페이지로 조정했습니다.")
            
            chapter_with_range = chapter.copy()
            chapter_with_range['start_page'] = start_page
            chapter_with_range['end_page'] = end_page
            chapters_with_ranges.append(chapter_with_range)
        
        return chapters_with_ranges
    
    def create_safe_filename(self, title: str) -> str:
        """안전한 파일명 생성"""
        # 특수문자 제거 및 한글 처리
        safe_name = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_name = safe_name.replace(' ', '_')
        safe_name = safe_name.replace('·', '')
        return safe_name
    
    def split_pdf_by_chapters(self) -> bool:
        """PDF를 장별로 분할"""
        if not self.load_json_data() or not self.load_pdf():
            return False
        
        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 목차 부분 먼저 분할
        toc_success = self.split_toc_section()
        
        # 2. 장 정보 추출
        chapters_by_section = self.extract_chapters()
        total_pages = len(self.pdf_reader.pages)
        
        print(f"\n=== 📋 분할 계획 ===")
        total_chapters = sum(len(chapters) for chapters in chapters_by_section.values())
        print(f"총 분할할 장 수: {total_chapters}개")
        
        success_count = 0
        error_count = 0
        
        # 목차 분할 성공 시 카운트 추가
        if toc_success:
            success_count += 1
        
        # 부문별로 분할
        for section_name, chapters in chapters_by_section.items():
            if not chapters:
                continue
            
            print(f"\n📁 {section_name} 처리 중...")
            
            # 부문별 폴더 생성
            section_dir = self.output_dir / section_name
            section_dir.mkdir(exist_ok=True)
            
            # 페이지 범위 계산
            chapters_with_ranges = self.calculate_page_ranges(chapters, total_pages)
            
            # 각 장별로 PDF 분할
            for chapter in chapters_with_ranges:
                try:
                    title = chapter['title']
                    start_page = chapter['start_page']
                    end_page = chapter['end_page']
                    
                    # 안전한 파일명 생성
                    safe_filename = self.create_safe_filename(title)
                    output_file = section_dir / f"{safe_filename}.pdf"
                    
                    # PDF 분할
                    writer = PdfWriter()
                    
                    # 페이지 인덱스는 0부터 시작하므로 -1
                    for page_num in range(start_page - 1, end_page):
                        if page_num < len(self.pdf_reader.pages):
                            writer.add_page(self.pdf_reader.pages[page_num])
                    
                    # 파일 저장
                    with open(output_file, 'wb') as output_pdf:
                        writer.write(output_pdf)
                    
                    file_size = output_file.stat().st_size
                    print(f"  ✅ {title} (p.{start_page}-{end_page}) → {file_size:,} bytes")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ❌ {title} 분할 실패: {e}")
                    error_count += 1
        
        # 결과 보고서 생성
        self.generate_report(chapters_by_section, success_count, error_count)
        
        print(f"\n=== 📊 분할 완료 ===")
        print(f"✅ 성공: {success_count}개")
        print(f"❌ 실패: {error_count}개")
        print(f"📁 출력 위치: {self.output_dir}")
        
        return error_count == 0
    
    def generate_report(self, chapters_by_section: Dict[str, List[Dict]], success_count: int, error_count: int):
        """분할 결과 보고서 생성"""
        report_file = self.output_dir / "분할_결과_보고서.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== PDF 부문별/장별 분할 결과 보고서 ===\n")
            f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"원본 PDF: {self.pdf_file_path}\n")
            f.write(f"목차 JSON: {self.json_file_path}\n\n")
            
            f.write(f"=== 📊 전체 통계 ===\n")
            f.write(f"성공: {success_count}개\n")
            f.write(f"실패: {error_count}개\n\n")
            
            f.write("=== �� 부문별 분할 결과 ===\n")
            
            # 목차 부분 추가
            f.write(f"\n📁 목차 (1개 파일):\n")
            f.write(f"  - 목차 (p.1-47)\n")
            
            for section_name, chapters in chapters_by_section.items():
                if chapters:
                    f.write(f"\n📁 {section_name} ({len(chapters)}개 장):\n")
                    for chapter in chapters:
                        f.write(f"  - {chapter['title']} (p.{chapter['page']})\n")
                else:
                    f.write(f"\n📁 {section_name}: 장 없음\n")
        
        print(f"📄 보고서 생성: {report_file}")

    def split_toc_section(self) -> bool:
        """목차 부분 분할 (1-47페이지)"""
        try:
            print(f"\n📁 목차 부분 처리 중...")
            
            # 목차 폴더 생성
            toc_dir = self.output_dir / "목차"
            toc_dir.mkdir(exist_ok=True)
            
            # 목차 부분 분할 (1-47페이지)
            start_page = 1
            end_page = 47
            
            # PDF 분할
            writer = PdfWriter()
            
            # 페이지 인덱스는 0부터 시작하므로 -1
            for page_num in range(start_page - 1, end_page):
                if page_num < len(self.pdf_reader.pages):
                    writer.add_page(self.pdf_reader.pages[page_num])
            
            # 파일 저장
            output_file = toc_dir / "목차.pdf"
            with open(output_file, 'wb') as output_pdf:
                writer.write(output_file)
            
            file_size = output_file.stat().st_size
            print(f"  ✅ 목차 (p.{start_page}-{end_page}) → {file_size:,} bytes")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 목차 분할 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    # 파일 경로 설정 - 최신 JSON 파일 사용
    json_file = "output/toc_tree_20250621_015401.json"
    pdf_file = "input/2025_construction_work_standard_price_list.pdf"  # 올바른 전체 PDF 파일
    
    print("🚀 PDF 부문별/장별 분할 시작")
    print("=" * 50)
    print("📋 작업 계획:")
    print("1. 목차 JSON: split_3_49.pdf에서 생성된 구조 사용")
    print("2. 분할 대상: 2025_construction_work_standard_price_list.pdf (전체 내용)")
    print("=" * 50)
    
    # 파일 존재 확인
    if not Path(json_file).exists():
        print(f"❌ JSON 파일을 찾을 수 없습니다: {json_file}")
        print("💡 먼저 extract_split_3_49_improved.py를 실행하여 목차 JSON을 생성하세요.")
        return
    
    if not Path(pdf_file).exists():
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_file}")
        print("💡 input 폴더에 2025_construction_work_standard_price_list.pdf 파일을 넣어주세요.")
        return
    
    # PDF 분할 실행
    splitter = PDFChapterSplitter(json_file, pdf_file)
    success = splitter.split_pdf_by_chapters()
    
    if success:
        print("\n🎉 모든 분할 작업이 성공적으로 완료되었습니다!")
        print("📁 결과 위치: output/split_pdfs/")
    else:
        print("\n⚠️ 일부 분할 작업에서 오류가 발생했습니다.")

if __name__ == "__main__":
    main() 