from src.converter.extract_PDF_pages import extract_pages_interactive

def main():
    print("어떤 작업을 하시겠습니까??")
    print("1. Extract pages")
    # 추후 기능 추가 시 아래에 elif로 확장
    job = input("작업명을 입력하세요: ").strip().lower()
    if job in ["extract pages", "1"]:
        extract_pages_interactive()
    else:
        print("알 수 없는 작업입니다.")

if __name__ == "__main__":
    main()