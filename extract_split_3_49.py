#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_3_49.pdf 텍스트 추출 스크립트
조건:
1. 페이지별로 텍스트 추출 (1페이지, 2페이지...)
2. 페이지 끝에 ---- 구분자 추가
3. 줄별로 번호 매기기 (1줄, 2줄...)
"""

from pathlib import Path
from src.utils.pdf_text_extractor import PDFTextExtractor

def extract_split_3_49_pdf():
    """split_3_49.pdf 파일을 요청된 조건에 맞게 처리"""
    
    # PDF 파일 경로
    pdf_path = Path("input/split_3_49.pdf")
    
    # 텍스트 추출기 생성
    extractor = PDFTextExtractor()
    
    print("=== split_3_49.pdf 텍스트 추출 시작 ===")
    
    # PDF 정보 확인
    info = extractor.get_pdf_info(pdf_path)
    print(f"파일명: {info.get('파일명', 'N/A')}")
    print(f"총 페이지 수: {info.get('총_페이지_수', 'N/A')}")
    print(f"파일 크기: {info.get('파일_크기', 'N/A')}")
    print()
    
    # 요청된 조건에 맞게 텍스트 추출
    # 1. 페이지별로 텍스트 추출
    # 2. 페이지 끝에 ---- 구분자 추가  
    # 3. 줄별로 번호 매기기
    result_path = extractor.extract_text_with_options(
        pdf_path=pdf_path,
        include_page_numbers=True,  # 1페이지, 2페이지...
        include_line_numbers=True,  # 1줄, 2줄...
        page_separator="----",      # 페이지 구분자
        output_filename="split_3_49_extracted.txt"
    )
    
    if result_path:
        print(f"✅ 텍스트 추출 완료!")
        print(f"📁 출력 파일: {result_path}")
        
        # 결과 파일 정보 확인
        result_file = Path(result_path)
        if result_file.exists():
            file_size = result_file.stat().st_size / 1024  # KB
            print(f"📊 파일 크기: {file_size:.1f} KB")
            
            # 파일 내용 미리보기 (처음 10줄)
            print("\n=== 파일 내용 미리보기 (처음 10줄) ===")
            with open(result_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i < 10:
                        print(line.rstrip())
                    else:
                        break
            print("...")
    else:
        print("❌ 텍스트 추출 실패")

if __name__ == "__main__":
    extract_split_3_49_pdf() 