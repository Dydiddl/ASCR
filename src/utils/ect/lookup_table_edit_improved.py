#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 목차에서 룩업 테이블 생성 (개선된 버전)
"""

import fitz  # PyMuPDF
import pandas as pd
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional

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

def create_lookup_table(entries: List[Dict]) -> pd.DataFrame:
    """
    목차 항목들로부터 룩업 테이블을 생성합니다.
    
    Args:
        entries: 목차 항목들의 리스트
        
    Returns:
        룩업 테이블 DataFrame
    """
    if not entries:
        print("경고: 처리할 목차 항목이 없습니다.")
        return pd.DataFrame()
    
    # DataFrame 생성
    df = pd.DataFrame(entries)
    
    # 계층 분리
    print("계층 구조 분리 중...")
    levels_df = df["번호"].apply(extract_levels).apply(pd.Series)
    
    # 원본 데이터와 계층 정보 결합
    result_df = pd.concat([df, levels_df], axis=1)
    
    # 컬럼 순서 정리
    column_order = ["번호", "대분류", "중분류", "소분류", "제목", "페이지", "발견페이지", "발견라인"]
    result_df = result_df.reindex(columns=column_order)
    
    return result_df

def save_lookup_table(df: pd.DataFrame, output_path: Path) -> bool:
    """
    룩업 테이블을 파일로 저장합니다.
    
    Args:
        df: 저장할 DataFrame
        output_path: 저장할 파일 경로
        
    Returns:
        저장 성공 여부
    """
    try:
        # Excel 파일로 저장
        df.to_excel(output_path, index=False)
        print(f"룩업 테이블이 저장되었습니다: {output_path}")
        
        # CSV 파일로도 저장 (백업용)
        csv_path = output_path.with_suffix('.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"CSV 백업 파일도 저장되었습니다: {csv_path}")
        
        return True
        
    except Exception as e:
        print(f"오류: 파일 저장 중 오류 발생: {e}")
        return False

def analyze_lookup_table(df: pd.DataFrame) -> None:
    """
    생성된 룩업 테이블을 분석합니다.
    
    Args:
        df: 분석할 DataFrame
    """
    if df.empty:
        print("분석할 데이터가 없습니다.")
        return
    
    print("\n=== 룩업 테이블 분석 결과 ===")
    print(f"총 항목 수: {len(df)}")
    
    # 대분류별 통계
    if "대분류" in df.columns:
        print(f"\n대분류별 항목 수:")
        for category, count in df["대분류"].value_counts().items():
            print(f"  {category}: {count}개")
    
    # 페이지 범위
    if "페이지" in df.columns:
        min_page = df["페이지"].min()
        max_page = df["페이지"].max()
        print(f"\n페이지 범위: {min_page} - {max_page}")
    
    # 계층 깊이 분석
    if "번호" in df.columns:
        depths = df["번호"].str.count("-") + 1
        print(f"\n계층 깊이별 항목 수:")
        for depth, count in depths.value_counts().sort_index().items():
            print(f"  {depth}단계: {count}개")

def main():
    """메인 함수"""
    print("=== PDF 목차에서 룩업 테이블 생성 ===")
    
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
    
    # 룩업 테이블 생성
    print("\n2. 룩업 테이블 생성 중...")
    df = create_lookup_table(entries)
    
    # 분석
    analyze_lookup_table(df)
    
    # 파일 저장
    print("\n3. 파일 저장 중...")
    output_path = OUTPUT_DIR / "lookup_table_from_pdf.xlsx"
    if save_lookup_table(df, output_path):
        print("\n=== 룩업 테이블 생성 완료 ===")
        print(f"저장 위치: {output_path}")
    else:
        print("\n=== 룩업 테이블 생성 실패 ===")

if __name__ == "__main__":
    main() 