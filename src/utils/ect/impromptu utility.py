# # 파일 경로 찾기 코드
# import os
# for root, dirs, files in os.walk('C:\\'):
#     if 'tesseract.exe' in files:
#         print(os.path.join(root, 'tesseract.exe'))


# 폴더안의 파일 이름 바꾸기 코드
import os
from pypdf import PdfReader
import re
import shutil

def sanitize_filename(text):
    text = re.sub(r'[\\/:*?"<>|]', '', text)  # 파일명에 쓸 수 없는 문자 제거
    text = text.strip()
    return text[:50]  # 너무 길면 50자 제한

def rename_pdfs_by_firstline(folder_path):
    # 폴더명에서 앞 숫자 추출 (예: 01_공통부문 → 01)
    folder_name = os.path.basename(folder_path)
    match = re.match(r'(\\d+)_', folder_name)
    folder_prefix = match.group(1) if match else folder_name

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    pdf_files.sort()  # 정렬(원하는 순서대로)

    for idx, fname in enumerate(pdf_files):
        input_pdf = os.path.join(folder_path, fname)
        reader = PdfReader(input_pdf)
        first_line = f"file_{idx+1}"
        if reader.pages:
            text = reader.pages[0].extract_text()
            if text:
                first_line = text.split('\n')[0]
        new_name = f"{folder_prefix}_{idx}_{sanitize_filename(first_line)}.pdf"
        new_path = os.path.join(folder_path, new_name)
        # 파일 이름 변경(덮어쓰기 방지)
        if not os.path.exists(new_path):
            shutil.move(input_pdf, new_path)
            print(f"{fname} → {new_name}")
        else:
            print(f"이미 존재: {new_name} (건너뜀)")

# 사용 예시
rename_pdfs_by_firstline("input/division/manual split/00_표지 및 목차")