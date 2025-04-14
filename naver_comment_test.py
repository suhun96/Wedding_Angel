from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

def setup_driver():
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    try:
        # 최신 크롬드라이버 자동 다운로드 시도
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except:
        # 수동 방식으로 시도
        driver = webdriver.Chrome(options=chrome_options)
    return driver

def capture_comment_elements(driver, url):
    """특정 댓글 영역 캡처 함수"""
    print(f"페이지 로딩 중: {url}")
    driver.get(url)
    time.sleep(3)
    
    # 결과 저장 폴더 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = f"comment_captures_{timestamp}"
    os.makedirs(save_dir, exist_ok=True)
    
    # iframe 전환 시도
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        iframe_switched = False
        
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
                print("iframe으로 전환 성공")
                iframe_switched = True
                break
            except:
                driver.switch_to.default_content()
    except:
        print("iframe 전환 시도 중 오류 발생")
    
    # 특정 댓글 요소 찾기
    try:
        # 비밀 댓글 요소 찾기 (제공된 HTML 구조 기반)
        secret_comments = driver.find_elements(
            By.CSS_SELECTOR, 
            "div.u_cbox_comment_box.u_cbox_type_profile.u_cbox_type_secret"
        )
        
        if not secret_comments:
            # 다른 방식으로 비밀 댓글 요소 찾기 
            secret_comments = driver.find_elements(
                By.CSS_SELECTOR, 
                "li.u_cbox_comment .u_cbox_type_secret"
            )
        
        # 캡처 수행
        print(f"발견된 댓글 요소 수: {len(secret_comments)}")
        
        for i, comment in enumerate(secret_comments):
            # 요소가 화면에 보이도록 스크롤
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment)
            time.sleep(0.5)
            
            # 댓글 영역 요소 (u_cbox_area) 찾기
            try:
                comment_area = comment.find_element(By.CSS_SELECTOR, "div.u_cbox_area")
                # 요소 하이라이트
                driver.execute_script(
                    "arguments[0].style.border = '2px solid red';", 
                    comment_area
                )
                
                # 캡처
                filename = f"{save_dir}/comment_{i+1}.png"
                comment_area.screenshot(filename)
                print(f"댓글 영역 {i+1} 캡처 완료: {filename}")
                
                # 요소 정보 저장
                try:
                    date_info = comment_area.find_element(By.CSS_SELECTOR, "span.u_cbox_date").text
                    with open(f"{save_dir}/comment_info.txt", "a", encoding="utf-8") as f:
                        f.write(f"댓글 {i+1}: {date_info}\n")
                except:
                    pass
            except:
                # 영역 찾기 실패 시 전체 요소 캡처
                filename = f"{save_dir}/comment_full_{i+1}.png"
                comment.screenshot(filename)
                print(f"전체 댓글 요소 {i+1} 캡처 완료: {filename}")
        
        print(f"모든 댓글 캡처 완료. 결과 위치: {save_dir}")
        return True
    
    except Exception as e:
        print(f"댓글 캡처 중 오류 발생: {e}")
        # 디버깅용 스크린샷
        driver.save_screenshot(f"{save_dir}/error_capture.png")
        return False

def main():
    url = input("캡처할 네이버 페이지 URL을 입력하세요: ")
    driver = setup_driver()
    
    try:
        capture_comment_elements(driver, url)
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        driver.quit()
        print("작업 완료")

if __name__ == "__main__":
    main()