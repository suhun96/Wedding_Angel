import time
import os
import re
import csv
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
        # _lastPageNo 클래스로 총 페이지 수 가져오기 (제공된 CSS에서 확인됨)
        last_page_element = pagination.find_element(By.CSS_SELECTOR, "._lastPageNo")
        total_pages = int(last_page_element.text.strip())
        print(f"총 페이지 수: {total_pages}")
        return total_pages
    except Exception as e:
        print(f"_lastPageNo 클래스로 총 페이지 확인 실패: {e}")
        
        # 다른 방법으로 시도
        try:
            # div.num 내 span 요소 찾기
            spans = pagination.find_elements(By.CSS_SELECTOR, "div.num > span")
            for span in spans:
                # 숫자가 포함된 span 찾기
                if span.text.strip().isdigit():
                    total_pages = int(span.text.strip())
                    print(f"div.num > span에서 총 페이지 수 추출: {total_pages}")
                    return total_pages
        except Exception as e2:
            print(f"div.num > span에서 총 페이지 수 추출 실패: {e2}")
        
        # 모든 방법 실패 시 기본값 1 반환
        return 1

def navigate_to_page(driver, pagination, page_num, current_page=None):
    """특정 페이지로 이동 - 제공된 CSS 구조 기반으로 수정"""
    if not pagination:
        return False
    
    print(f"페이지 {page_num}로 이동 시도...")
    
    try:
        # 현재 페이지 정보 확인 (CSS 구조에서 확인된 ._currentPageNo 사용)
        current_page_element = pagination.find_element(By.CSS_SELECTOR, "._currentPageNo")
        current_page = int(current_page_element.text.strip())
        
        # 총 페이지 수 확인
        last_page_element = pagination.find_element(By.CSS_SELECTOR, "._lastPageNo")
        total_pages = int(last_page_element.text.strip())
        
        print(f"현재 페이지 정보: {current_page}/{total_pages}")
        
        # 현재 페이지가 이미 원하는 페이지인 경우
        if current_page == page_num:
            print(f"이미 페이지 {page_num}에 있습니다.")
            return True
        
        # 페이지 이동 방향 결정
        if page_num < current_page:
            # 이전 페이지로 이동
            try:
                # CSS에서 확인된 정확한 선택자 사용
                prev_button = pagination.find_element(By.CSS_SELECTOR, "a.prev")
                
                # 버튼 비활성화 여부 확인
                if "dimmed" in prev_button.get_attribute("class"):
                    print("이전 버튼이 비활성화되어 있습니다.")
                    return False
                
                # 버튼 클릭
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", prev_button)
                time.sleep(1.5)
                
                try:
                    prev_button.click()
                except:
                    driver.execute_script("arguments[0].click();", prev_button)
                
                print("이전 버튼 클릭!")
                time.sleep(3)
                
                # 페이지 전환 확인
                updated_pagination = find_pagination_element(driver)
                if not updated_pagination:
                    print("페이지네이션 요소를 다시 찾을 수 없습니다.")
                    return False
                
                # 현재 페이지 다시 확인
                try:
                    new_current_element = updated_pagination.find_element(By.CSS_SELECTOR, "._currentPageNo")
                    new_current_page = int(new_current_element.text.strip())
                    print(f"이동 후 현재 페이지: {new_current_page}")
                    
                    if new_current_page == page_num:
                        print(f"목표 페이지 {page_num}에 도달했습니다.")
                        return True
                    else:
                        # 계속 이동 시도 (재귀 호출)
                        return navigate_to_page(driver, updated_pagination, page_num)
                except Exception as e:
                    print(f"이동 후 페이지 확인 실패: {e}")
                    return False
            except Exception as e:
                print(f"이전 버튼 클릭 실패: {e}")
                return False
        else:
            # 다음 페이지로 이동
            try:
                # CSS에서 확인된 정확한 선택자 사용
                next_button = pagination.find_element(By.CSS_SELECTOR, "a.next")
                
                # 버튼 비활성화 여부 확인
                if "dimmed" in next_button.get_attribute("class"):
                    print("다음 버튼이 비활성화되어 있습니다.")
                    return False
                
                # 버튼 클릭
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(1.5)
                
                try:
                    next_button.click()
                except:
                    driver.execute_script("arguments[0].click();", next_button)
                
                print("다음 버튼 클릭!")
                time.sleep(3)
                
                # 페이지 전환 확인
                updated_pagination = find_pagination_element(driver)
                if not updated_pagination:
                    print("페이지네이션 요소를 다시 찾을 수 없습니다.")
                    return False
                
                # 현재 페이지 다시 확인
                try:
                    new_current_element = updated_pagination.find_element(By.CSS_SELECTOR, "._currentPageNo")
                    new_current_page = int(new_current_element.text.strip())
                    print(f"이동 후 현재 페이지: {new_current_page}")
                    
                    if new_current_page == page_num:
                        print(f"목표 페이지 {page_num}에 도달했습니다.")
                        return True
                    else:
                        # 계속 이동 시도 (재귀 호출)
                        return navigate_to_page(driver, updated_pagination, page_num)
                except Exception as e:
                    print(f"이동 후 페이지 확인 실패: {e}")
                    return False
            except Exception as e:
                print(f"다음 버튼 클릭 실패: {e}")
                return False
    except Exception as e:
        print(f"페이지 {page_num}로 이동 실패: {e}")
        return False

def extract_email(text):
    """텍스트에서 이메일 주소 추출"""
    if not text:
        return None
    
    # 이메일 정규식 패턴
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    
    if match:
        return match.group(0)
    
    return None

def get_username_from_email(email):
    """이메일에서 @ 앞 부분 추출"""
    if not email:
        return None
    
    parts = email.split('@')
    if len(parts) >= 1:
        return parts[0]
    
    return None

def capture_comment_with_email(driver, capture_dir, page_num=1):
    """이메일이 포함된 댓글 영역 캡처 함수"""
    print(f"페이지 {page_num}의 댓글 영역에서 이메일 탐색 중...")
    
    # 댓글 영역 저장 폴더
    os.makedirs(capture_dir, exist_ok=True)
    
    # CSV 파일 준비
    csv_file = f"{capture_dir}/email_comments.csv"
    csv_exists = os.path.exists(csv_file)
    
    csv_fields = ["이메일 ID", "이메일 주소", "스크린샷 파일명"]
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        if not csv_exists:
            csv_writer.writerow(csv_fields)
    
    # 댓글 요소들 찾기
    try:
        # 일반 댓글 선택자
        comment_selectors = [
            ".u_cbox_comment",           # 네이버 뉴스/블로그 댓글
            ".comment_item",             # 네이버 블로그 댓글
            ".item_comment",             # 아이템 댓글
            ".comment",                  # 댓글
            "li",                        # 목록 아이템 (댓글 목록에서)
        ]
        
        all_comments = []
        
        # 각 선택자로 시도
        for selector in comment_selectors:
            try:
                comments = driver.find_elements(By.CSS_SELECTOR, selector)
                if comments and len(comments) > 0:
                    all_comments = comments
                    print(f"{len(comments)}개 댓글 발견 (선택자: {selector})")
                    break
            except:
                continue
        
        if not all_comments:
            print(f"페이지 {page_num}에서 댓글을 찾을 수 없습니다.")
            return 0
        
        # 이메일이 포함된 댓글 수
        email_comment_count = 0
        email_data = []
        
        # 각 댓글 확인
        for i, comment in enumerate(all_comments):
            try:
                # 스크롤하여 댓글이 보이게 조정
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment)
                time.sleep(0.5)
                
                # 댓글 내용 추출
                try:
                    # 댓글 내용 요소 찾기 - 여러 선택자 시도
                    content_selectors = [
                        ".u_cbox_contents",          # 네이버 댓글 내용
                        ".u_cbox_text",              # 다른 형식의 네이버 댓글
                        ".comment_text",             # 일반 댓글 텍스트
                        ".text_comment",             # 텍스트 댓글
                        "p",                         # 단락 요소
                        ".comment_area"              # 댓글 영역
                    ]
                    
                    comment_text = None
                    for cs in content_selectors:
                        try:
                            content_elem = comment.find_element(By.CSS_SELECTOR, cs)
                            comment_text = content_elem.text
                            if comment_text.strip():
                                break
                        except:
                            continue
                    
                    # 내용을 찾지 못했다면 전체 텍스트 사용
                    if not comment_text:
                        comment_text = comment.text
                    
                    # 이메일 주소 탐색
                    email = extract_email(comment_text)
                    
                    if email:
                        print(f"이메일 발견: {email} (댓글 {i+1})")
                        
                        # 이메일 사용자명 추출
                        username = get_username_from_email(email)
                        
                        # 댓글 영역 찾기 (정확한 캡처를 위해)
                        comment_area = None
                        try:
                            comment_area = comment.find_element(By.CSS_SELECTOR, "div.u_cbox_area")
                        except:
                            comment_area = comment  # 영역이 없으면 전체 댓글 요소 사용
                        
                        # 파일명에 이메일 사용
                        safe_email = email.replace('@', '_').replace('.', '_')
                        filename = f"{safe_email}.png"
                        filepath = f"{capture_dir}/{filename}"
                        
                        # 스크린샷 저장 (테두리 없이)
                        comment_area.screenshot(filepath)
                        print(f"이메일이 포함된 댓글 캡처: {filepath}")
                        
                        # CSV 데이터 준비
                        email_data.append([username, email, filename])
                        email_comment_count += 1
                        
                except Exception as e:
                    print(f"댓글 {i+1}의 내용 추출 중 오류: {e}")
            
            except Exception as e:
                print(f"댓글 {i+1} 처리 중 오류: {e}")
        
        # CSV 파일에 데이터 추가
        if email_data:
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerows(email_data)
            
            print(f"페이지 {page_num}에서 {email_comment_count}개의 이메일이 포함된 댓글을 캡처했습니다.")
        
        return email_comment_count
        
    except Exception as e:
        print(f"이메일 포함 댓글 캡처 중 오류 발생: {e}")
        return 0

def capture_secret_comment_with_email(driver, capture_dir, page_num=1):
    """비밀 댓글 중 이메일이 포함된 댓글 영역만 캡처하는 함수"""
    print(f"페이지 {page_num}의 비밀 댓글 영역에서 이메일 탐색 중...")
    
    # 캡처 저장 폴더
    os.makedirs(capture_dir, exist_ok=True)
    
    # CSV 파일 준비
    csv_file = f"{capture_dir}/email_comments.csv"
    csv_exists = os.path.exists(csv_file)
    
    csv_fields = ["이메일 ID", "이메일 주소", "스크린샷 파일명"]
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        if not csv_exists:
            csv_writer.writerow(csv_fields)
    
    try:
        # 비밀 댓글 요소 선택자
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
        
        # 이메일이 포함된 비밀 댓글 수
        email_comment_count = 0
        email_data = []
        
        # 각 비밀 댓글 요소 확인
        for i, comment in enumerate(secret_comments):
            try:
                # 스크롤하여 댓글이 보이게 조정
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment)
                time.sleep(0.5)
                
                # 댓글 내용 추출
                try:
                    # 비밀 댓글 내용 텍스트 확인 시도
                    content_selectors = [
                        ".u_cbox_secret_contents",   # 비밀 댓글 내용
                        ".u_cbox_contents",          # 일반 댓글 내용
                        ".u_cbox_text"               # 댓글 텍스트
                    ]
                    
                    comment_text = None
                    for cs in content_selectors:
                        try:
                            content_elem = comment.find_element(By.CSS_SELECTOR, cs)
                            comment_text = content_elem.text
                            if comment_text.strip():
                                break
                        except:
                            continue
                    
                    # 내용을 찾지 못했다면 전체 텍스트 사용
                    if not comment_text:
                        comment_text = comment.text
                    
                    # 이메일 주소 탐색
                    email = extract_email(comment_text)
                    
                    if email:
                        print(f"이메일 발견: {email} (비밀 댓글 {i+1})")
                        
                        # 이메일 사용자명 추출
                        username = get_username_from_email(email)
                        
                        # 댓글 영역 찾기 (u_cbox_area - 우리가 캡처하려는 정확한 부분)
                        try:
                            comment_area = comment.find_element(By.CSS_SELECTOR, "div.u_cbox_area")
                            
                            # 파일명에 이메일 사용
                            safe_email = email.replace('@', '_').replace('.', '_')
                            filename = f"{safe_email}.png"
                            filepath = f"{capture_dir}/{filename}"
                            
                            # 스크린샷 저장 (테두리 없이)
                            comment_area.screenshot(filepath)
                            print(f"이메일이 포함된 비밀 댓글 캡처: {filepath}")
                            
                            # CSV 데이터 준비
                            email_data.append([username, email, filename])
                            email_comment_count += 1
                            
                        except Exception as e:
                            print(f"비밀 댓글 {i+1}의 영역 캡처 실패: {e}")
                            
                            # 전체 요소 캡처 시도
                            try:
                                safe_email = email.replace('@', '_').replace('.', '_')
                                filename = f"{safe_email}_full.png"
                                filepath = f"{capture_dir}/{filename}"
                                
                                comment.screenshot(filepath)
                                print(f"이메일이 포함된 전체 비밀 댓글 요소 캡처: {filepath}")
                                
                                # CSV 데이터 준비
                                email_data.append([username, email, filename])
                                email_comment_count += 1
                            except:
                                print(f"이메일이 포함된 전체 비밀 댓글 요소 캡처도 실패")
                except Exception as e:
                    print(f"비밀 댓글 {i+1}의 내용 확인 중 오류: {e}")
            except Exception as e:
                print(f"비밀 댓글 {i+1} 처리 중 오류: {e}")
        
        # CSV 파일에 데이터 추가
        if email_data:
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerows(email_data)
            
            print(f"페이지 {page_num}에서 {email_comment_count}개의 이메일이 포함된 비밀 댓글을 캡처했습니다.")
        
        return email_comment_count
    except Exception as e:
        print(f"이메일 포함 비밀 댓글 캡처 중 오류 발생: {e}")
        return 0

def navigate_and_capture_email_comments(driver, blog_url):
    """모든 페이지의 이메일이 포함된 댓글 영역만 캡처 - 제공된 CSS 구조 기반으로 수정"""
    print(f"블로그 페이지 접속: {blog_url}")
    driver.get(blog_url)
    time.sleep(3)
    
    # 화면 캡처 저장 폴더
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_dir = f"email_comments_{timestamp}"
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
    
    # 이전/다음 페이지 이동을 위한 변수 초기화
    total_email_count = 0
    processed_pages = set()  # 이미 처리한 페이지 추적
    
    # 첫 번째 페이지 처리 (항상 존재)
    print("\n=== 댓글 페이지 처리 시작 ===")
    
    # 페이지네이션 요소 찾기
    pagination = find_pagination_element(driver)
    
    if not pagination:
        print("페이지네이션 요소를 찾을 수 없습니다. 단일 페이지만 처리합니다.")
        # 첫 페이지 이메일 포함 댓글 캡처
        normal_count = capture_comment_with_email(driver, capture_dir, 1)
        secret_count = capture_secret_comment_with_email(driver, capture_dir, 1)
        total_email_count = normal_count + secret_count
        return total_email_count
    
    # 총 페이지 수 가져오기
    total_pages = get_total_pages(driver, pagination)
    
    # 페이지 처리 루프
    while True:
        # 현재 페이지 번호 확인
        try:
            current_element = pagination.find_element(By.CSS_SELECTOR, "._currentPageNo")
            current_page = int(current_element.text.strip())
            print(f"\n=== 현재 페이지 {current_page}/{total_pages} 처리 중... ===")
        except Exception as e:
            print(f"현재 페이지 번호 확인 실패: {e}")
            current_page = len(processed_pages) + 1
            print(f"\n=== 추정 페이지 {current_page} 처리 중... ===")
        
        # 이미 처리한 페이지인지 확인
        if current_page in processed_pages:
            print(f"페이지 {current_page}는 이미 처리했습니다. 종료합니다.")
            break
        
        # 현재 페이지 이메일 포함 댓글 캡처
        normal_count = capture_comment_with_email(driver, capture_dir, current_page)
        secret_count = capture_secret_comment_with_email(driver, capture_dir, current_page)
        total_email_count += (normal_count + secret_count)
        
        # 처리한 페이지 기록
        processed_pages.add(current_page)
        
        # 모든 페이지 처리 완료 확인
        if len(processed_pages) >= total_pages:
            print(f"모든 페이지({total_pages}개)를 처리했습니다.")
            break
        
        # 페이지네이션 요소 다시 찾기 (댓글 영역 변화 가능성)
        pagination = find_pagination_element(driver)
        if not pagination:
            print("페이지네이션 요소를 다시 찾을 수 없습니다. 종료합니다.")
            break
        
        # 다음 또는 이전 페이지로 이동
        # 현재 2/2 페이지인 경우 이전 버튼으로 1페이지 이동
        if current_page == total_pages and 1 not in processed_pages:
            try:
                prev_button = pagination.find_element(By.CSS_SELECTOR, "a.prev")
                
                # 이전 버튼 비활성화 확인
                if "dimmed" in prev_button.get_attribute("class"):
                    print("이전 버튼이 비활성화되어 있습니다. 이동 불가.")
                    break
                
                # 이전 버튼 클릭
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", prev_button)
                time.sleep(1.5)
                try:
                    prev_button.click()
                except:
                    driver.execute_script("arguments[0].click();", prev_button)
                print("이전 버튼 클릭!")
                time.sleep(3)
                
                # 페이지네이션 요소 다시 찾기
                pagination = find_pagination_element(driver)
            except Exception as e:
                print(f"이전 버튼 클릭 실패: {e}")
                break
        
        # 현재 1/2 페이지인 경우 다음 버튼으로 2페이지 이동
        elif current_page == 1 and total_pages > 1 and total_pages not in processed_pages:
            try:
                next_button = pagination.find_element(By.CSS_SELECTOR, "a.next")
                
                # 다음 버튼 비활성화 확인
                if "dimmed" in next_button.get_attribute("class"):
                    print("다음 버튼이 비활성화되어 있습니다. 이동 불가.")
                    break
                
                # 다음 버튼 클릭
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(1.5)
                try:
                    next_button.click()
                except:
                    driver.execute_script("arguments[0].click();", next_button)
                print("다음 버튼 클릭!")
                time.sleep(3)
                
                # 페이지네이션 요소 다시 찾기
                pagination = find_pagination_element(driver)
            except Exception as e:
                print(f"다음 버튼 클릭 실패: {e}")
                break
        
        # 그 외의 경우 (모든 페이지를 처리한 경우)
        else:
            print("더 이상 처리할 페이지가 없습니다.")
            break
    
    print(f"\n순회 완료! 총 {total_email_count}개의 이메일이 포함된 댓글 영역을 캡처했습니다.")
    print(f"결과는 '{capture_dir}' 폴더에 저장되었습니다.")
    print(f"CSV 파일: '{capture_dir}/email_comments.csv'")
    return total_email_count

def main():
    print("===== 네이버 블로그 이메일 포함 댓글 캡처 =====")
    print("이 스크립트는 네이버 블로그의 모든 페이지에서 이메일이 포함된 댓글 영역을 찾아 캡처합니다.")
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
            # 블로그 페이지로 이동하여 이메일 포함 댓글만 캡처
            captured_count = navigate_and_capture_email_comments(driver, blog_url)
            print(f"총 {captured_count}개의 이메일이 포함된 댓글 영역을 캡처했습니다.")
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