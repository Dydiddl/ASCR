from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import numpy as np
import cv2
from tqdm import tqdm
import os

def preprocess_for_ocr(pil_img):
    """OCR을 위한 이미지 전처리를 수행합니다."""
    # PIL 이미지를 OpenCV 이미지로 변환
    img = np.array(pil_img)
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # 노이즈 제거
    img = cv2.medianBlur(img, 3)
    
    # 이진화 (적응형 임계값)
    img_bin = cv2.adaptiveThreshold(
        img, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )
    
    # 모폴로지 연산으로 노이즈 제거
    kernel = np.ones((2,2), np.uint8)
    img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_CLOSE, kernel)
    
    return Image.fromarray(img_bin)

def extract_header_texts(pdf_path: str, dpi: int = 300) -> list:
    """PDF 파일에서 각 페이지의 헤더 텍스트를 추출합니다."""
    print("\n=== OCR 처리 시작 ===")
    
    # Poppler 경로 확인
    poppler_bin_path = r'C:\poppler\Library\bin'
    if not os.path.exists(poppler_bin_path):
        raise FileNotFoundError(f"Poppler가 설치되지 않았습니다. 설치 경로: {poppler_bin_path}")
    
    # Tesseract 경로 확인
    tesseract_cmd = r'C:\Users\dydid\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    if not os.path.exists(tesseract_cmd):
        raise FileNotFoundError(f"Tesseract가 설치되지 않았습니다. 설치 경로: {tesseract_cmd}")
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    print("1. PDF 페이지 이미지 변환 중...")
    pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_bin_path)
    total_pages = len(pages)
    print(f"   - 총 {total_pages}페이지 변환 완료")
    
    print("\n2. 헤더 텍스트 추출 중...")
    header_texts = []
    for i, page_img in tqdm(enumerate(pages), total=total_pages, desc="   진행률"):
        # 헤더 영역 추출 (페이지 상단 10%)
        width, height = page_img.size
        header_box = (0, 0, width, int(height * 0.1))
        header_img = page_img.crop(header_box)
        
        # 이미지 전처리
        header_img = preprocess_for_ocr(header_img)
        
        # OCR 수행
        try:
            header_text = pytesseract.image_to_string(header_img, lang='kor+eng')
            header_text = header_text.strip()
            header_texts.append(header_text)
        except Exception as e:
            print(f"\n   - {i+1}페이지 OCR 처리 중 오류 발생: {str(e)}")
            header_texts.append("")
            
    print("\n=== OCR 처리 완료 ===\n")
    return header_texts


# easyocr 사용 하는 것도 고려할 것
