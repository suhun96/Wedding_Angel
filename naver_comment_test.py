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

def capture_comment_area(driver, comment_area, capture_dir, page_num=1):
    """댓글 영역 캡처"""
    if not comment_area:
        return
    
    try:
        # 스크롤하여 댓글 영역이 보이게 조정
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_area)
        time.sleep(1)
        
        # 전체 댓글 영역 스크린샷
        filename = f"{capture_dir}/page_{page_num}_comments.png"
        
        try:
            # 요소 테두리 추가
            driver.execute_script("""
                arguments[0].style.border = '2px solid red';
            """, comment_area)
            
            # 요소 스크린샷
            comment_area.screenshot(filename)
            print(f"댓글 영역 캡처 (페이지 {page_num}): {filename}")
            
            # 개별 댓글 캡처
            find_and_capture_individual_comments(driver, comment_area, capture_dir, page_num)
            
            return True
        except Exception as e:
            print(f"댓글 영역 스크린샷 오류: {e}")
            
            # 요소 캡처 실패 시 전체 페이지 캡처
            driver.save_screenshot(f"{capture_dir}/page_{page_num}_full.png")
            print(f"전체 페이지 캡처 (페이지 {page_num}): {capture_dir}/page_{page_num}_full.png")
            
            return False
    except Exception as e:
        print(f"댓글 영역 캡처 오류: {e}")
        return False

def find_and_capture_individual_comments(driver, comment_area, capture_dir, page_num):
    """개별 댓글 찾아서 캡처"""
    try:
        # 댓글 선택자
        comment_selectors = [
            ".comment_item",             # 네이버 블로그 댓글
            ".u_cbox_comment",           # 네이버 뉴스 댓글
            ".item_comment",             # 아이템 댓글
            ".comment",                  # 댓글
            "li",                        # 목록 아이템 (댓글 목록에서)
            ".reply_item",               # 답글 아이템
            ".cmt_item"                  # 코멘트 아이템
        ]
        
        comments = []
        used_selector = ""
        
        # 각 선택자로 시도
        for selector in comment_selectors:
            try:
                elements = comment_area.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 0:
                    comments = elements
                    used_selector = selector
                    print(f"{len(comments)}개 댓글 발견 (선택자: {selector})")
                    break
            except:
                continue
        
        # 댓글이 없으면 JavaScript로 시도
        if not comments:
            try:
                comments_count = driver.execute_script("""
                    var commentArea = arguments[0];
                    var commentElements = [];
                    
                    // 자식 요소 중 텍스트가 있고 높이가 적절한 요소 찾기
                    function findPossibleComments(element, depth) {
                        if (depth > 10) return;
                        
                        var children = element.children;
                        for (var i = 0; i < children.length; i++) {
                            var child = children[i];
                            
                            // 댓글로 추정되는 요소 찾기
                            if (child.offsetHeight > 30 && 
                                child.offsetWidth > 100 && 
                                child.textContent.trim() && 
                                child.tagName !== 'SCRIPT' && 
                                child.tagName !== 'STYLE') {
                                
                                // 형제 요소가 비슷한 구조를 가지면 댓글 목록일 가능성 높음
                                var siblings = 0;
                                var parent = child.parentElement;
                                for (var j = 0; j < parent.children.length; j++) {
                                    if (parent.children[j].tagName === child.tagName) {
                                        siblings++;
                                    }
                                }
                                
                                if (siblings > 1) {
                                    // 댓글로 표시
                                    child.style.border = '2px solid green';
                                    commentElements.push(child);
                                }
                            }
                            
                            // 재귀적으로 자식 탐색
                            findPossibleComments(child, depth + 1);
                        }
                    }
                    
                    findPossibleComments(commentArea, 0);
                    return commentElements.length;
                """, comment_area)
                
                print(f"JavaScript로 {comments_count}개 댓글을 발견했습니다.")
            except Exception as e:
                print(f"JavaScript 댓글 찾기 오류: {e}")
        
        # 개별 댓글 캡처 (최대 10개)
        comment_count = min(len(comments), 10)
        for i in range(comment_count):
            try:
                comment = comments[i]
                
                # 스크롤하여 댓글이 보이게 조정
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment)
                time.sleep(0.3)
                
                # 요소 테두리 추가
                driver.execute_script("""
                    arguments[0].style.border = '1px solid blue';
                    arguments[0].style.backgroundColor = '#f8f8f8';
                """, comment)
                
                # 댓글 요소 캡처
                filename = f"{capture_dir}/page_{page_num}_comment_{i+1}.png"
                try:
                    comment.screenshot(filename)
                    print(f"댓글 {i+1} 캡처 (페이지 {page_num}): {filename}")
                except Exception as e:
                    print(f"댓글 {i+1} 개별 캡처 실패: {e}")
            except Exception as e:
                print(f"댓글 {i+1} 처리 중 오류: {e}")
        
        return True
    except Exception as e:
        print(f"개별 댓글 캡처 오류: {e}")
        return False

def navigate_and_capture_all_pages(driver, blog_url):
    """모든 댓글 페이지 순회하며 캡처"""
    print(f"블로그 페이지 접속: {blog_url}")
    driver.get(blog_url)
    time.sleep(3)
    
    # 화면 캡처 저장 폴더
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_dir = f"captures_{timestamp}"
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
    
    # 댓글 영역 찾기
    comment_area = find_comment_area(driver)
    
    if not comment_area:
        print("댓글 영역을 찾지 못했습니다. 종료합니다.")
        driver.save_screenshot(f"{capture_dir}/error_no_comment_area.png")
        return
    
    # 첫 페이지 댓글 캡처
    capture_comment_area(driver, comment_area, capture_dir, 1)
    
    # 페이지네이션 요소 찾기
    pagination = find_pagination_element(driver)
    
    if not pagination:
        print("페이지네이션 요소를 찾지 못했습니다. 첫 페이지만 캡처했습니다.")
        return
    
    # 페이지네이션 스크린샷
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination)
    pagination.screenshot(f"{capture_dir}/pagination.png")
    print(f"페이지네이션 캡처: {capture_dir}/pagination.png")
    
    # 총 페이지 수 가져오기
    total_pages = get_total_pages(driver, pagination)
    
    if total_pages <= 1:
        print("추가 페이지가 없습니다. 첫 페이지만 캡처했습니다.")
        return
    
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
                if page_num > 1:
                    next_button = pagination.find_element(By.CSS_SELECTOR, ".next:not(.dimmed)")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(1)
                    next_button.click()
                    print("다음 버튼 클릭")
                    time.sleep(2)
            except Exception as e:
                print(f"이전/다음 버튼 클릭 실패: {e}")
                continue
        
        # 댓글 영역 다시 찾기
        comment_area = find_comment_area(driver)
        if not comment_area:
            print(f"페이지 {page_num}의 댓글 영역을 찾지 못했습니다.")
            driver.save_screenshot(f"{capture_dir}/page_{page_num}_error.png")
            continue
        
        # 댓글 영역 캡처
        capture_comment_area(driver, comment_area, capture_dir, page_num)
        
        # 페이지네이션 다시 찾기 (다음 반복을 위해)
        pagination = find_pagination_element(driver)
    
    print(f"\n모든 페이지 캡처 완료! 결과는 '{capture_dir}' 폴더에 저장되었습니다.")

def main():
    print("===== 네이버 블로그 댓글 페이지네이션 전체 캡처 =====")
    print("이 스크립트는 네이버 블로그의 모든 댓글 페이지를 찾아 캡처합니다.")
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
            # 블로그 페이지로 이동하여 댓글 캡처
            navigate_and_capture_all_pages(driver, blog_url)
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