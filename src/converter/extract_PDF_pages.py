import os
from pypdf import PdfReader, PdfWriter

def extract_pdf_pages(input_path, output_path, start_page, end_page):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for i in range(start_page - 1, end_page):
        writer.add_page(reader.pages[i])
    with open(output_path, "wb") as output_file:
        writer.write(output_file)

def extract_pages_interactive():
    input_path = input("원본 PDF 경로를 입력하세요: ").strip()
    output_dir = input("분할된 PDF를 저장할 폴더 경로를 입력하세요: ").strip()
    ranges = []
    idx = 1
    while True:
        start = int(input(f"{idx}. 추출할 첫 페이지를 입력하세요: "))
        end = int(input(f"{idx}. 추출할 마지막 페이지를 입력하세요: "))
        ranges.append((start, end))
        cont = input("계속 입력하시겠습니까? (y/n): ").strip().lower()
        if cont != "y":
            break
        idx += 1

    for i, (start, end) in enumerate(ranges, 1):
        output_path = os.path.join(output_dir, f"split_{start}_{end}.pdf")
        extract_pdf_pages(input_path, output_path, start, end)
        print(f"{start}~{end}페이지 추출 완료: {output_path}")