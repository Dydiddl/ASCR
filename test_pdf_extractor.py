import os
import unittest
import traceback
import time
from datetime import datetime
from pdf_chapter_extractor import extract_chapters_by_toc

class TestPDFExtractor(unittest.TestCase):
    def setUp(self):
        # 테스트에 사용할 디렉토리 설정
        self.input_dir = "input"
        self.output_dir = "input/edit"
        
        # 출력 디렉토리가 없으면 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        print("\n=== PDF 분할 테스트 시작 ===")
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def test_pdf_chapter_extraction(self):
        """PDF 장 분할 테스트"""
        # input 디렉토리의 모든 PDF 파일 처리
        pdf_files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print("경고: input 디렉토리에 PDF 파일이 없습니다.")
            return
        
        print(f"\n처리할 PDF 파일 수: {len(pdf_files)}")
        
        for pdf_file in pdf_files:
            input_path = os.path.join(self.input_dir, pdf_file)
            print(f"\n{'='*50}")
            print(f"파일 처리 시작: {pdf_file}")
            print(f"시작 시간: {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                # PDF 분할 실행
                start_time = time.time()
                extract_chapters_by_toc(input_path, self.output_dir)
                end_time = time.time()
                
                # 결과 확인
                output_files = os.listdir(self.output_dir)
                self.assertTrue(len(output_files) > 0, f"{pdf_file}에 대한 분할된 파일이 생성되지 않았습니다.")
                
                print(f"\n처리 완료: {pdf_file}")
                print(f"소요 시간: {end_time - start_time:.2f}초")
                print(f"생성된 파일 수: {len(output_files)}")
                print("\n생성된 파일 목록:")
                for output_file in output_files:
                    print(f"- {output_file}")
                
            except Exception as e:
                print(f"\n오류 발생: {str(e)}")
                print("상세 오류 정보:")
                print(traceback.format_exc())
                self.fail(f"{pdf_file} 처리 중 오류 발생: {str(e)}")
    
    def tearDown(self):
        """테스트 후 정리 작업"""
        print(f"\n=== 테스트 종료 ===")
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 