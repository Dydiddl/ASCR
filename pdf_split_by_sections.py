#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 부문별 분할 스크립트
JSON 파일의 목차 구조를 기반으로 PDF를 분할합니다.

조건:
1. 부문별로 폴더로 정리해서 pdf를 모은다.
2. 부문안에 각 장별로 하나의 pdf로 만든다.
"""

import json
import os
import platform
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from pypdf import PdfReader, PdfWriter
import re
from datetime import datetime

class DocumentAnalyzer:
    """문서 분석 클래스 - 코딩 표준 준수"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.structure = {}
        
    def analyze_document_structure(self) -> Dict[str, Any]:
        """문서 구조 분석 - 체계적 접근 필수"""
        try:
            # 1. 파일 타입 및 크기 확인
            file_info = self._get_file_info()
            
            # 2. 내용 미리보기 (처음 1000자)
            preview = self._get_content_preview()
            
            # 3. 구조적 패턴 검색
            patterns = self._find_structural_patterns()
            
            # 4. 부문/장/절 구분 분석
            sections = self._analyze_sections()
            
            # 5. 검증 및 결과 반환
            return self._validate_and_return(file_info, preview, patterns, sections)
            
        except Exception as e:
            print(f"문서 분석 중 오류 발생: {e}")
            return {}
    
    def _get_file_info(self) -> Dict[str, Any]:
        """파일 정보 수집"""
        return {
            "name": self.file_path.name,
            "size": self.file_path.stat().st_size,
            "type": self.file_path.suffix.lower(),
            "exists": self.file_path.exists()
        }
    
    def _get_content_preview(self) -> str:
        """내용 미리보기"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read(1000)
        except UnicodeDecodeError:
            # 바이너리 파일인 경우
            return "[바이너리 파일]"
    
    def _find_structural_patterns(self) -> Dict[str, List[str]]:
        """구조적 패턴 검색"""
        patterns = {
            "부문": [],
            "장": [],
            "절": [],
            "페이지": []
        }
        
        # 정규식 패턴 정의
        section_patterns = {
            "부문": r"([가-힣]+부문)",
            "장": r"(제[0-9]+장\s*[가-힣]+)",
            "절": r"([0-9]+-[0-9]+[가-힣]*)",
            "페이지": r"(=== [0-9]+페이지 ==)"
        }
        
        # 패턴 검색
        for pattern_name, pattern in section_patterns.items():
            matches = re.findall(pattern, self.content)
            patterns[pattern_name] = matches
        
        return patterns
    
    def _analyze_sections(self) -> Dict[str, Any]:
        """부문/장/절 구분 분석"""
        sections = {
            "공통부문": {"start": None, "end": None, "chapters": []},
            "토목부문": {"start": None, "end": None, "chapters": []},
            "건축부문": {"start": None, "end": None, "chapters": []},
            "기계설비부문": {"start": None, "end": None, "chapters": []},
            "유지관리부문": {"start": None, "end": None, "chapters": []}
        }
        
        # 부문 시작점 찾기
        for line_num, line in enumerate(self.content.split('\n')):
            for section_name in sections.keys():
                if section_name in line:
                    sections[section_name]["start"] = line_num
                    break
        
        return sections
    
    def _validate_and_return(self, file_info: Dict, preview: str, 
                           patterns: Dict, sections: Dict) -> Dict[str, Any]:
        """검증 및 결과 반환"""
        return {
            "file_info": file_info,
            "preview": preview[:200] + "..." if len(preview) > 200 else preview,
            "patterns": patterns,
            "sections": sections,
            "analysis_confidence": self._calculate_confidence(patterns, sections)
        }
    
    def _calculate_confidence(self, patterns: Dict, sections: Dict) -> float:
        """분석 신뢰도 계산"""
        confidence = 0.0
        
        # 패턴 발견 여부에 따른 점수
        if patterns.get("부문"):
            confidence += 0.3
        if patterns.get("장"):
            confidence += 0.3
        if patterns.get("페이지"):
            confidence += 0.2
        if patterns.get("절"):
            confidence += 0.2
            
        return min(confidence, 1.0)

class PDFSectionSplitter:
    """PDF 부문별 분할 클래스 - 코딩 표준 준수"""
    
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
        self.analyzer = DocumentAnalyzer(self.json_file_path)
        
    def load_data(self) -> bool:
        """데이터 로드 및 검증"""
        try:
            # JSON 파일 검증
            if not self.json_file_path.exists():
                print(f"오류: JSON 파일을 찾을 수 없습니다: {self.json_file_path}")
                return False
                
            # PDF 파일 검증
            if not self.pdf_file_path.exists():
                print(f"오류: PDF 파일을 찾을 수 없습니다: {self.pdf_file_path}")
                return False
            
            # JSON 데이터 로드
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.toc_data = json.load(f)
            
            # PDF 리더 초기화
            self.pdf_reader = PdfReader(self.pdf_file_path)
            
            # 데이터 검증
            if not self._validate_data():
                return False
                
            print(f"✅ 데이터 로드 완료")
            print(f"   - PDF 페이지 수: {len(self.pdf_reader.pages)}")
            print(f"   - 목차 항목 수: {len(self.toc_data.get('children', []))}")
            
            return True
            
        except FileNotFoundError as e:
            print(f"오류: 파일을 찾을 수 없습니다: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"오류: JSON 파일 형식이 잘못되었습니다: {e}")
            return False
        except Exception as e:
            print(f"오류: 데이터 로드 중 오류 발생: {e}")
            return False
    
    def _validate_data(self) -> bool:
        """데이터 검증"""
        if not self.toc_data:
            print("오류: 목차 데이터가 없습니다")
            return False
            
        if not self.pdf_reader:
            print("오류: PDF 리더가 초기화되지 않았습니다")
            return False
            
        if len(self.pdf_reader.pages) == 0:
            print("오류: PDF에 페이지가 없습니다")
            return False
            
        return True
    
    def _find_section_for_chapter(self, chapter_title: str) -> Optional[str]:
        """장 제목으로부터 부문 찾기"""
        if "적용기준" in chapter_title or "공통" in chapter_title:
            return "공통부문"
        elif "가설" in chapter_title or "토공" in chapter_title:
            return "토목부문"
        elif "건축" in chapter_title:
            return "건축부문"
        elif "기계" in chapter_title or "설비" in chapter_title:
            return "기계설비부문"
        elif "유지" in chapter_title or "관리" in chapter_title:
            return "유지관리부문"
        return None
    
    def _extract_chapters(self) -> Dict[str, List[Dict[str, Any]]]:
        """목차에서 장 정보 추출"""
        chapters_by_section = {
            "공통부문": [],
            "토목부문": [],
            "건축부문": [],
            "기계설비부문": [],
            "유지관리부문": []
        }
        
        # 부문 매핑 정의
        section_mapping = {
            "1": "공통부문",
            "2": "토목부문", 
            "3": "건축부문",
            "4": "기계설비부문",
            "5": "유지관리부문"
        }
        
        def extract_from_children(children: List[Dict], current_section: str = None):
            for child in children:
                if child.get("type") == "chapter":
                    title = child.get("title", "")
                    page_start = child.get("page")
                    page_end = child.get("page_end")
                    
                    # 부문 결정
                    section = self._find_section_for_chapter(title)
                    if not section:
                        section = current_section or "공통부문"
                    
                    # 페이지 범위 검증
                    if page_start is not None and page_end is not None:
                        if 0 <= page_start < len(self.pdf_reader.pages) and 0 <= page_end < len(self.pdf_reader.pages):
                            chapters_by_section[section].append({
                                "title": title,
                                "page_start": page_start,
                                "page_end": page_end,
                                "section": section
                            })
                        else:
                            print(f"⚠️  페이지 범위 오류: {title} ({page_start}-{page_end})")
                    elif page_start is not None:
                        # page_end가 없는 경우, 다음 장의 시작 페이지까지로 설정
                        chapters_by_section[section].append({
                            "title": title,
                            "page_start": page_start,
                            "page_end": page_start,  # 임시로 같은 페이지로 설정
                            "section": section
                        })
                
                # 재귀적으로 자식 항목 처리
                if child.get("children"):
                    extract_from_children(child.get("children"), current_section)
        
        # toc_tree에서 부문별로 처리
        if self.toc_data.get("toc_tree"):
            for section_key, children in self.toc_data["toc_tree"].items():
                section_name = section_mapping.get(section_key, "공통부문")
                extract_from_children(children, section_name)
        
        # 페이지 범위 계산 (다음 장의 시작 페이지까지)
        for section_name, chapters in chapters_by_section.items():
            for i, chapter in enumerate(chapters):
                if chapter["page_start"] == chapter["page_end"]:
                    # 다음 장의 시작 페이지 찾기
                    next_page = len(self.pdf_reader.pages) - 1  # 기본값: PDF 끝
                    
                    # 같은 부문 내에서 다음 장 찾기
                    for j in range(i + 1, len(chapters)):
                        if chapters[j]["section"] == section_name:
                            next_page = chapters[j]["page_start"] - 1
                            break
                    
                    chapter["page_end"] = next_page
        
        return chapters_by_section
    
    def _create_safe_filename(self, title: str) -> str:
        """안전한 파일명 생성"""
        # 특수문자 제거 및 한글 처리
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_title = safe_title.replace(' ', '_')
        safe_title = safe_title.replace('/', '_')
        
        # 파일명 길이 제한
        if len(safe_title) > 100:
            safe_title = safe_title[:100]
            
        return f"_{safe_title}.pdf"
    
    def _validate_page_range(self, page_start: int, page_end: int, title: str) -> bool:
        """페이지 범위 검증"""
        if page_start < 0 or page_end < 0:
            print(f"⚠️  음수 페이지: {title} ({page_start}-{page_end})")
            return False
            
        if page_start >= len(self.pdf_reader.pages):
            print(f"⚠️  시작 페이지가 PDF 범위를 초과: {title} ({page_start}-{page_end})")
            return False
            
        if page_end >= len(self.pdf_reader.pages):
            print(f"⚠️  끝 페이지가 PDF 범위를 초과: {title} ({page_start}-{page_end})")
            return False
            
        if page_start > page_end:
            print(f"⚠️  시작 페이지가 끝 페이지보다 큼: {title} ({page_start}-{page_end})")
            return False
            
        return True
    
    def split_pdf(self) -> bool:
        """PDF 분할 실행"""
        try:
            # 출력 디렉토리 생성
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 장 정보 추출
            chapters_by_section = self._extract_chapters()
            
            # 각 부문별로 처리
            total_files_created = 0
            report_lines = []
            
            for section_name, chapters in chapters_by_section.items():
                section_dir = self.output_dir / section_name
                section_dir.mkdir(exist_ok=True)
                
                files_created = 0
                
                for chapter in chapters:
                    title = chapter["title"]
                    page_start = chapter["page_start"]
                    page_end = chapter["page_end"]
                    
                    # 페이지 범위 검증
                    if not self._validate_page_range(page_start, page_end, title):
                        continue
                    
                    # 파일명 생성
                    filename = self._create_safe_filename(title)
                    output_path = section_dir / filename
                    
                    # PDF 분할
                    try:
                        writer = PdfWriter()
                        
                        for page_num in range(page_start, page_end + 1):
                            if page_num < len(self.pdf_reader.pages):
                                writer.add_page(self.pdf_reader.pages[page_num])
                        
                        # 파일 저장
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                        
                        file_size = output_path.stat().st_size
                        print(f"✅ 생성됨: {section_name}/{filename} ({file_size} bytes)")
                        files_created += 1
                        
                    except Exception as e:
                        print(f"❌ PDF 분할 실패: {title} - {e}")
                        continue
                
                total_files_created += files_created
                
                # 보고서 라인 추가
                report_lines.append(f"📁 {section_name}")
                report_lines.append(f"   📄 PDF 파일 수: {files_created}")
                if files_created > 0:
                    for chapter in chapters:
                        if chapter["section"] == section_name:
                            filename = self._create_safe_filename(chapter["title"])
                            file_path = section_dir / filename
                            if file_path.exists():
                                file_size = file_path.stat().st_size / 1024  # KB
                                report_lines.append(f"      - {filename} ({file_size:.1f} KB)")
                report_lines.append("")
            
            # 보고서 생성
            self._create_report(report_lines, total_files_created)
            
            print(f"\n🎉 PDF 분할 완료!")
            print(f"   총 생성된 파일 수: {total_files_created}")
            print(f"   출력 디렉토리: {self.output_dir}")
            
            return True
            
        except Exception as e:
            print(f"오류: PDF 분할 중 오류 발생: {e}")
            return False
    
    def _create_report(self, report_lines: List[str], total_files: int):
        """분할 결과 보고서 생성"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_content = f"""============================================================
PDF 부문별 분할 결과 보고서
============================================================
생성 시간: {timestamp}
원본 PDF: {self.pdf_file_path.name}
목차 데이터: {self.json_file_path.name}

"""
        
        report_content += "\n".join(report_lines)
        report_content += f"""📊 총 생성된 PDF 파일 수: {total_files}
============================================================"""
        
        report_path = self.output_dir / "분할_결과_보고서.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

def main():
    """메인 함수"""
    try:
        # 파일 경로 설정
        json_file = "output/toc_tree_with_content_20250620_231055.json"
        pdf_file = "input/split_3_49.pdf"
        
        # PDF 분할기 초기화
        splitter = PDFSectionSplitter(json_file, pdf_file)
        
        # 데이터 로드
        if not splitter.load_data():
            print("❌ 데이터 로드 실패")
            return False
        
        # PDF 분할 실행
        if not splitter.split_pdf():
            print("❌ PDF 분할 실패")
            return False
        
        return True
        
    except Exception as e:
        print(f"오류: 메인 실행 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 