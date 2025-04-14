import os
import re
import time
from datetime import datetime
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")  # 필요시 헤드리스 모드 활성화
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login_to_naver(driver, username, password):
    """네이버 로그인"""
    print("네이버에 로그인 중...")
    driver.get("https://nid.naver.com/nidlogin.login")
    
    # 자바스크립트 실행으로 아이디/비밀번호 입력 (캡차 우회)
    driver.execute_script(f"document.getElementsByName('id')[0].value='{username}'")
    time.sleep(1)
    driver.execute_script(f"document.getElementsByName('pw')[0].value='{password}'")
    time.sleep(1)
    
    # 로그인 버튼 클릭
    try:
        login_button = driver.find_element(By.ID, "log.login")
        login_button.click()
        
        # 로그인 성공 확인
        WebDriverWait(driver, 5).until(
            lambda x: "nid.naver.com/nidlogin.login" not in x.current_url
        )
        print("로그인 성공!")
        return True
    except:
        print("로그인 실패. 아이디와 비밀번호를 확인해주세요.")
        return False

def is_valid_email(text):
    """이메일 주소 검증"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_blog_id_and_post_id(url):
    """블로그 URL에서 블로그 ID와 포스트 ID 추출"""
    # 일반 블로그 URL 패턴
    pattern1 = r'blog\.naver\.com\/([^\/]+)\/([0-9]+)'
    # 모바일 또는 다른 패턴
    pattern2 = r'blog\.naver\.com\/PostView\.naver\?blogId=([^&]+)&logNo=([0-9]+)'
    
    match = re.search(pattern1, url)
    if match:
        return match.group(1), match.group(2)
    
    match = re.search(pattern2, url)
    if match:
        return match.group(1), match.group(2)
    
    return None, None

def get_comments(driver, blog_url):
    """블로그 댓글 수집 및 이메일 포함 댓글 캡처"""
    print(f"블로그 게시물 접속 중: {blog_url}")
    driver.get(blog_url)
    
    # 블로그 ID와 포스트 ID 추출
    blog_id, post_id = extract_blog_id_and_post_id(blog_url)
    if not blog_id or not post_id:
        print("유효한 블로그 URL이 아닙니다.")
        return
    
    # 블로그 프레임으로 전환 (네이버 블로그는 iframe 구조)
    try:
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
        )
    except TimeoutException:
        print("블로그 프레임을 찾을 수 없습니다.")
        return
    
    # 댓글 영역 로딩 대기
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".area_comment"))
        )
    except TimeoutException:
        print("댓글 영역을 찾을 수 없습니다.")
        return
    
    # 더보기 버튼이 있으면 모든 댓글 로드
    try:
        while True:
            more_button = driver.find_element(By.CSS_SELECTOR, ".btn_comment_more")
            more_button.click()
            time.sleep(1)
    except NoSuchElementException:
        print("모든 댓글을 로드했습니다.")
    
    # 댓글 수집
    comments = driver.find_elements(By.CSS_SELECTOR, ".area_comment .item_comment")
    print(f"총 {len(comments)}개의 댓글을 찾았습니다.")
    
    # 스크린샷 저장 폴더 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_dir = f"screenshots_{timestamp}"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # 이메일이 포함된 댓글 캡처
    email_comments_count = 0
    for i, comment in enumerate(comments):
        try:
            # 댓글 내용
            comment_text = comment.find_element(By.CSS_SELECTOR, ".text_comment").text
            email = is_valid_email(comment_text)
            
            if email:
                print(f"이메일 발견: {email}")
                email_comments_count += 1
                
                # 스크롤하여 댓글이 보이게 조정
                driver.execute_script("arguments[0].scrollIntoView(true);", comment)
                time.sleep(0.5)
                
                # 댓글 요소 캡처
                filename = f"{screenshot_dir}/{email.replace('@', '_at_')}.png"
                comment.screenshot(filename)
                print(f"캡처 저장: {filename}")
        except Exception as e:
            print(f"댓글 처리 중 오류 발생: {e}")
    
    print(f"이메일이 포함된 댓글 {email_comments_count}개를 캡처했습니다.")
    print(f"스크린샷은 '{screenshot_dir}' 폴더에 저장되었습니다.")

def main():
    """메인 함수"""
    print("===== 네이버 블로그 댓글 수집기 =====")
    print("이메일이 포함된 댓글을 찾아 스크린샷으로 저장합니다.")
    print()
    
    # 네이버 계정 정보 입력
    username = input("네이버 아이디: ")
    password = getpass("네이버 비밀번호: ")
    blog_url = input("블로그 게시물 URL: ")
    
    # 드라이버 설정
    driver = setup_driver()
    
    try:
        # 네이버 로그인
        if login_to_naver(driver, username, password):
            # 댓글 수집 및 스크린샷
            get_comments(driver, blog_url)
    finally:
        # 종료
        print("\n프로그램을 종료합니다.")
        driver.quit()

if __name__ == "__main__":
    main()