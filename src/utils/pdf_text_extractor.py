#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 텍스트 추출기 - 페이지별, 줄별 텍스트 추출 (개선된 버전)
문서 분석 패턴과 검증 로직을 포함한 체계적 접근
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import re

# 설정 모듈 import
try:
    from config.settings import INPUT_DIR, OUTPUT_DIR, ensure_directories
except ImportError:
    INPUT_DIR = Path("input")
    OUTPUT_DIR = Path("output")
    
    def ensure_directories():
        INPUT_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)

class DocumentAnalyzer:
    """문서 분석 클래스 - 반드시 사용"""
    
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
            "페이지": r"(=== [0-9]+페이지 ===)"
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
        
        # 부문이 발견되면 +30%
        if any(sections[section]["start"] is not None for section in sections):
            confidence += 0.3
        
        # 장이 발견되면 +30%
        if patterns["장"]:
            confidence += 0.3
        
        # 절이 발견되면 +20%
        if patterns["절"]:
            confidence += 0.2
        
        # 페이지 구분이 발견되면 +20%
        if patterns["페이지"]:
            confidence += 0.2
        
        return min(confidence, 1.0)

class ContentSearcher:
    """내용 검색 및 검증 클래스"""
    
    def __init__(self, content: str):
        self.content = content
        self.search_results = {}
    
    def search_with_validation(self, search_terms: List[str]) -> Dict[str, List[Dict]]:
        """검색어로 검색하고 결과 검증"""
        results = {}
        
        for term in search_terms:
            found_locations = self._find_term_locations(term)
            validated_results = self._validate_search_results(term, found_locations)
            results[term] = validated_results
        
        return results
    
    def _find_term_locations(self, term: str) -> List[Dict]:
        """용어 위치 찾기"""
        locations = []
        lines = self.content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if term in line:
                locations.append({
                    "line_number": line_num,
                    "line_content": line,
                    "context": self._get_context(lines, line_num)
                })
        
        return locations
    
    def _get_context(self, lines: List[str], line_num: int, context_size: int = 2) -> List[str]:
        """주변 문맥 가져오기"""
        start = max(0, line_num - context_size - 1)
        end = min(len(lines), line_num + context_size)
        return lines[start:end]
    
    def _validate_search_results(self, term: str, locations: List[Dict]) -> List[Dict]:
        """검색 결과 검증"""
        validated = []
        
        for location in locations:
            # 중복 제거
            if not any(v["line_number"] == location["line_number"] for v in validated):
                # 관련성 점수 계산
                relevance_score = self._calculate_relevance(term, location["line_content"])
                if relevance_score > 0.5:  # 50% 이상 관련성
                    location["relevance_score"] = relevance_score
                    validated.append(location)
        
        return validated
    
    def _calculate_relevance(self, term: str, line_content: str) -> float:
        """관련성 점수 계산"""
        if term in line_content:
            # 정확히 일치하면 높은 점수
            if term == line_content.strip():
                return 1.0
            # 부분 일치하면 중간 점수
            elif term in line_content:
                return 0.8
        return 0.0

class PDFTextExtractor:
    """PDF 텍스트 추출 클래스 (개선된 버전)"""
    
    def __init__(self):
        """초기화"""
        ensure_directories()
        self.analyzer = None
        self.searcher = None
    
    def extract_text_by_pages(self, pdf_path: Path, output_filename: Optional[str] = None) -> str:
        """
        PDF 파일에서 페이지별로 텍스트를 추출하여 TXT 파일로 저장 (개선된 버전)
        
        Args:
            pdf_path: PDF 파일 경로
            output_filename: 출력 파일명 (선택사항)
            
        Returns:
            str: 출력 파일 경로
        """
        try:
            # 1단계: 파일 검증
            if not self._validate_pdf_file(pdf_path):
                return ""
            
            # 2단계: PDF 정보 수집
            pdf_info = self.get_pdf_info(pdf_path)
            print(f"=== PDF 정보 ===")
            print(f"파일명: {pdf_info.get('파일명', 'N/A')}")
            print(f"총 페이지 수: {pdf_info.get('총_페이지_수', 'N/A')}")
            print(f"파일 크기: {pdf_info.get('파일_크기', 'N/A')}")
            print()
            
            # 3단계: 텍스트 추출 및 구조화
            extracted_content = self._extract_and_structure_text(pdf_path)
            
            # 4단계: 문서 분석
            analysis_results = self._analyze_extracted_content(extracted_content)
            
            # 5단계: 출력 파일명 결정
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{pdf_path.stem}_extracted_{timestamp}.txt"
            
            output_path = OUTPUT_DIR / output_filename
            
            # 6단계: 결과 저장
            self._save_extracted_content(output_path, extracted_content, analysis_results)
            
            # 7단계: 검증 및 보고서 생성
            validation_report = self._generate_validation_report(analysis_results)
            print(validation_report)
            
            return str(output_path)
            
        except Exception as e:
            print(f"오류: PDF 텍스트 추출 중 오류 발생: {e}")
            return ""
    
    def _validate_pdf_file(self, pdf_path: Path) -> bool:
        """PDF 파일 검증"""
        if not pdf_path.exists():
            print(f"오류: PDF 파일이 존재하지 않습니다: {pdf_path}")
            return False
        
        if pdf_path.stat().st_size == 0:
            print(f"오류: PDF 파일이 비어있습니다: {pdf_path}")
            return False
        
        if pdf_path.suffix.lower() != '.pdf':
            print(f"오류: PDF 파일이 아닙니다: {pdf_path}")
            return False
        
        return True
    
    def _extract_and_structure_text(self, pdf_path: Path) -> str:
        """텍스트 추출 및 구조화"""
        try:
            doc = fitz.open(str(pdf_path))
            total_pages = len(doc)
            
            extracted_content = []
            
            print("=== 텍스트 추출 시작 ===")
            
            for page_num in range(total_pages):
                print(f"페이지 {page_num + 1}/{total_pages} 처리 중...")
                
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():  # 빈 페이지가 아닌 경우만 처리
                    # 페이지 시작 표시
                    extracted_content.append(f"=== {page_num + 1}페이지 ===")
                    
                    # 줄별로 번호 매기기
                    lines = text.strip().split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if line.strip():  # 빈 줄 제외
                            extracted_content.append(f"{line_num}줄: {line}")
                    
                    # 페이지 구분자
                    extracted_content.append("----")
                    extracted_content.append("")  # 빈 줄 추가
            
            doc.close()
            
            return '\n'.join(extracted_content)
            
        except Exception as e:
            print(f"오류: 텍스트 추출 중 오류 발생: {e}")
            return ""
    
    def _analyze_extracted_content(self, content: str) -> Dict[str, Any]:
        """추출된 내용 분석"""
        try:
            # 문서 분석기 초기화
            temp_file = Path("temp") / "temp_content.txt"
            temp_file.parent.mkdir(exist_ok=True)
            temp_file.write_text(content, encoding='utf-8')
            
            self.analyzer = DocumentAnalyzer(temp_file)
            self.analyzer.content = content
            
            # 구조 분석
            structure_analysis = self.analyzer.analyze_document_structure()
            
            # 검색 및 검증
            self.searcher = ContentSearcher(content)
            search_results = self.searcher.search_with_validation([
                "부문", "장", "절", "페이지", "도로", "하천", "터널"
            ])
            
            # 임시 파일 정리
            temp_file.unlink()
            
            return {
                "structure": structure_analysis,
                "search_results": search_results,
                "content_length": len(content),
                "line_count": len(content.split('\n')),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"오류: 내용 분석 중 오류 발생: {e}")
            return {}
    
    def _save_extracted_content(self, output_path: Path, content: str, analysis_results: Dict[str, Any]):
        """추출된 내용 저장"""
        try:
            # 출력 디렉토리 확인
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 메타데이터 추가
            metadata = self._generate_metadata(analysis_results)
            
            # 전체 내용 구성
            full_content = f"""# PDF 텍스트 추출 결과

## 메타데이터
{metadata}

## 추출된 내용
{content}

## 분석 완료 시간
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            
            # 파일 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            print(f"✅ 텍스트 추출 완료: {output_path}")
            print(f"📊 파일 크기: {output_path.stat().st_size:,} bytes")
            
        except Exception as e:
            print(f"오류: 파일 저장 중 오류 발생: {e}")
    
    def _generate_metadata(self, analysis_results: Dict[str, Any]) -> str:
        """메타데이터 생성"""
        metadata_lines = []
        
        # 기본 정보
        structure = analysis_results.get("structure", {})
        file_info = structure.get("file_info", {})
        
        metadata_lines.append(f"- 파일명: {file_info.get('name', 'N/A')}")
        metadata_lines.append(f"- 파일 크기: {file_info.get('size', 0):,} bytes")
        metadata_lines.append(f"- 내용 길이: {analysis_results.get('content_length', 0):,} characters")
        metadata_lines.append(f"- 총 줄 수: {analysis_results.get('line_count', 0):,} lines")
        
        # 분석 신뢰도
        confidence = structure.get("analysis_confidence", 0.0)
        metadata_lines.append(f"- 분석 신뢰도: {confidence:.1%}")
        
        # 발견된 패턴
        patterns = structure.get("patterns", {})
        for pattern_type, pattern_list in patterns.items():
            if pattern_list:
                metadata_lines.append(f"- 발견된 {pattern_type}: {len(pattern_list)}개")
        
        # 검색 결과
        search_results = analysis_results.get("search_results", {})
        for term, results in search_results.items():
            if results:
                metadata_lines.append(f"- '{term}' 검색 결과: {len(results)}개")
        
        return '\n'.join(metadata_lines)
    
    def _generate_validation_report(self, analysis_results: Dict[str, Any]) -> str:
        """검증 보고서 생성"""
        report_lines = []
        report_lines.append("=== 검증 보고서 ===")
        
        # 기본 검증
        structure = analysis_results.get("structure", {})
        confidence = structure.get("analysis_confidence", 0.0)
        
        if confidence >= 0.8:
            report_lines.append("✅ 높은 신뢰도로 분석 완료")
        elif confidence >= 0.5:
            report_lines.append("⚠️ 중간 신뢰도로 분석 완료")
        else:
            report_lines.append("❌ 낮은 신뢰도 - 추가 검토 필요")
        
        # 패턴 검증
        patterns = structure.get("patterns", {})
        if patterns.get("부문"):
            report_lines.append("✅ 부문 구조 발견")
        if patterns.get("장"):
            report_lines.append("✅ 장 구조 발견")
        if patterns.get("절"):
            report_lines.append("✅ 절 구조 발견")
        if patterns.get("페이지"):
            report_lines.append("✅ 페이지 구분 발견")
        
        # 검색 결과 검증
        search_results = analysis_results.get("search_results", {})
        for term, results in search_results.items():
            if results:
                report_lines.append(f"✅ '{term}' 관련 내용 {len(results)}개 발견")
        
        return '\n'.join(report_lines)
    
    def get_pdf_info(self, pdf_path: Path) -> Dict[str, Any]:
        """
        PDF 파일 정보 반환
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict[str, Any]: PDF 파일 정보
        """
        try:
            doc = fitz.open(str(pdf_path))
            
            info = {
                "파일명": pdf_path.name,
                "총_페이지_수": len(doc),
                "파일_크기": f"{pdf_path.stat().st_size:,} bytes",
                "PDF_버전": doc.version,
                "메타데이터": doc.metadata
            }
            
            doc.close()
            return info
            
        except Exception as e:
            print(f"오류: PDF 정보 수집 중 오류 발생: {e}")
            return {}

class ErrorPreventionStrategy:
    """오류 방지 전략"""
    
    @staticmethod
    def validate_input_files(file_paths: List[Path]) -> List[Path]:
        """입력 파일 검증"""
        valid_files = []
        
        for file_path in file_paths:
            if not file_path.exists():
                print(f"경고: 파일이 존재하지 않습니다: {file_path}")
                continue
            
            if file_path.stat().st_size == 0:
                print(f"경고: 빈 파일입니다: {file_path}")
                continue
            
            valid_files.append(file_path)
        
        return valid_files
    
    @staticmethod
    def check_document_consistency(content: str) -> Dict[str, bool]:
        """문서 일관성 검사"""
        checks = {
            "has_content": len(content.strip()) > 0,
            "has_structure": any(keyword in content for keyword in ["부문", "장", "절"]),
            "has_page_breaks": "===" in content,
            "encoding_valid": True
        }
        
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            checks["encoding_valid"] = False
        
        return checks
    
    @staticmethod
    def generate_analysis_report(results: Dict[str, Any]) -> str:
        """분석 보고서 생성"""
        report = []
        report.append("=== 문서 분석 보고서 ===")
        
        # 파일 정보
        file_info = results.get("file_info", {})
        report.append(f"파일명: {file_info.get('name', 'N/A')}")
        report.append(f"크기: {file_info.get('size', 0)} bytes")
        
        # 구조 정보
        structure = results.get("structure", {})
        if structure.get("sections"):
            report.append("발견된 부문:")
            for section, info in structure["sections"].items():
                if info.get("start") is not None:
                    report.append(f"  - {section}")
        
        # 검증 결과
        validation = results.get("validation", {})
        report.append("검증 결과:")
        for check, status in validation.items():
            status_text = "✅ 통과" if status else "❌ 실패"
            report.append(f"  - {check}: {status_text}")
        
        # 권장사항
        recommendations = results.get("recommendations", [])
        if recommendations:
            report.append("권장사항:")
            for rec in recommendations:
                report.append(f"  - {rec}")
        
        return "\n".join(report)

def main():
    """메인 실행 함수"""
    # PDF 파일 경로
    pdf_path = INPUT_DIR / "split_3_49.pdf"
    
    # 텍스트 추출기 생성
    extractor = PDFTextExtractor()
    
    # PDF 정보 출력
    print("=== PDF 파일 정보 ===")
    info = extractor.get_pdf_info(pdf_path)
    for key, value in info.items():
        print(f"{key}: {value}")
    print()
    
    # 기본 텍스트 추출
    print("=== 기본 텍스트 추출 ===")
    result_path = extractor.extract_text_by_pages(pdf_path)
    
    if result_path:
        print(f"텍스트 추출 성공: {result_path}")
    else:
        print("텍스트 추출 실패")

if __name__ == "__main__":
    main() 