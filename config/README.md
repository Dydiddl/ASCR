# 설정 디렉토리

이 디렉토리는 프로젝트의 모든 설정 파일들을 관리합니다.

## 파일 구조

```
config/
├── __init__.py          # Python 패키지 초기화 파일
├── settings.py          # 설정 관리 모듈
├── mapping_config.json  # 수동 매핑 규칙 설정 파일
└── README.md           # 이 파일
```

## 설정 파일 설명

### mapping_config.json
- **용도**: PDF 분류를 위한 수동 매핑 규칙 정의
- **내용**: 장 패턴, 부문 패턴, 특수 케이스 매핑
- **형식**: JSON
- **인코딩**: UTF-8

### settings.py
- **용도**: 프로젝트 전체 설정 관리
- **기능**: 
  - 디렉토리 경로 관리
  - 설정 파일 경로 관리
  - 기본 설정값 정의

## 설정 파일 수정 방법

### 1. 직접 편집
`mapping_config.json` 파일을 텍스트 에디터로 직접 편집할 수 있습니다.

### 2. 프로그램을 통한 편집
```python
from src.utils.lookup_table import LookupTable

lookup = LookupTable()
lookup.add_mapping_rule("chapter", "제21장", "21", "", "신기술")
```

## 주의사항

1. **인코딩**: 모든 설정 파일은 UTF-8 인코딩으로 저장해야 합니다.
2. **JSON 형식**: `mapping_config.json`은 유효한 JSON 형식을 유지해야 합니다.
3. **백업**: 설정 파일 수정 전에 백업을 권장합니다.
4. **문법**: JSON 파일에서 쉼표, 따옴표 등의 문법을 정확히 지켜야 합니다.

## 설정 파일 위치 변경

설정 파일의 위치를 변경하려면 `config/settings.py` 파일의 경로 설정을 수정하세요:

```python
MAPPING_CONFIG_FILE = CONFIG_DIR / "your_new_path.json"
``` 