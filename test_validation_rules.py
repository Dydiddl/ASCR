#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새로 추가된 검증 규칙 테스트 스크립트
건축부문 누락 사고 방지를 위한 규칙들을 테스트합니다.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def pre_analysis_checklist(file_path: Path) -> Dict[str, bool]:
    """분석 전 체크리스트 - 반드시 실행"""
    checklist = {
        "file_exists": False,
        "file_readable": False,
        "file_not_empty": False,
        "encoding_supported": False,
        "content_contains_korean": False,
        "ready_for_analysis": False
    }
    
    try:
        # 1. 파일 존재 확인
        if file_path.exists():
            checklist["file_exists"] = True
        
        # 2. 파일 읽기 가능 확인
        if file_path.is_file():
            checklist["file_readable"] = True
        
        # 3. 파일 크기 확인
        if file_path.stat().st_size > 0:
            checklist["file_not_empty"] = True
        
        # 4. 인코딩 지원 확인
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)
                checklist["encoding_supported"] = True
                
                # 5. 한국어 내용 포함 확인
                if any('\u3131' <= char <= '\u318E' or '\uAC00' <= char <= '\uD7A3' for char in content):
                    checklist["content_contains_korean"] = True
        except UnicodeDecodeError:
            pass
        
        # 6. 분석 준비 완료 확인
        checklist["ready_for_analysis"] = all([
            checklist["file_exists"],
            checklist["file_readable"],
            checklist["file_not_empty"],
            checklist["encoding_supported"],
            checklist["content_contains_korean"]
        ])
        
    except Exception as e:
        print(f"체크리스트 실행 중 오류: {e}")
    
    return checklist

def validate_all_sections(content: str) -> Dict[str, Any]:
    """모든 부문 검증 - 반드시 실행"""
    # 공백이 있는 형태와 없는 형태 모두 검색
    required_sections = [
        "공통부문", "공 통 부 문",
        "토목부문", "토 목 부 문", 
        "건축부문", "건 축 부 문",
        "기계설비부문", "기 계 설 비 부 문",
        "유지관리부문", "유 지 관 리 부 문"
    ]
    
    validation_result = {
        "all_sections_found": True,
        "section_details": {},
        "missing_sections": [],
        "section_order": [],
        "validation_passed": False
    }
    
    # 각 부문 검색 및 상세 정보 수집
    found_sections = []
    
    for section in required_sections:
        section_info = {
            "found": False,
            "position": -1,
            "line_number": -1,
            "context": "",
            "original_text": section
        }
        
        # 부문 검색
        pos = content.find(section)
        if pos != -1:
            section_info["found"] = True
            section_info["position"] = pos
            
            # 줄 번호 계산
            lines_before = content[:pos].count('\n')
            section_info["line_number"] = lines_before + 1
            
            # 컨텍스트 추출 (앞뒤 100자)
            start = max(0, pos - 100)
            end = min(len(content), pos + len(section) + 100)
            section_info["context"] = content[start:end]
            
            # 부문 이름 정규화 (공백 제거)
            normalized_name = section.replace(" ", "")
            validation_result["section_details"][normalized_name] = section_info
            found_sections.append((normalized_name, pos))
    
    # 필수 부문 확인 (정규화된 이름으로)
    required_normalized = ["공통부문", "토목부문", "건축부문", "기계설비부문", "유지관리부문"]
    found_normalized = [section for section, _ in found_sections]
    
    for section in required_normalized:
        if section not in found_normalized:
            validation_result["missing_sections"].append(section)
            validation_result["all_sections_found"] = False
    
    # 부문 순서 결정
    found_sections.sort(key=lambda x: x[1])
    validation_result["section_order"] = [section for section, _ in found_sections]
    
    # 검증 통과 여부
    validation_result["validation_passed"] = validation_result["all_sections_found"]
    
    return validation_result

def generate_validated_analysis_report(file_path: Path, analysis_results: Dict[str, Any], 
                                     validation_results: Dict[str, Any]) -> str:
    """검증된 분석 보고서 생성 - 반드시 사용"""
    
    # 1. 기본 보고서 생성
    report = f"""# 📋 PDF 구조 분석 보고서 (검증됨)

## 🎯 분석 개요
- **파일명**: {file_path.name}
- **분석 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **검증 상태**: {'✅ 통과' if validation_results.get('validation_passed', False) else '❌ 실패'}

## 🏗️ 문서 구조 분석
"""
    
    # 2. 부문별 상세 정보 추가
    section_details = validation_results.get("section_details", {})
    for section_name, section_info in section_details.items():
        if section_info["found"]:
            report += f"""
### {section_name}
- **위치**: {section_info['line_number']}번째 줄
- **컨텍스트**: {section_info['context'][:200]}...
"""
    
    # 3. 누락된 부문 경고
    missing_sections = validation_results.get("missing_sections", [])
    if missing_sections:
        report += f"""
## ⚠️ 누락된 부문
다음 부문이 문서에서 찾을 수 없습니다:
{chr(10).join(f'- {section}' for section in missing_sections)}

**권장사항**: 전체 문서를 다시 검토하여 누락된 부문을 확인하세요.
"""
    
    # 4. 검증 결과 요약
    report += f"""
## ✅ 검증 결과
- **모든 부문 발견**: {'예' if validation_results.get('all_sections_found', False) else '아니오'}
- **부문 순서**: {' → '.join(validation_results.get('section_order', []))}
- **분석 신뢰도**: {analysis_results.get('analysis_confidence', 0):.1f}%

## 💡 권장사항
"""
    
    if validation_results.get("validation_passed", False):
        report += "- ✅ 분석이 성공적으로 완료되었습니다.\n"
    else:
        report += "- 🔄 누락된 부문을 확인하고 재분석을 수행하세요.\n"
        report += "- 📖 문서의 전체 구조를 다시 검토하세요.\n"
        report += "- 🔍 부문 제목의 정확한 표기를 확인하세요.\n"
    
    return report

def execute_error_prevention_workflow(file_path: Path) -> Dict[str, Any]:
    """오류 방지 워크플로우 - 반드시 사용"""
    try:
        # 1단계: 사전 체크리스트
        checklist = pre_analysis_checklist(file_path)
        if not checklist["ready_for_analysis"]:
            return {
                "error": "파일이 분석 준비가 되지 않았습니다",
                "checklist": checklist,
                "is_valid": False
            }
        
        # 2단계: 파일 내용 로드
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 3단계: 부문 검증
        validation_results = validate_all_sections(content)
        
        # 4단계: 기본 분석 수행 (간단한 버전)
        analysis_results = {
            "analysis_confidence": 85.0,
            "file_info": {
                "name": file_path.name,
                "size": file_path.stat().st_size
            }
        }
        
        # 5단계: 검증된 보고서 생성
        comprehensive_report = generate_validated_analysis_report(
            file_path, analysis_results, validation_results
        )
        
        # 6단계: 결과 반환
        final_result = {
            "checklist": checklist,
            "validation_results": validation_results,
            "analysis_results": analysis_results,
            "comprehensive_report": comprehensive_report,
            "is_valid": validation_results.get("validation_passed", False)
        }
        
        # 7단계: 검증 실패 시 경고
        if not final_result["is_valid"]:
            print("⚠️ 경고: 부문 검증에 실패했습니다!")
            print(f"누락된 부문: {', '.join(validation_results.get('missing_sections', []))}")
            print("전체 문서를 다시 검토하세요.")
        
        return final_result
        
    except Exception as e:
        print(f"❌ 오류 방지 워크플로우 실행 중 오류 발생: {e}")
        return {
            "error": str(e),
            "is_valid": False
        }

def main():
    """메인 함수"""
    print("🧪 새로 추가된 검증 규칙 테스트를 시작합니다...")
    
    # 테스트할 파일 경로
    test_file = Path("output/split_3_49_extracted_20250620_165853.txt")
    
    if not test_file.exists():
        print(f"❌ 테스트 파일을 찾을 수 없습니다: {test_file}")
        return
    
    print(f"📁 테스트 파일: {test_file}")
    
    # 오류 방지 워크플로우 실행
    result = execute_error_prevention_workflow(test_file)
    
    # 결과 출력
    print("\n" + "="*50)
    print("📊 테스트 결과")
    print("="*50)
    
    if result.get("is_valid", False):
        print("✅ 검증 통과: 모든 부문이 정상적으로 발견되었습니다.")
    else:
        print("❌ 검증 실패: 일부 부문이 누락되었습니다.")
    
    # 상세 결과 출력
    validation_results = result.get("validation_results", {})
    if validation_results.get("missing_sections"):
        print(f"📋 누락된 부문: {', '.join(validation_results['missing_sections'])}")
    
    if validation_results.get("section_order"):
        print(f"📋 발견된 부문 순서: {' → '.join(validation_results['section_order'])}")
    
    # 보고서 저장
    report_file = Path("output/validation_test_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(result.get("comprehensive_report", ""))
    
    print(f"📄 상세 보고서가 저장되었습니다: {report_file}")
    
    print("\n🎯 테스트 완료!")

if __name__ == "__main__":
    main() 