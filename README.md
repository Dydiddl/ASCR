# ASCR (Automated Standard Construction Reference)
건설업계 표준 문서 자동화 처리 시스템

## 주요 기능
- **PDF 파일 자동 분류**: 부문별, 장별 자동 분류
- **PDF 디버그 분석**: PDF 내용 추출 및 분석
- **룩업테이블 생성**: PDF 목차를 구조화된 테이블로 변환
- **매핑 설정 자동화**: 룩업테이블을 기반으로 매핑 설정 생성
- **PDF 페이지 분리**: 지정된 페이지 범위로 PDF 분리
- **PDF 파일 병합**: 분리된 PDF 파일들을 병합

## 설치 및 환경
- Python 3.8+
- 필수 패키지: requirements.txt 참고

### 설치 방법
1. **저장소 클론**
   ```bash
   git clone [repository-url]
   cd ASCR
   ```

2. **가상환경 생성 및 활성화**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   # 또는
   venv\Scripts\activate     # Windows
   ```

3. **의존성 패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

## 폴더 구조
```
ASCR/
  ├─ input/           # 원본 PDF 파일 저장 폴더
  ├─ output/          # 분류된 PDF, 결과물 저장 폴더
  ├─ config/          # 설정 파일들
  │   ├─ mapping_config.json
  │   └─ settings.py
  ├─ src/
  │   ├─ classifier/  # PDF 분류 및 처리 로직
  │   │   ├─ content_classifier.py
  │   │   └─ pdf_processor.py
  │   ├─ converter/   # PDF 변환 도구
  │   │   └─ extract_PDF_pages.py
  │   └─ utils/       # 유틸리티 함수들
  │       ├─ lookup_table.py
  │       ├─ pdf_merger.py
  │       ├─ pdf_to_lookup_table.py
  │       └─ ect/
  │           └─ pdf_debug.py
  ├─ venv/            # 가상환경
  ├─ main.py          # 메인 실행 파일
  ├─ requirements.txt # 의존성 패키지 목록
  └─ README.md
```

## 사용법

### 1. 메인 프로그램 실행
```bash
python main.py
```

### 2. 주요 기능 메뉴
- **자동 분류**: PDF를 부문별, 장별로 자동 분류
- **페이지 지정 분리**: 특정 페이지 범위로 PDF 분리
- **PDF 파일 병합**: 분리된 PDF 파일들을 병합
- **프로젝트 정보 보기**: 현재 프로젝트 상태 확인
- **PDF 디버그 파일을 룩업테이블로 변환**: PDF 내용을 구조화된 테이블로 변환
- **룩업테이블을 매핑 설정으로 변환**: 룩업테이블을 기반으로 매핑 설정 생성

### 3. 워크플로우 예시

#### PDF 분석 및 룩업테이블 생성
1. PDF 파일을 `input/` 폴더에 배치
2. 메인 프로그램에서 "PDF 디버그 파일을 룩업테이블로 변환" 선택
3. 생성된 룩업테이블 확인 (`output/lookup_table_*.csv`)

#### 매핑 설정 생성
1. 생성된 룩업테이블을 기반으로 매핑 설정 생성
2. 메인 프로그램에서 "룩업테이블을 매핑 설정으로 변환" 선택
3. 새로운 매핑 설정 파일 확인 (`config/mapping_config_*.json`)

## 설정 파일

### mapping_config.json
PDF 분류를 위한 매핑 규칙을 정의합니다:
```json
{
  "chapter_patterns": [
    {"pattern": "제1장", "chapter": "1", "title": "총칙"},
    {"pattern": "제2장", "chapter": "2", "title": "일반사항"}
  ],
  "section_patterns": [
    {"pattern": "01부문", "section": "01", "title": "준비공사"},
    {"pattern": "02부문", "section": "02", "title": "토공사"}
  ],
  "special_cases": {
    "첫페이지": {"chapter": "0", "section": "00", "title": "목차"}
  }
}
```

## 출력 파일 형식

### 룩업테이블 (CSV/Excel)
```
대분류,중분류,소분류,번호,제목,페이지
총칙,1부문,,1-1,일반사항,3
총칙,1부문,1,1-1-1,목적,3
```

## 의존성 패키지
- `pypdf`: PDF 파일 처리
- `pandas`: 데이터 처리 및 분석
- `openpyxl`: Excel 파일 생성
- `PyMuPDF`: PDF 텍스트 추출
- `tqdm`: 진행률 표시

## 참고사항
- PDF 텍스트 추출이 잘 되는 경우 OCR 없이도 충분히 정확한 분류가 가능합니다
- 매핑 설정은 프로젝트별로 커스터마이징 가능합니다
- 생성된 룩업테이블은 Excel과 CSV 형식으로 모두 저장됩니다

## 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다.
