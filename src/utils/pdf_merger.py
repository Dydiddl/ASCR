import os
from pathlib import Path
import re
import pypdf
from typing import Dict, List, Set

def merge_chapter_pdfs(output_dir: str = "output"):
    """같은 장의 PDF 파일들을 하나로 합칩니다."""
    output_path = Path(output_dir)
    if not output_path.exists():
        print("출력 디렉토리가 존재하지 않습니다.")
        return
        
    print("\n=== PDF 파일 병합 시작 ===")
    
    # 부문별로 처리
    for section_dir in output_path.iterdir():
        if not section_dir.is_dir() or section_dir.name.startswith('.'):
            continue
            
        print(f"\n{section_dir.name} 처리 중...")
        
        # 장별로 파일 그룹화
        chapter_files: Dict[str, List[Path]] = {}
        
        # 파일 패턴: 제X장_제목숫자.pdf
        chapter_pattern = re.compile(r'제(\d+)장_([^0-9]+).*?\.pdf')
        
        # 각 PDF 파일 확인
        for pdf_file in section_dir.glob("*.pdf"):
            match = chapter_pattern.match(pdf_file.name)
            if match:
                chapter_num = match.group(1)
                chapter_title = match.group(2).rstrip('_')
                key = f"제{chapter_num}장_{chapter_title}"
                
                if key not in chapter_files:
                    chapter_files[key] = []
                chapter_files[key].append(pdf_file)
                
        # 각 장별로 파일 병합
        for chapter_name, files in chapter_files.items():
            if len(files) <= 1:
                continue
                
            # 파일 이름순으로 정렬
            files.sort()
            
            try:
                # 새 PDF 생성
                merger = pypdf.PdfWriter()
                
                # 파일들을 순서대로 병합
                for file in files:
                    reader = pypdf.PdfReader(str(file))
                    for page in reader.pages:
                        merger.add_page(page)
                    
                # 병합된 파일 저장
                output_file = section_dir / f"{chapter_name}.pdf"
                with open(output_file, 'wb') as output:
                    merger.write(output)
                    
                print(f"  - {chapter_name}: {len(files)}개 파일 병합 완료")
                
                # 원본 파일 삭제
                for file in files:
                    file.unlink()
                    
            except Exception as e:
                print(f"  - {chapter_name} 병합 중 오류 발생: {str(e)}")
                continue
                
    print("\n=== PDF 파일 병합 완료 ===")

if __name__ == "__main__":
    merge_chapter_pdfs() 