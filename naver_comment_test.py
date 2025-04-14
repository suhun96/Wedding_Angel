import time
import os
import re
from datetime import datetime
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

def setup_driver():
    """Chrome 드라이버 설정 (자동 다운로드)"""
    try:
        # 최신 크롬드라이버 자동 다운로드 시도
        from webdriver_manager.chrome import ChromeDriverManager
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"자동 크롬드라이버 설치 실패: {e}")
        
        # 수동 방식으로 시도
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e2:
            print(f"크롬드라이버 초기화 실패: {e2}")
            print("크롬드라이버가 설치되어 있지 않거나 PATH에 등록되지 않았습니다.")
            print("크롬드라이버를 수동으로 설치해주세요: https://chromedriver.chromium.org/downloads")
            exit(1)

def login_to_naver(driver, username, password):
    """네이버 로그인"""
    print("네이버에 로그인 중...")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(2)
    
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
    except Exception as e:
        print(f"로그인 실패: {e}")
        print("경고: 보안을 위해 네이버에서 자동 로그인을 차단할 수 있습니다.")
        print("차단될 경우 브라우저에서 직접 로그인 후 다시 시도해보세요.")
        return False

def switch_to_blog_frame(driver):
    """블로그 프레임 전환 시도"""
    # iframe ID로 시도
    frame_ids = ["mainFrame", "blogFrame", "postFrame"]
    for frame_id in frame_ids:
        try:
            WebDriverWait(driver, 3).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, frame_id))
            )
            print(f"프레임 전환 성공: {frame_id}")
            return True
        except:
            continue
    
    # 모든 iframe 시도
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for i, iframe in enumerate(iframes):
            try:
                driver.switch_to.frame(iframe)
                print(f"iframe[{i}] 전환 성공")
                return True
            except:
                driver.switch_to.default_content()
    except:
        pass
    
    print("프레임 전환 실패")
    return False

def click_comment_button(driver):
    """댓글 버튼 찾아서 클릭 - 특정 요구사항 반영"""
    print("댓글 버튼 찾는 중...")
    
    # 요구사항에 맞는 댓글 버튼 선택자
    try:
        # 1. role이 button이고 class에 btn_comment가 포함된 요소 찾기
        comment_button = driver.find_element(
            By.CSS_SELECTOR, 
            "a[role='button'][class*='btn_comment']"
        )
        
        print(f"댓글 버튼 발견: {comment_button.get_attribute('id')}")
        
        # 스크롤 및 클릭
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_button)
        time.sleep(1)
        
        try:
            comment_button.click()
        except:
            driver.execute_script("arguments[0].click();", comment_button)
        
        print("댓글 버튼 클릭 성공!")
        time.sleep(2)  # 댓글 로딩 대기
        return True
    except Exception as e:
        print(f"요구사항에 맞는 댓글 버튼 찾기 실패: {e}")
    
    # 기존 방식으로 시도
    selectors = [
        "a[role='button'][class*='btn_comment']",
        ".btn_comment",
        "a[id*='Comi']",
        "//a[contains(@class, 'btn_comment')]",
        "//a[contains(text(), '댓글')]"
    ]
    
    for selector in selectors:
        try:
            if selector.startswith("//"):
                elements = driver.find_elements(By.XPATH, selector)
            else:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
            if elements:
                print(f"{selector} 선택자로 요소 발견, 클릭 시도...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elements[0])
                time.sleep(1)
                try:
                    elements[0].click()
                except:
                    driver.execute_script("arguments[0].click();", elements[0])
                print(f"{selector} 클릭 성공!")
                time.sleep(2)
                return True
        except:
            continue
    
    # JavaScript로 시도
    print("JavaScript로 댓글 버튼 찾기 시도...")
    try:
        clicked = driver.execute_script("""
            // btn_comment 클래스 포함 & role='button' 속성 가진 요소 찾기
            var commentBtn = document.querySelector('a[role="button"][class*="btn_comment"]');
            if (commentBtn) {
                commentBtn.scrollIntoView({block: 'center'});
                setTimeout(function() {
                    commentBtn.click();
                }, 1000);
                return true;
            }
            
            // id가 Comi로 시작하는 요소 찾기
            var comiBtn = document.querySelector('a[id^="Comi"]');
            if (comiBtn) {
                comiBtn.scrollIntoView({block: 'center'});
                setTimeout(function() {
                    comiBtn.click();
                }, 1000);
                return true;
            }
            
            // '댓글' 텍스트 포함 버튼 찾기
            var elements = document.querySelectorAll('a, button');
            for (var i = 0; i < elements.length; i++) {
                if (elements[i].textContent.includes('댓글')) {
                    elements[i].scrollIntoView({block: 'center'});
                    setTimeout(function() {
                        elements[i].click();
                    }, 1000);
                    return true;
                }
            }
            
            return false;
        """)
        
        if clicked:
            print("JavaScript로 댓글 버튼 클릭 성공!")
            time.sleep(2)
            return True
    except Exception as e:
        print(f"JavaScript 댓글 버튼 클릭 오류: {e}")
    
    print("댓글 버튼을 찾지 못했습니다.")
    return False

def find_comment_area(driver):
    """댓글 영역 찾기"""
    print("댓글 영역 찾는 중...")
    
    # 댓글 영역 선택자
    comment_area_selectors = [
        ".area_comment",           # 네이버 블로그 댓글 영역
        ".u_cbox_area",            # 네이버 뉴스 등의 댓글 영역
        ".comment_box",
        "#cbox_module",
        ".comment_area",
        ".comment_list"
    ]
    
    for selector in comment_area_selectors:
        try:
            comment_area = driver.find_element(By.CSS_SELECTOR, selector)
            print(f"댓글 영역 발견: {selector}")
            return comment_area
        except:
            continue
    
    print("댓글 영역을 찾지 못했습니다.")
    return None

def find_pagination_element(driver):
    """페이지네이션 요소 찾기 - 특정 요구사항 반영"""
    print("페이지네이션 요소 찾는 중...")
    
    # 요구사항에 맞는 페이지네이션 선택자
    try:
        # div class="commentbox_pagination"
        pagination = driver.find_element(By.CSS_SELECTOR, ".commentbox_pagination")
        print("요구사항에 맞는 페이지네이션 요소 발견!")
        return pagination
    except Exception as e:
        print(f"요구사항에 맞는 페이지네이션 찾기 실패: {e}")
    
    # 일반적인 페이지네이션 선택자로 시도
    pagination_selectors = [
        ".commentbox_pagination",  # 요구사항 페이지네이션
        ".u_cbox_paginate",        # 네이버 댓글 페이지네이션
        ".pagination",             # 일반적인 페이지네이션
        ".paging",                 # 구 스타일 페이징
        ".page_navigation",        # 페이지 네비게이션
        ".paginate",               # 페이지네이트
        ".btn_pagination",         # 페이지네이션 버튼
        ".page_num"                # 페이지 번호
    ]
    
    for selector in pagination_selectors:
        try:
            pagination = driver.find_element(By.CSS_SELECTOR, selector)
            print(f"선택자로 페이지네이션 요소 발견: {selector}")
            return pagination
        except:
            continue
    
    print("페이지네이션 요소를 찾지 못했습니다.")
    return None

def get_total_pages(driver, pagination):
    """페이지네이션에서 총 페이지 수 가져오기"""
    if not pagination:
        return 1
    
    try:
        # 페이지 번호 정보 찾기
        last_page_element = pagination.find_element(By.CSS_SELECTOR, "._lastPageNo")
        total_pages = int(last_page_element.text.strip())
        print(f"총 페이지 수: {total_pages}")
        return total_pages
    except Exception as e:
        print(f"총 페이지 수 확인 실패: {e}")
        
        # 다른 방법으로 시도
        try:
            # JavaScript로 페이지 정보 확인
            total_pages = driver.execute_script("""
                var pagination = arguments[0];
                
                // lastPageNo 클래스 확인
                var lastPageEl = pagination.querySelector('._lastPageNo, .last_page, .total_page');
                if (lastPageEl) {
                    return parseInt(lastPageEl.textContent.trim());
                }
                
                // 페이지 번호가 있는 링크 확인
                var pageLinks = pagination.querySelectorAll('a');
                var maxPage = 1;
                
                for (var i = 0; i < pageLinks.length; i++) {
                    var pageNum = parseInt(pageLinks[i].textContent.trim());
                    if (!isNaN(pageNum) && pageNum > maxPage) {
                        maxPage = pageNum;
                    }
                }
                
                return maxPage || 1;
            """, pagination)
            
            print(f"JavaScript로 확인한 총 페이지 수: {total_pages}")
            return total_pages or 1
        except Exception as e:
            print(f"총 페이지 수 확인 실패 (JavaScript): {e}")
            return 1

def navigate_to_page(driver, pagination, page_num):
    """특정 페이지로 이동"""
    if not pagination:
        return False
    
    print(f"페이지 {page_num}로 이동 시도...")
    
    try:
        # 페이지 이동 전에 현재 페이지 확인
        current_page_element = pagination.find_element(By.CSS_SELECTOR, "._currentPageNo")
        current_page = int(current_page_element.text.strip())
        
        if current_page == page_num:
            print(f"이미 페이지 {page_num}에 있습니다.")
            return True
        
        # 이전/다음 버튼으로 이동
        prev_button = pagination.find_element(By.CSS_SELECTOR, ".prev")
        next_button = pagination.find_element(By.CSS_SELECTOR, ".next:not(.dimmed)")
        
        if current_page < page_num:
            # 다음 페이지로 이동
            if "dimmed" not in next_button.get_attribute("class"):
                print(f"다음 버튼으로 이동 (현재: {current_page} -> 목표: {page_num})")
                
                # 버튼이 보이게 스크롤
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(1)
                
                # 버튼 클릭
                try:
                    next_button.click()
                except:
                    driver.execute_script("arguments[0].click();", next_button)
                
                time.sleep(2)  # 페이지 로딩 대기
                return navigate_to_page(driver, find_pagination_element(driver), page_num)
            else:
                print("다음 버튼이 비활성화 되어 있습니다.")
                return False
        elif current_page > page_num:
            # 이전 페이지로 이동
            if "dimmed" not in prev_button.get_attribute("class"):
                print(f"이전 버튼으로 이동 (현재: {current_page} -> 목표: {page_num})")
                
                # 버튼이 보이게 스크롤
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", prev_button)
                time.sleep(1)
                
                # 버튼 클릭
                try:
                    prev_button.click()
                except:
                    driver.execute_script("arguments[0].click();", prev_button)
                
                time.sleep(2)  # 페이지 로딩 대기
                return navigate_to_page(driver, find_pagination_element(driver), page_num)
            else:
                print("이전 버튼이 비활성화 되어 있습니다.")
                return False
    except Exception as e:
        print(f"페이지 {page_num}로 이동 실패: {e}")
        
        # JavaScript로 시도
        try:
            moved = driver.execute_script("""
                var pagination = arguments[0];
                var targetPage = arguments[1];
                
                // 현재 페이지 확인
                var currentPageEl = pagination.querySelector('._currentPageNo, .current, .on');
                if (!currentPageEl) return false;
                
                var currentPage = parseInt(currentPageEl.textContent.trim());
                if (currentPage === targetPage) return true;
                
                // 이동 방향 결정
                if (currentPage < targetPage) {
                    // 다음 버튼 클릭
                    var nextBtn = pagination.querySelector('.next:not(.dimmed)');
                    if (nextBtn) {
                        nextBtn.click();
                        return true;
                    }
                } else {
                    // 이전 버튼 클릭
                    var prevBtn = pagination.querySelector('.prev:not(.dimmed)');
                    if (prevBtn) {
                        prevBtn.click();
                        return true;
                    }
                }
                
                return false;
            """, pagination, page_num)
            
            if moved:
                print(f"JavaScript로 페이지 이동 시도 성공")
                time.sleep(2)  # 페이지 로딩 대기
                return navigate_to_page(driver, find_pagination_element(driver), page_num)
        except Exception as e:
            print(f"JavaScript 페이지 이동 실패: {e}")
        
        return False

# 새로 추가한 함수: 비밀 댓글 영역 캡처
def capture_secret_comment_areas(driver, capture_dir, page_num=1):
    """비밀 댓글 영역만 캡처하는 함수"""
    print(f"페이지 {page_num}의 비밀 댓글 영역 찾아서 캡처...")
    
    # 비밀 댓글 영역 저장 폴더
    secret_dir = f"{capture_dir}/secret_comments"
    os.makedirs(secret_dir, exist_ok=True)
    
    try:
        # 비밀 댓글 요소 선택자 (제공된 HTML 분석 기반)
        secret_comments = driver.find_elements(
            By.CSS_SELECTOR, 
            "div.u_cbox_comment_box.u_cbox_type_profile.u_cbox_type_secret"
        )
        
        if not secret_comments:
            # 다른 형식의 비밀 댓글도 시도
            secret_comments = driver.find_elements(
                By.CSS_SELECTOR, 
                "li.u_cbox_comment .u_cbox_type_secret"
            )
        
        if not secret_comments:
            print(f"페이지 {page_num}에서 비밀 댓글을 찾을 수 없습니다.")
            return 0
            
        print(f"페이지 {page_num}에서 {len(secret_comments)}개의 비밀 댓글 발견")
        
        # 각 비밀 댓글 요소 캡처
        for i, comment in enumerate(secret_comments):
            # 스크롤하여 댓글이 보이게 조정
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment)
            time.sleep(0.5)  # 스크롤 후 대기
            
            # 댓글 영역 찾기 (u_cbox_area - 우리가 캡처하려는 정확한 부분)
            try:
                comment_area = comment.find_element(By.CSS_SELECTOR, "div.u_cbox_area")
                
                # 시각화를 위한 테두리 설정
                driver.execute_script("""
                    arguments[0].style.border = '2px solid red';
                """, comment_area)
                
                # 스크린샷 저장
                filename = f"{secret_dir}/page_{page_num}_secret_{i+1}.png"
                comment_area.screenshot(filename)
                print(f"비밀 댓글 영역 {i+1} 캡처: {filename}")
                
                # 날짜 정보 저장
                try:
                    date_info = comment_area.find_element(By.CSS_SELECTOR, "span.u_cbox_date").text
                    with open(f"{secret_dir}/secret_comments_info.txt", "a", encoding="utf-8") as f:
                        f.write(f"페이지 {page_num} - 비밀 댓글 {i+1}: {date_info}\n")
                except:
                    pass
            except Exception as e:
                print(f"비밀 댓글 {i+1}의 영역 캡처 실패: {e}")
                
                # 전체 요소 캡처 시도
                try:
                    filename = f"{secret_dir}/page_{page_num}_secret_full_{i+1}.png"
                    comment.screenshot(filename)
                    print(f"전체 비밀 댓글 요소 {i+1} 캡처: {filename}")
                except:
                    print(f"전체 비밀 댓글 요소 {i+1} 캡처도 실패")
        
        return len(secret_comments)
    except Exception as e:
        print(f"비밀 댓글 영역 캡처 중 오류 발생: {e}")
        return 0

def navigate_and_capture_secret_comments(driver, blog_url):
    """모든 페이지의 비밀 댓글 영역만 캡처"""
    print(f"블로그 페이지 접속: {blog_url}")
    driver.get(blog_url)
    time.sleep(3)
    
    # 화면 캡처 저장 폴더
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_dir = f"secret_comments_{timestamp}"
    os.makedirs(capture_dir, exist_ok=True)
    
    # 블로그 프레임 전환
    switch_to_blog_frame(driver)
    
    # 페이지 소스 저장 (디버깅용)
    with open(f"{capture_dir}/page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"페이지 소스 저장: {capture_dir}/page_source.html")
    
    # 댓글 버튼 클릭
    comment_button_clicked = click_comment_button(driver)
    
    if comment_button_clicked:
        print("댓글 로딩 중...")
        time.sleep(3)
    
    # 첫 페이지 비밀 댓글 캡처
    secret_count = capture_secret_comment_areas(driver, capture_dir, 1)
    total_secret_count = secret_count
    
    # 페이지네이션 요소 찾기
    pagination = find_pagination_element(driver)
    
    if not pagination:
        print("페이지네이션 요소를 찾지 못했습니다. 첫 페이지만 캡처했습니다.")
        return total_secret_count
    
    # 총 페이지 수 가져오기
    total_pages = get_total_pages(driver, pagination)
    
    if total_pages <= 1:
        print("추가 페이지가 없습니다. 첫 페이지만 캡처했습니다.")
        return total_secret_count
    
    # 2페이지부터 마지막 페이지까지 처리
    for page_num in range(2, total_pages + 1):
        print(f"\n=== 페이지 {page_num}/{total_pages} 처리 중... ===")
        
        # 페이지 이동
        page_moved = navigate_to_page(driver, pagination, page_num)
        
        if not page_moved:
            print(f"페이지 {page_num}로 이동하지 못했습니다.")
            
            # 페이지네이션 요소 다시 찾기
            pagination = find_pagination_element(driver)
            if not pagination:
                print("페이지네이션 요소를 다시 찾지 못했습니다.")
                break
            
            # 이전/다음 버튼으로 이동 시도
            try:
                next_button = pagination.find_element(By.CSS_SELECTOR, ".next:not(.dimmed)")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(1)
                next_button.click()
                print("다음 버튼 클릭")
                time.sleep(2)
            except Exception as e:
                print(f"다음 버튼 클릭 실패: {e}")
                continue
        
        # 현재 페이지의 비밀 댓글 캡처
        page_secret_count = capture_secret_comment_areas(driver, capture_dir, page_num)
        total_secret_count += page_secret_count
        
        # 페이지네이션 다시 찾기 (다음 반복을 위해)
        pagination = find_pagination_element(driver)
    
    print(f"\n모든 페이지 처리 완료! 총 {total_secret_count}개의 비밀 댓글 영역을 캡처했습니다.")
    print(f"결과는 '{capture_dir}' 폴더에 저장되었습니다.")
    return total_secret_count

def main():
    print("===== 네이버 블로그 비밀 댓글 영역 캡처 =====")
    print("이 스크립트는 네이버 블로그의 모든 페이지에서 비밀 댓글 영역을 찾아 캡처합니다.")
    print()
    
    # 네이버 로그인 정보 입력
    username = input("네이버 아이디: ")
    password = getpass("네이버 비밀번호: ")
    blog_url = input("블로그 게시물 URL: ")
    
    # URL 형식 검증
    if not blog_url.startswith("https://"):
        blog_url = "https://" + blog_url
    
    if not re.search(r"(blog\.naver\.com|m\.blog\.naver\.com)", blog_url):
        print("경고: 네이버 블로그 URL이 아닌 것 같습니다. 계속하시겠습니까? (y/n)")
        if input().lower() != 'y':
            print("프로그램을 종료합니다.")
            return
    
    # 드라이버 초기화
    driver = setup_driver()
    if not driver:
        print("브라우저 드라이버 초기화 실패")
        return
    
    try:
        # 네이버 로그인 시도
        login_success = login_to_naver(driver, username, password)
        
        if login_success:
            # 블로그 페이지로 이동하여 비밀 댓글만 캡처
            captured_count = navigate_and_capture_secret_comments(driver, blog_url)
            print(f"총 {captured_count}개의 비밀 댓글 영역을 캡처했습니다.")
        else:
            print("로그인 실패로 인해 진행할 수 없습니다.")
            print("참고: 네이버는 자동 로그인을 차단할 수 있습니다.")
            print("브라우저에서 직접 로그인 후 프로그램을 다시 실행해보세요.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 브라우저 종료
        print("브라우저를 종료합니다...")
        driver.quit()
        print("프로그램이 완료되었습니다.")

if __name__ == "__main__":
    main()