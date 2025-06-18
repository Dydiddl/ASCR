# ASCR
Automation of Standard Construction Records

## 주요 기능
- PDF 파일의 부문/장별 자동 분류(실험 중)
- PDF 상단 헤더에서 장/부문 정보를 OCR로 추출
- Tesseract-OCR, EasyOCR 등 다양한 OCR 엔진 지원
- PDF → 이미지 변환(pdf2image), 이미지 전처리(OpenCV) 적용

## 설치 및 환경
- Python 3.8+
- 필수 패키지: requirements.txt 참고
- **Windows:** Tesseract-OCR, Poppler 설치 필요
- **Mac:** Poppler, Tesseract-OCR Homebrew로 설치 가능

### Mac에서의 추가 설치 및 설정
1. **Homebrew 설치** (설치되어 있지 않다면)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Poppler 설치**
   ```bash
   brew install poppler
   ```
3. **Tesseract-OCR 및 한글 데이터 설치**
   ```bash
   brew install tesseract
   brew install tesseract-lang  # 또는 아래 명령어로 한글 데이터만 추가
   wget https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata -P /usr/local/share/tessdata/
   ```
4. **경로 지정(필요시)**
   - poppler_path: `/usr/local/bin` 또는 `/opt/homebrew/bin`
   - tesseract_cmd: `/usr/local/bin/tesseract`

## 폴더 구조
```
ASCR/
  ├─ input/           # 원본 PDF 파일 저장 폴더
  ├─ output/          # 분류된 PDF, 결과물 저장 폴더
  ├─ src/
  │   ├─ classifier/  # PDF 분류 및 정보 추출 로직
  │   │   ├─ content_classifier.py
  │   │   └─ pdf_processor.py
  │   └─ utils/       # OCR 등 유틸리티 함수
  │       └─ ocr_header_extractor.py
  ├─ venv/            # 가상환경
  ├─ main.py          # 메인 실행 파일
  ├─ requirements.txt # 의존성 패키지 목록
  └─ README.md
```

## 사용법
1. `requirements.txt`의 패키지 설치  
   ```
   pip install -r requirements.txt
   ```
2. Tesseract-OCR, Poppler 설치 및 환경 변수 등록
3. `main.py` 실행 후 안내에 따라 PDF 경로 입력

## 참고
- OCR 인식률 향상을 위해 이미지 전처리(이진화 등) 적용
- EasyOCR, pytesseract 모두 지원(코드에서 선택 가능)
