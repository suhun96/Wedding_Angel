import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def read_config():
    """설정 파일에서 네이버 로그인 정보를 읽어옵니다."""
    try:
        with open('config.txt', 'r') as file:
            lines = file.readlines()
            naver_id = lines[0].strip()
            naver_pw = lines[1].strip()
        return naver_id, naver_pw
    except:
        print("로그인 정보를 읽어오는 데 실패했습니다. setup.bat을 다시 실행해주세요.")
        input("아무 키나 눌러 종료...")
        exit(1)

def setup_driver():
    """크롬 드라이버를 설정합니다."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("detach", True)  # 브라우저 자동 종료 방지
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"드라이버 설정 중 오류가 발생했습니다: {e}")
        input("아무 키나 눌러 종료...")
        exit(1)

def login_to_naver(driver, naver_id, naver_pw):
    """네이버에 로그인합니다."""
    try:
        print("네이버 로그인 페이지로 이동합니다...")
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(1)
        
        # 자바스크립트로 직접 ID와 비밀번호 입력 (봇 감지 우회)
        driver.execute_script(f"document.getElementsByName('id')[0].value='{naver_id}'")
        time.sleep(0.5)
        driver.execute_script(f"document.getElementsByName('pw')[0].value='{naver_pw}'")
        time.sleep(0.5)
        
        # 로그인 버튼 클릭
        print("로그인 중...")
        login_button = driver.find_element(By.ID, "log.login")
        login_button.click()
        
        # 로그인 성공 대기
        time.sleep(3)
        
        # 로그인 성공 여부 확인
        if "로그인" in driver.title:
            print("자동 로그인에 실패했습니다. 캡차 인증이 필요할 수 있습니다.")
            print("브라우저에서 직접 로그인을 완료해주세요.")
            input("로그인을 완료한 후 여기에서 Enter 키를 눌러주세요...")
        else:
            print("네이버 로그인 성공!")
            
    except Exception as e:
        print(f"로그인 중 오류가 발생했습니다: {e}")
        print("브라우저에서 직접 로그인을 완료해주세요.")
        input("로그인을 완료한 후 여기에서 Enter 키를 눌러주세요...")

def go_to_blog_search(driver, search_keyword):
    """블로그 검색 페이지로 이동하고 키워드를 검색합니다."""
    try:
        print(f"'{search_keyword}' 키워드로 블로그를 검색합니다...")
        driver.get(f"https://search.naver.com/search.naver?where=blog&query={search_keyword}")
        time.sleep(2)
    except Exception as e:
        print(f"검색 중 오류가 발생했습니다: {e}")

def crawl_blog_posts(driver, num_posts=10):
    """블로그 게시물 정보를 크롤링합니다."""
    blog_data = []
    
    try:
        print(f"최대 {num_posts}개의 블로그 포스트를 크롤링합니다...")
        
        # 블로그 리스트 가져오기
        blog_list = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.bx"))
        )
        
        for i, blog in enumerate(blog_list[:num_posts]):
            try:
                # 게시물 제목
                title_element = blog.find_element(By.CSS_SELECTOR, "a.title_link")
                title = title_element.text
                
                # 블로그 이름
                blogger_element = blog.find_element(By.CSS_SELECTOR, "a.sub_txt.sub_name")
                blogger = blogger_element.text
                
                # 게시일
                date_element = blog.find_element(By.CSS_SELECTOR, "span.sub_time")
                date = date_element.text
                
                # 포스트 URL
                post_url = title_element.get_attribute("href")
                
                # 결과 저장
                blog_data.append({
                    "제목": title,
                    "블로그명": blogger,
                    "작성일": date,
                    "URL": post_url
                })
                
                print(f"[{i+1}/{num_posts}] '{title}' 크롤링 완료")
                
            except Exception as e:
                print(f"게시물 크롤링 중 오류 발생: {e}")
                continue
                
        return blog_data
        
    except Exception as e:
        print(f"크롤링 중 오류가 발생했습니다: {e}")
        return blog_data

def save_to_excel(data, keyword):
    """크롤링한 데이터를 엑셀 파일로 저장합니다."""
    if not data:
        print("저장할 데이터가 없습니다.")
        return
    
    try:
        # 결과 저장 폴더 생성
        if not os.path.exists("results"):
            os.makedirs("results")
            
        # 현재 시간을 파일명에 추가
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"results/네이버블로그_{keyword}_{timestamp}.xlsx"
        
        # 데이터프레임 생성 및 엑셀 저장
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        
        print(f"\n크롤링 결과가 '{filename}' 파일로 저장되었습니다.")
        return filename
    except Exception as e:
        print(f"파일 저장 중 오류가 발생했습니다: {e}")

def main():
    print("=" * 50)
    print("네이버 블로그 크롤러를 시작합니다")
    print("=" * 50)
    print()
    
    # 설정 파일에서 로그인 정보 읽기
    naver_id, naver_pw = read_config()
    
    # 검색어 입력 받기
    search_keyword = input("검색할 키워드를 입력하세요: ")
    num_posts = input("크롤링할 게시물 수를 입력하세요 (기본값: 10): ")
    
    # 게시물 수 설정
    if not num_posts.isdigit():
        num_posts = 10
    else:
        num_posts = int(num_posts)
    
    # 드라이버 설정
    driver = setup_driver()
    
    # 네이버 로그인
    login_to_naver(driver, naver_id, naver_pw)
    
    # 블로그 검색
    go_to_blog_search(driver, search_keyword)
    
    # 블로그 게시물 크롤링
    blog_data = crawl_blog_posts(driver, num_posts)
    
    # 결과 저장
    if blog_data:
        excel_file = save_to_excel(blog_data, search_keyword)
        
        # 저장된 엑셀 파일 열기
        if excel_file and os.path.exists(excel_file):
            print(f"크롤링된 데이터를 엑셀 파일로 열려면 Enter 키를 누르세요...")
            input()
            os.startfile(excel_file)
    
    print("\n크롤링이 완료되었습니다.")
    print("브라우저는 수동으로 닫아주세요.")
    input("프로그램을 종료하려면 아무 키나 누르세요...")

if __name__ == "__main__":
    main()