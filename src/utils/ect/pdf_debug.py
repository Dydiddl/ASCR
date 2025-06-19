#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 내용 디버깅 도구
"""

import fitz
from pathlib import Path
from datetime import datetime

class PDFDebugger:
    """PDF 디버깅을 위한 클래스"""
    
    def __init__(self):
        pass
    
    def create_debug_file(self, pdf_path: str, max_pages: int = 10) -> str:
        """
        PDF 파일을 디버깅하여 텍스트 파일로 저장
        
        Args:
            pdf_path: PDF 파일 경로
            max_pages: 최대 처리할 페이지 수
            
        Returns:
            str: 생성된 디버그 파일 경로
        """
        return debug_pdf_content(Path(pdf_path), max_pages)

def debug_pdf_content(pdf_path: Path, max_pages: int = 10):
    """PDF 내용을 디버깅합니다."""
    
    # 출력 파일 경로
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("output") / f"pdf_debug_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        try:
            with fitz.open(str(pdf_path)) as doc:
                f.write(f"PDF 파일: {pdf_path}\n")
                f.write(f"총 페이지 수: {len(doc)}\n")
                
                for page_num in range(min(max_pages, len(doc))):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    
                    f.write(f"\n=== 페이지 {page_num + 1} ===\n")
                    f.write(f"텍스트 길이: {len(text)}\n")
                    
                    # 처음 1000자만 출력
                    preview = text[:1000]
                    f.write(f"미리보기:\n{preview}\n")
                    
                    # 줄별로 분석
                    lines = text.split('\n')
                    f.write(f"\n줄 수: {len(lines)}\n")
                    
                    # 각 줄의 내용 확인
                    for i, line in enumerate(lines[:20]):  # 처음 20줄만
                        if line.strip():
                            f.write(f"줄 {i+1}: '{line}'\n")
                    
                    f.write("\n" + "="*50 + "\n")
                    
        except Exception as e:
            f.write(f"오류 발생: {e}\n")
    
    print(f"디버그 결과가 {output_file}에 저장되었습니다.")
    return str(output_file)

if __name__ == "__main__":
    pdf_path = Path("input/split_3_49.pdf")
    debug_pdf_content(pdf_path, max_pages=5) 