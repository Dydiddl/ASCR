#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
설정 관리 모듈
"""

import os
from pathlib import Path
from typing import List, Dict, Optional

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent

# 설정 파일 경로
CONFIG_DIR = PROJECT_ROOT / "config"
MAPPING_CONFIG_FILE = CONFIG_DIR / "mapping_config.json"

# 입력/출력 디렉토리
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

# 기본 설정
DEFAULT_ENCODING = "utf-8"
DEFAULT_USE_LOOKUP_TABLE = True

# PDF 처리 설정
PDF_SETTINGS = {
    "max_pages_per_file": 1000,
    "supported_formats": [".pdf"],
    "temp_dir": PROJECT_ROOT / "temp",
    "log_dir": PROJECT_ROOT / "logs"
}

# OCR 설정
OCR_SETTINGS = {
    "tesseract_path": None,  # 자동 감지
    "poppler_path": None,    # 자동 감지
    "language": "kor+eng",
    "confidence_threshold": 60
}

# 로깅 설정
LOGGING_SETTINGS = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": PROJECT_ROOT / "logs" / "app.log"
}

# 디렉토리 생성
def ensure_directories():
    """필요한 디렉토리들을 생성합니다."""
    directories = [
        CONFIG_DIR, 
        INPUT_DIR, 
        OUTPUT_DIR,
        PDF_SETTINGS["temp_dir"],
        PDF_SETTINGS["log_dir"]
    ]
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"디렉토리 생성/확인: {directory}")

# 설정 파일 경로 확인
def get_mapping_config_path() -> Path:
    """매핑 설정 파일 경로를 반환합니다."""
    return MAPPING_CONFIG_FILE

# 설정 파일 존재 확인
def config_file_exists() -> bool:
    """매핑 설정 파일이 존재하는지 확인합니다."""
    return MAPPING_CONFIG_FILE.exists()

# 입력 파일 목록 가져오기
def get_input_files(extension: str = ".pdf") -> List[Path]:
    """입력 디렉토리에서 특정 확장자의 파일들을 가져옵니다."""
    if not INPUT_DIR.exists():
        return []
    return list(INPUT_DIR.glob(f"*{extension}"))

# 출력 디렉토리 정리
def clean_output_directory():
    """출력 디렉토리의 임시 파일들을 정리합니다."""
    if not OUTPUT_DIR.exists():
        return
    
    # 임시 파일들 삭제
    temp_patterns = ["*.tmp", "*.temp", "~*"]
    for pattern in temp_patterns:
        for file in OUTPUT_DIR.glob(pattern):
            try:
                file.unlink()
                print(f"임시 파일 삭제: {file}")
            except Exception as e:
                print(f"파일 삭제 실패: {file} - {e}")

# 환경 설정 확인
def check_environment() -> Dict[str, bool]:
    """프로젝트 실행에 필요한 환경을 확인합니다."""
    checks = {
        "project_root_exists": PROJECT_ROOT.exists(),
        "config_dir_exists": CONFIG_DIR.exists(),
        "input_dir_exists": INPUT_DIR.exists(),
        "output_dir_exists": OUTPUT_DIR.exists(),
        "mapping_config_exists": config_file_exists(),
        "python_version_ok": True  # Python 3.7+ 확인 로직 추가 가능
    }
    return checks

# 설정 정보 출력
def print_settings_info():
    """현재 설정 정보를 출력합니다."""
    print("=== 프로젝트 설정 정보 ===")
    print(f"프로젝트 루트: {PROJECT_ROOT}")
    print(f"설정 디렉토리: {CONFIG_DIR}")
    print(f"입력 디렉토리: {INPUT_DIR}")
    print(f"출력 디렉토리: {OUTPUT_DIR}")
    print(f"매핑 설정 파일: {MAPPING_CONFIG_FILE}")
    print(f"기본 인코딩: {DEFAULT_ENCODING}")
    print(f"룩업 테이블 사용: {DEFAULT_USE_LOOKUP_TABLE}")
    
    # 환경 확인
    print("\n=== 환경 확인 ===")
    checks = check_environment()
    for check_name, status in checks.items():
        status_symbol = "✓" if status else "✗"
        print(f"{status_symbol} {check_name}: {status}")

# 설정 파일 백업
def backup_config_file():
    """설정 파일을 백업합니다."""
    if not config_file_exists():
        print("백업할 설정 파일이 없습니다.")
        return
    
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CONFIG_DIR / f"mapping_config_backup_{timestamp}.json"
    
    try:
        shutil.copy2(MAPPING_CONFIG_FILE, backup_path)
        print(f"설정 파일 백업 완료: {backup_path}")
    except Exception as e:
        print(f"백업 실패: {e}")

# 설정 파일 복원
def restore_config_file(backup_file: str):
    """백업 파일에서 설정을 복원합니다."""
    backup_path = CONFIG_DIR / backup_file
    
    if not backup_path.exists():
        print(f"백업 파일을 찾을 수 없습니다: {backup_path}")
        return
    
    import shutil
    
    try:
        shutil.copy2(backup_path, MAPPING_CONFIG_FILE)
        print(f"설정 파일 복원 완료: {backup_file}")
    except Exception as e:
        print(f"복원 실패: {e}") 