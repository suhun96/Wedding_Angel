# -*- coding: utf-8 -*-
import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

def go_to_blog_post(driver, blog_url):
    """입력받은 블로그 포스트 페이지로 이동합니다."""
    try:
        print(f"블로그 포스트 페이지로 이동합니다: {blog_url}")
        driver.get(blog_url)
        time.sleep(3)
        
        # 블로그 포스트가 iframe 내부에 있는지 확인
        try:
            # 주요 iframe ID들
            iframe_ids = ["mainFrame", "cafe_main"]
            
            for iframe_id in iframe_ids:
                try:
                    iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, iframe_id))
                    )
                    driver.switch_to.frame(iframe)
                    print(f"iframe({iframe_id})으로 전환했습니다.")
                    break
                except:
                    continue
                    
        except Exception as e:
            print(f"iframe 전환 실패: {e}")
            print("메인 페이지에서 계속 진행합니다.")
            
        return True
    except Exception as e:
        print(f"블로그 페이지 이동 중 오류가 발생했습니다: {e}")
        return False

def capture_comments(driver):
    """블로그 포스트의 댓글 영역을 찾아 캡처합니다."""
    # 댓글 영역 선택자 리스트 (네이버 블로그 버전별로 다를 수 있음)
    comment_selectors = [
        ".area_comment", 
        "#cbox_module",
        ".comment_area",
        ".comment-box",
        ".commentBox",
        ".comment_wrap",
        ".u_cbox",
        ".u_cbox_content_wrap",
        ".u_cbox_list",
        ".list_comment", 
        ".comment_list"
    ]
    
    # 댓글 더보기 버튼 선택자 리스트
    more_comment_selectors = [
        ".btn_more", 
        ".u_cbox_more_btn",
        ".u_cbox_page_more",
        ".link_more", 
        ".more_comment", 
        ".btn_comment_more",
        "a:contains('댓글 더보기')"
    ]
    
    # 현재 시간을 이용한 파일명 생성
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_folder = "screenshots"
    os.makedirs(screenshot_folder, exist_ok=True)
    
    # 찾은 댓글 영역 수
    comment_count = 0
    
    print("\n댓글 영역을 찾고 캡처합니다...")
    
    # 모든 댓글을 보기 위해 '더보기' 버튼 클릭 시도
    for selector in more_comment_selectors:
        try:
            while True:
                more_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                if not more_buttons or not more_buttons[0].is_displayed():
                    break
                    
                print("댓글 더보기 버튼을 클릭합니다...")
                driver.execute_script("arguments[0].click();", more_buttons[0])
                time.sleep(1)
        except Exception as e:
            continue
    
    print("댓글을 모두 펼쳤습니다.")
    
    # 댓글 영역 찾기 및 캡처
    for selector in comment_selectors:
        try:
            comment_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            if not comment_elements:
                continue
                
            for i, element in enumerate(comment_elements):
                try:
                    # 요소가 보이도록 스크롤
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    
                    # 요소의 위치와 크기 가져오기
                    location = element.location
                    size = element.size
                    
                    # 요소 크기가 너무 작으면 건너뛰기 (실제 댓글 영역이 아닐 가능성)
                    if size['width'] < 100 or size['height'] < 50:
                        continue
                        
                    # 스크린샷 촬영
                    file_name = f"{screenshot_folder}/comment_{timestamp}_{i+1}.png"
                    element.screenshot(file_name)
                    print(f"댓글 영역 캡처 완료: {file_name}")
                    comment_count += 1
                except Exception as e:
                    print(f"댓글 요소 캡처 실패: {e}")
                    continue
            
            if comment_count > 0:
                print(f"총 {comment_count}개의 댓글 영역을 캡처했습니다.")
                break
        except Exception as e:
            continue
    
    if comment_count == 0:
        print("댓글 영역을 찾을 수 없거나 댓글이 없습니다.")
        
        # 전체 페이지 스크린샷 대신 찍기
        try:
            file_name = f"{screenshot_folder}/full_page_{timestamp}.png"
            driver.save_screenshot(file_name)
            print(f"전체 페이지 스크린샷을 저장했습니다: {file_name}")
        except Exception as e:
            print(f"전체 페이지 스크린샷 저장 실패: {e}")
    
    return comment_count

def main():
    print("=" * 50)
    print("네이버 블로그 댓글 캡처 도구를 시작합니다")
    print("=" * 50)
    print()
    
    # 설정 파일에서 로그인 정보 읽기
    naver_id, naver_pw = read_config()
    
    # 블로그 주소 입력 받기
    blog_url = input("네이버 블로그 포스트 URL을 입력하세요: ")
    
    if not blog_url.startswith("http"):
        blog_url = "https://" + blog_url
    
    # 드라이버 설정
    driver = setup_driver()
    
    try:
        # 네이버 로그인
        login_to_naver(driver, naver_id, naver_pw)
        
        # 블로그 포스트 페이지로 이동
        if go_to_blog_post(driver, blog_url):
            # 댓글 캡처
            comment_count = capture_comments(driver)
            
            if comment_count > 0:
                print(f"\n작업이 완료되었습니다. 캡처된 {comment_count}개의 이미지는 'screenshots' 폴더에 저장되었습니다.")
                os.startfile(os.path.abspath("screenshots"))
            else:
                print("\n댓글 캡처에 실패했습니다. 다른 블로그 주소를 시도해보세요.")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
    
    print("\n브라우저는 수동으로 닫아주세요.")
    input("프로그램을 종료하려면 아무 키나 누르세요...")

if __name__ == "__main__":
    main()