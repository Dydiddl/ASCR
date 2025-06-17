"""
PDF 파일을 머릿말 번호를 기준으로 분할하는 모듈

주요 기능:
1. 문서 초반의 목차 페이지들을 하나의 PDF로 통합
2. 페이지 상단 3-5cm 영역의 머릿말 번호를 기준으로 페이지 그룹화
3. 그룹화된 페이지들을 개별 PDF 파일로 저장

사용 예시:
    from pdf_chapter_extractor import extract_chapters_by_toc
    
    input_pdf = "example.pdf"
    output_dir = "extracted_chapters"
    extract_chapters_by_toc(input_pdf, output_dir)
"""

import os
import re
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def sanitize_filename(filename):
    """파일명에서 특수문자를 안전한 문자로 대체"""
    # 파일명으로 사용할 수 없는 문자들을 대체
    unsafe_chars = {
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '_',
        '<': '_',
        '>': '_',
        '|': '_',
        '(': '_',
        ')': '_'
    }
    safe_filename = filename
    for unsafe, safe in unsafe_chars.items():
        safe_filename = safe_filename.replace(unsafe, safe)
    return safe_filename

def is_common_section(title):
    """공통부문인지 확인"""
    return '공통부문' in title

def merge_common_sections(reader, start_page, end_page, output_dir):
    """공통부문 페이지들을 하나의 PDF로 병합"""
    writer = PdfWriter()
    for page_num in range(start_page, end_page):
        writer.add_page(reader.pages[page_num])
    
    output_filename = "공통부문.pdf"
    output_path = os.path.join(output_dir, output_filename)
    
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

def clean_title(title):
    """제목을 깔끔하게 정리"""
    # 숫자와 공백 제거
    title = re.sub(r'^\d+[\s_]*', '', title)
    # 중복 공백 제거
    title = re.sub(r'\s+', ' ', title)
    # 앞뒤 공백 제거
    return title.strip()

def normalize_title(title):
    """목차 제목을 정규화"""
    # 점(.) 또는 공백이 3개 이상 연속된 부분 제거
    title = re.sub(r'[.·\s]{3,}.*$', '', title)
    # 숫자와 공백을 제거하고 문자만 남김
    title = re.sub(r'\d+[-\s]*', '', title)
    # 공백 정리
    title = re.sub(r'\s+', ' ', title)
    return title.strip()

def extract_text_from_header(page):
    """
    페이지 상단 3-5cm 영역에서 텍스트 추출
    
    Args:
        page: pdfplumber Page 객체
    
    Returns:
        str: 추출된 텍스트
    """
    # 3cm ≈ 85 points, 5cm ≈ 142 points
    header_height = 142  # 약 5cm
    min_height = 85     # 약 3cm
    
    height = page.height
    width = page.width
    
    # 상단 영역 추출 (전체 너비, 상단 3-5cm)
    header = page.crop((0, height-header_height, width, height-min_height))
    
    if header:
        return header.extract_text() or ""
    return ""

def parse_header_text(text):
    """
    머릿말 텍스트에서 장 번호 추출
    
    Args:
        text (str): 추출된 머릿말 텍스트
    
    Returns:
        tuple: (chapter_num, chapter_title) 또는 (None, None)
    """
    if not text:
        return None, None
    
    # 패턴 1: "숫자 제목" 형식 (왼쪽 정렬)
    pattern1 = r'^\s*(\d+(?:-\d+)?)\s+'
    # 패턴 2: "제목 숫자" 형식 (오른쪽 정렬)
    pattern2 = r'\s+(\d+(?:-\d+)?)\s*$'
    
    # 패턴 1 확인
    match = re.search(pattern1, text, re.MULTILINE)
    if match:
        return match.group(1), None
    
    # 패턴 2 확인
    match = re.search(pattern2, text, re.MULTILINE)
    if match:
        return match.group(1), None
    
    return None, None

def extract_chapter_pages(reader):
    """PDF에서 장 시작 페이지 추출"""
    chapter_pages = []
    current_chapter = None
    
    # pdfplumber로 PDF 열기
    with pdfplumber.open(reader.stream) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # 상단 영역 텍스트 추출
            header_text = extract_text_from_header(page)
            
            # 장 번호와 제목 추출
            chapter_num, chapter_title = parse_header_text(header_text)
            
            if chapter_num and chapter_title:
                chapter_key = f"{chapter_num}_{chapter_title}"
                
                # 새로운 장이 시작될 때만 페이지 추가
                if chapter_key != current_chapter:
                    current_chapter = chapter_key
                    chapter_pages.append((page_num, chapter_num, chapter_title))
                    print(f"장 발견: {chapter_num} - {chapter_title} (페이지 {page_num+1})")
                    print(f"원본 텍스트: {header_text.strip()}")
    
    return chapter_pages

def is_toc_page(text):
    """목차 페이지인지 확인"""
    # "목 차", "차 례" 등의 패턴 확인
    toc_patterns = [
        r'목\s*차',
        r'차\s*례',
        r'contents',
        r'table of contents'
    ]
    text_lower = text.lower()
    return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in toc_patterns)

def merge_toc_pages(reader, output_dir):
    """
    문서 초반의 목차 페이지들을 하나로 통합
    
    Args:
        reader: PdfReader 객체
        output_dir (str): 출력 디렉토리 경로
    
    Returns:
        list: 목차 페이지 번호 리스트
    """
    writer = PdfWriter()
    toc_pages = []
    
    with pdfplumber.open(reader.stream) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if is_toc_page(text):
                toc_pages.append(page_num)
                logging.info(f"목차 페이지 발견: {page_num + 1}")
            elif toc_pages:  # 목차가 아닌 페이지를 만나면 중단
                break
    
    if toc_pages:
        for page_num in toc_pages:
            writer.add_page(reader.pages[page_num])
        
        output_filename = "00_목차.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
            
        logging.info(f"목차 통합 완료: {output_filename} (페이지: {toc_pages[0]+1}-{toc_pages[-1]+1})")
    else:
        logging.warning("목차 페이지를 찾을 수 없습니다.")
    
    return toc_pages

def extract_header_number(page):
    """페이지 상단 3-5cm 영역에서 머릿말 번호 추출"""
    # 3cm ≈ 85 points, 5cm ≈ 142 points
    height = page.height
    header = page.crop((0, height-142, page.width, height-85))
    
    if not header:
        return None
        
    text = header.extract_text() or ""
    
    # 패턴 1: "숫자 제목" 형식
    pattern1 = r'^\s*(\d+(?:-\d+)?)\s+'
    # 패턴 2: "제목 숫자" 형식
    pattern2 = r'\s+(\d+(?:-\d+)?)\s*$'
    
    match = re.search(pattern1, text) or re.search(pattern2, text)
    return match.group(1) if match else None

def extract_chapters_by_toc(pdf_path, output_dir):
    """
    PDF 파일을 머릿말 번호 기준으로 분할
    
    Args:
        pdf_path (str): 입력 PDF 파일 경로
        output_dir (str): 출력 디렉토리 경로
    
    Returns:
        int: 변환된 페이지 수
    """
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(pdf_path)
    
    total_pages = len(reader.pages)
    logging.info(f"PDF 전체 페이지 수: {total_pages}")
    
    # 목차 페이지 처리
    toc_pages = merge_toc_pages(reader, output_dir)
    
    # 페이지 그룹화
    current_number = None
    current_pages = []
    chapter_groups = []
    converted_pages = set(toc_pages)  # 목차 페이지도 변환된 것으로 처리
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(len(pdf.pages)):
            if page_num in toc_pages:
                continue
                
            header_num = extract_header_number(pdf.pages[page_num])
            
            if header_num:
                if header_num != current_number:
                    if current_pages:
                        chapter_groups.append((current_number, current_pages))
                        logging.info(f"챕터 그룹 생성: {current_number}, 페이지 수: {len(current_pages)}")
                    current_number = header_num
                    current_pages = [page_num]
                else:
                    current_pages.append(page_num)
                converted_pages.add(page_num)
    
    # 마지막 그룹 추가
    if current_pages:
        chapter_groups.append((current_number, current_pages))
        logging.info(f"마지막 챕터 그룹 생성: {current_number}, 페이지 수: {len(current_pages)}")
    
    # PDF 파일 생성
    for i, (number, pages) in enumerate(chapter_groups, 1):
        writer = PdfWriter()
        for page_num in pages:
            writer.add_page(reader.pages[page_num])
        
        output_filename = f"{str(i).zfill(2)}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        logging.info(f"파일 생성 완료: {output_filename} (원본 번호: {number}, 페이지: {pages[0]+1}-{pages[-1]+1})")
    
    # 결과 요약
    converted_count = len(converted_pages)
    logging.info(f"PDF 변환 페이지 수: {converted_count}")
    
    if converted_count < total_pages:
        unconverted = sorted(set(range(total_pages)) - converted_pages)
        logging.warning(f"주의: {total_pages - converted_count}개의 페이지가 변환되지 않았습니다.")
        logging.warning(f"변환되지 않은 페이지: {[p+1 for p in unconverted]}")
    
    return converted_count

def find_chapter_starts(pdf_path):
    """
    각 장의 시작 페이지를 찾습니다.
    """
    chapter_starts = []
    chapter_pattern = re.compile(r'제\s*(\d+)\s*장')
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                # 장 시작 패턴 찾기
                if chapter_pattern.search(text):
                    chapter_starts.append(page_num)
    
    return chapter_starts

if __name__ == "__main__":
    input_pdf = "example.pdf"
    output_directory = "extracted_chapters"
    
    try:
        logging.info(f"'{input_pdf}' 파일 처리 시작...")
        converted = extract_chapters_by_toc(input_pdf, output_directory)
        logging.info(f"작업 완료. 총 {converted}개 페이지 변환됨.")
    except Exception as e:
        logging.error(f"오류 발생: {str(e)}", exc_info=True) 