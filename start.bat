@echo off
echo ====================================================
echo      네이버 블로그 댓글 캡처 도구 (올인원 버전)
echo ====================================================
echo.

REM Python 설치 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python이 설치되어 있지 않습니다. Python 설치 프로그램을 다운로드합니다...
    echo Python 설치 시 "Add Python to PATH" 옵션을 반드시 체크해주세요!
    start https://www.python.org/downloads/
    echo Python 설치 후 이 스크립트를 다시 실행해주세요.
    pause
    exit
)

REM 가상환경 생성 및 활성화
if not exist venv (
    echo 가상환경을 생성합니다...
    python -m venv venv
) else (
    echo 가상환경이 이미 존재합니다.
)

echo 가상환경을 활성화합니다...
call venv\Scripts\activate.bat

REM pip 업그레이드 및 필요한 패키지 설치
echo pip를 최신 버전으로 업그레이드합니다...
python -m pip install --upgrade pip

echo 필요한 패키지를 설치합니다...
pip install selenium webdriver-manager pillow

REM 웹드라이버 자동 업데이트를 위한 초기 실행
echo 웹드라이버를 초기화합니다...
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"

REM 결과물 저장 폴더 생성
if not exist screenshots (
    echo 스크린샷 저장 폴더를 생성합니다...
    mkdir screenshots
)

REM 네이버 로그인 정보 설정 파일 생성
if not exist config.txt (
    echo 네이버 로그인 정보를 설정해주세요.
    set /p naver_id=네이버 아이디: 
    set /p naver_pw=네이버 비밀번호: 
    echo %naver_id%>config.txt
    echo %naver_pw%>>config.txt
    echo 로그인 정보가 저장되었습니다.
) else (
    echo 로그인 정보가 이미 존재합니다. 변경하려면 config.txt 파일을 삭제 후 다시 실행하세요.
)

REM 메인 스크립트 자동 생성 (없는 경우)
if not exist naver_blog_comment_capturer.py (
    echo 메인 스크립트 파일을 생성합니다...
    
    echo import os> naver_blog_comment_capturer.py
    echo import time>> naver_blog_comment_capturer.py
    echo import datetime>> naver_blog_comment_capturer.py
    echo from selenium import webdriver>> naver_blog_comment_capturer.py
    echo from selenium.webdriver.chrome.service import Service>> naver_blog_comment_capturer.py
    echo from selenium.webdriver.chrome.options import Options>> naver_blog_comment_capturer.py
    echo from selenium.webdriver.common.by import By>> naver_blog_comment_capturer.py
    echo from selenium.webdriver.support.ui import WebDriverWait>> naver_blog_comment_capturer.py
    echo from selenium.webdriver.support import expected_conditions as EC>> naver_blog_comment_capturer.py
    echo from selenium.common.exceptions import TimeoutException, NoSuchElementException>> naver_blog_comment_capturer.py
    echo from webdriver_manager.chrome import ChromeDriverManager>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo def read_config():>> naver_blog_comment_capturer.py
    echo     """설정 파일에서 네이버 로그인 정보를 읽어옵니다.""">> naver_blog_comment_capturer.py
    echo     try:>> naver_blog_comment_capturer.py
    echo         with open('config.txt', 'r') as file:>> naver_blog_comment_capturer.py
    echo             lines = file.readlines()>> naver_blog_comment_capturer.py
    echo             naver_id = lines[0].strip()>> naver_blog_comment_capturer.py
    echo             naver_pw = lines[1].strip()>> naver_blog_comment_capturer.py
    echo         return naver_id, naver_pw>> naver_blog_comment_capturer.py
    echo     except:>> naver_blog_comment_capturer.py
    echo         print("로그인 정보를 읽어오는 데 실패했습니다. setup.bat을 다시 실행해주세요.")>> naver_blog_comment_capturer.py
    echo         input("아무 키나 눌러 종료...")>> naver_blog_comment_capturer.py
    echo         exit(1)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo def setup_driver():>> naver_blog_comment_capturer.py
    echo     """크롬 드라이버를 설정합니다.""">> naver_blog_comment_capturer.py
    echo     try:>> naver_blog_comment_capturer.py
    echo         chrome_options = Options()>> naver_blog_comment_capturer.py
    echo         chrome_options.add_argument("--start-maximized")>> naver_blog_comment_capturer.py
    echo         chrome_options.add_experimental_option("detach", True)  # 브라우저 자동 종료 방지>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         service = Service(ChromeDriverManager().install())>> naver_blog_comment_capturer.py
    echo         driver = webdriver.Chrome(service=service, options=chrome_options)>> naver_blog_comment_capturer.py
    echo         return driver>> naver_blog_comment_capturer.py
    echo     except Exception as e:>> naver_blog_comment_capturer.py
    echo         print(f"드라이버 설정 중 오류가 발생했습니다: {e}")>> naver_blog_comment_capturer.py
    echo         input("아무 키나 눌러 종료...")>> naver_blog_comment_capturer.py
    echo         exit(1)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo def login_to_naver(driver, naver_id, naver_pw):>> naver_blog_comment_capturer.py
    echo     """네이버에 로그인합니다.""">> naver_blog_comment_capturer.py
    echo     try:>> naver_blog_comment_capturer.py
    echo         print("네이버 로그인 페이지로 이동합니다...")>> naver_blog_comment_capturer.py
    echo         driver.get("https://nid.naver.com/nidlogin.login")>> naver_blog_comment_capturer.py
    echo         time.sleep(1)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         # 자바스크립트로 직접 ID와 비밀번호 입력 (봇 감지 우회)>> naver_blog_comment_capturer.py
    echo         driver.execute_script(f"document.getElementsByName('id')[0].value='{naver_id}'")>> naver_blog_comment_capturer.py
    echo         time.sleep(0.5)>> naver_blog_comment_capturer.py
    echo         driver.execute_script(f"document.getElementsByName('pw')[0].value='{naver_pw}'")>> naver_blog_comment_capturer.py
    echo         time.sleep(0.5)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         # 로그인 버튼 클릭>> naver_blog_comment_capturer.py
    echo         print("로그인 중...")>> naver_blog_comment_capturer.py
    echo         login_button = driver.find_element(By.ID, "log.login")>> naver_blog_comment_capturer.py
    echo         login_button.click()>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         # 로그인 성공 대기>> naver_blog_comment_capturer.py
    echo         time.sleep(3)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         # 로그인 성공 여부 확인>> naver_blog_comment_capturer.py
    echo         if "로그인" in driver.title:>> naver_blog_comment_capturer.py
    echo             print("자동 로그인에 실패했습니다. 캡차 인증이 필요할 수 있습니다.")>> naver_blog_comment_capturer.py
    echo             print("브라우저에서 직접 로그인을 완료해주세요.")>> naver_blog_comment_capturer.py
    echo             input("로그인을 완료한 후 여기에서 Enter 키를 눌러주세요...")>> naver_blog_comment_capturer.py
    echo         else:>> naver_blog_comment_capturer.py
    echo             print("네이버 로그인 성공!")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     except Exception as e:>> naver_blog_comment_capturer.py
    echo         print(f"로그인 중 오류가 발생했습니다: {e}")>> naver_blog_comment_capturer.py
    echo         print("브라우저에서 직접 로그인을 완료해주세요.")>> naver_blog_comment_capturer.py
    echo         input("로그인을 완료한 후 여기에서 Enter 키를 눌러주세요...")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo def go_to_blog_post(driver, blog_url):>> naver_blog_comment_capturer.py
    echo     """입력받은 블로그 포스트 페이지로 이동합니다.""">> naver_blog_comment_capturer.py
    echo     try:>> naver_blog_comment_capturer.py
    echo         print(f"블로그 포스트 페이지로 이동합니다: {blog_url}")>> naver_blog_comment_capturer.py
    echo         driver.get(blog_url)>> naver_blog_comment_capturer.py
    echo         time.sleep(3)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         # 블로그 포스트가 iframe 내부에 있는지 확인>> naver_blog_comment_capturer.py
    echo         try:>> naver_blog_comment_capturer.py
    echo             # 주요 iframe ID들>> naver_blog_comment_capturer.py
    echo             iframe_ids = ["mainFrame", "cafe_main"]>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo             for iframe_id in iframe_ids:>> naver_blog_comment_capturer.py
    echo                 try:>> naver_blog_comment_capturer.py
    echo                     iframe = WebDriverWait(driver, 5).until(>> naver_blog_comment_capturer.py
    echo                         EC.presence_of_element_located((By.ID, iframe_id))>> naver_blog_comment_capturer.py
    echo                     )>> naver_blog_comment_capturer.py
    echo                     driver.switch_to.frame(iframe)>> naver_blog_comment_capturer.py
    echo                     print(f"iframe({iframe_id})으로 전환했습니다.")>> naver_blog_comment_capturer.py
    echo                     break>> naver_blog_comment_capturer.py
    echo                 except:>> naver_blog_comment_capturer.py
    echo                     continue>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         except Exception as e:>> naver_blog_comment_capturer.py
    echo             print(f"iframe 전환 실패: {e}")>> naver_blog_comment_capturer.py
    echo             print("메인 페이지에서 계속 진행합니다.")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         return True>> naver_blog_comment_capturer.py
    echo     except Exception as e:>> naver_blog_comment_capturer.py
    echo         print(f"블로그 페이지 이동 중 오류가 발생했습니다: {e}")>> naver_blog_comment_capturer.py
    echo         return False>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo def capture_comments(driver):>> naver_blog_comment_capturer.py
    echo     """블로그 포스트의 댓글 영역을 찾아 캡처합니다.""">> naver_blog_comment_capturer.py
    echo     # 댓글 영역 선택자 리스트 (네이버 블로그 버전별로 다를 수 있음)>> naver_blog_comment_capturer.py
    echo     comment_selectors = [>> naver_blog_comment_capturer.py
    echo         ".area_comment", >> naver_blog_comment_capturer.py
    echo         "#cbox_module",>> naver_blog_comment_capturer.py
    echo         ".comment_area",>> naver_blog_comment_capturer.py
    echo         ".comment-box",>> naver_blog_comment_capturer.py
    echo         ".commentBox",>> naver_blog_comment_capturer.py
    echo         ".comment_wrap",>> naver_blog_comment_capturer.py
    echo         ".u_cbox",>> naver_blog_comment_capturer.py
    echo         ".u_cbox_content_wrap",>> naver_blog_comment_capturer.py
    echo         ".u_cbox_list",>> naver_blog_comment_capturer.py
    echo         ".list_comment", >> naver_blog_comment_capturer.py
    echo         ".comment_list">> naver_blog_comment_capturer.py
    echo     ]>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     # 댓글 더보기 버튼 선택자 리스트>> naver_blog_comment_capturer.py
    echo     more_comment_selectors = [>> naver_blog_comment_capturer.py
    echo         ".btn_more", >> naver_blog_comment_capturer.py
    echo         ".u_cbox_more_btn",>> naver_blog_comment_capturer.py
    echo         ".u_cbox_page_more",>> naver_blog_comment_capturer.py
    echo         ".link_more", >> naver_blog_comment_capturer.py
    echo         ".more_comment", >> naver_blog_comment_capturer.py
    echo         ".btn_comment_more",>> naver_blog_comment_capturer.py
    echo         "a:contains('댓글 더보기')">> naver_blog_comment_capturer.py
    echo     ]>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     # 현재 시간을 이용한 파일명 생성>> naver_blog_comment_capturer.py
    echo     timestamp = datetime.datetime.now().strftime("%%Y%%m%%d_%%H%%M%%S")>> naver_blog_comment_capturer.py
    echo     screenshot_folder = "screenshots">> naver_blog_comment_capturer.py
    echo     os.makedirs(screenshot_folder, exist_ok=True)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     # 찾은 댓글 영역 수>> naver_blog_comment_capturer.py
    echo     comment_count = 0>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     print("\n댓글 영역을 찾고 캡처합니다...")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     # 모든 댓글을 보기 위해 '더보기' 버튼 클릭 시도>> naver_blog_comment_capturer.py
    echo     for selector in more_comment_selectors:>> naver_blog_comment_capturer.py
    echo         try:>> naver_blog_comment_capturer.py
    echo             while True:>> naver_blog_comment_capturer.py
    echo                 more_buttons = driver.find_elements(By.CSS_SELECTOR, selector)>> naver_blog_comment_capturer.py
    echo                 if not more_buttons or not more_buttons[0].is_displayed():>> naver_blog_comment_capturer.py
    echo                     break>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo                 print("댓글 더보기 버튼을 클릭합니다...")>> naver_blog_comment_capturer.py
    echo                 driver.execute_script("arguments[0].click();", more_buttons[0])>> naver_blog_comment_capturer.py
    echo                 time.sleep(1)>> naver_blog_comment_capturer.py
    echo         except Exception as e:>> naver_blog_comment_capturer.py
    echo             continue>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     print("댓글을 모두 펼쳤습니다.")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     # 댓글 영역 찾기 및 캡처>> naver_blog_comment_capturer.py
    echo     for selector in comment_selectors:>> naver_blog_comment_capturer.py
    echo         try:>> naver_blog_comment_capturer.py
    echo             comment_elements = driver.find_elements(By.CSS_SELECTOR, selector)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo             if not comment_elements:>> naver_blog_comment_capturer.py
    echo                 continue>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo             for i, element in enumerate(comment_elements):>> naver_blog_comment_capturer.py
    echo                 try:>> naver_blog_comment_capturer.py
    echo                     # 요소가 보이도록 스크롤>> naver_blog_comment_capturer.py
    echo                     driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)>> naver_blog_comment_capturer.py
    echo                     time.sleep(0.5)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo                     # 요소의 위치와 크기 가져오기>> naver_blog_comment_capturer.py
    echo                     location = element.location>> naver_blog_comment_capturer.py
    echo                     size = element.size>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo                     # 요소 크기가 너무 작으면 건너뛰기 (실제 댓글 영역이 아닐 가능성)>> naver_blog_comment_capturer.py
    echo                     if size['width'] ^< 100 or size['height'] ^< 50:>> naver_blog_comment_capturer.py
    echo                         continue>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo                     # 스크린샷 촬영>> naver_blog_comment_capturer.py
    echo                     file_name = f"{screenshot_folder}/comment_{timestamp}_{i+1}.png">> naver_blog_comment_capturer.py
    echo                     element.screenshot(file_name)>> naver_blog_comment_capturer.py
    echo                     print(f"댓글 영역 캡처 완료: {file_name}")>> naver_blog_comment_capturer.py
    echo                     comment_count += 1>> naver_blog_comment_capturer.py
    echo                 except Exception as e:>> naver_blog_comment_capturer.py
    echo                     print(f"댓글 요소 캡처 실패: {e}")>> naver_blog_comment_capturer.py
    echo                     continue>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo             if comment_count ^> 0:>> naver_blog_comment_capturer.py
    echo                 print(f"총 {comment_count}개의 댓글 영역을 캡처했습니다.")>> naver_blog_comment_capturer.py
    echo                 break>> naver_blog_comment_capturer.py
    echo         except Exception as e:>> naver_blog_comment_capturer.py
    echo             continue>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     if comment_count == 0:>> naver_blog_comment_capturer.py
    echo         print("댓글 영역을 찾을 수 없거나 댓글이 없습니다.")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         # 전체 페이지 스크린샷 대신 찍기>> naver_blog_comment_capturer.py
    echo         try:>> naver_blog_comment_capturer.py
    echo             file_name = f"{screenshot_folder}/full_page_{timestamp}.png">> naver_blog_comment_capturer.py
    echo             driver.save_screenshot(file_name)>> naver_blog_comment_capturer.py
    echo             print(f"전체 페이지 스크린샷을 저장했습니다: {file_name}")>> naver_blog_comment_capturer.py
    echo         except Exception as e:>> naver_blog_comment_capturer.py
    echo             print(f"전체 페이지 스크린샷 저장 실패: {e}")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     return comment_count>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo def main():>> naver_blog_comment_capturer.py
    echo     print("=" * 50)>> naver_blog_comment_capturer.py
    echo     print("네이버 블로그 댓글 캡처 도구를 시작합니다")>> naver_blog_comment_capturer.py
    echo     print("=" * 50)>> naver_blog_comment_capturer.py
    echo     print()>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     # 설정 파일에서 로그인 정보 읽기>> naver_blog_comment_capturer.py
    echo     naver_id, naver_pw = read_config()>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     # 블로그 주소 입력 받기>> naver_blog_comment_capturer.py
    echo     blog_url = input("네이버 블로그 포스트 URL을 입력하세요: ")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     if not blog_url.startswith("http"):>> naver_blog_comment_capturer.py
    echo         blog_url = "https://" + blog_url>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     # 드라이버 설정>> naver_blog_comment_capturer.py
    echo     driver = setup_driver()>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     try:>> naver_blog_comment_capturer.py
    echo         # 네이버 로그인>> naver_blog_comment_capturer.py
    echo         login_to_naver(driver, naver_id, naver_pw)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo         # 블로그 포스트 페이지로 이동>> naver_blog_comment_capturer.py
    echo         if go_to_blog_post(driver, blog_url):>> naver_blog_comment_capturer.py
    echo             # 댓글 캡처>> naver_blog_comment_capturer.py
    echo             comment_count = capture_comments(driver)>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo             if comment_count ^> 0:>> naver_blog_comment_capturer.py
    echo                 print(f"\n작업이 완료되었습니다. 캡처된 {comment_count}개의 이미지는 'screenshots' 폴더에 저장되었습니다.")>> naver_blog_comment_capturer.py
    echo                 os.startfile(os.path.abspath("screenshots"))>> naver_blog_comment_capturer.py
    echo             else:>> naver_blog_comment_capturer.py
    echo                 print("\n댓글 캡처에 실패했습니다. 다른 블로그 주소를 시도해보세요.")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     except Exception as e:>> naver_blog_comment_capturer.py
    echo         print(f"오류가 발생했습니다: {e}")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo     print("\n브라우저는 수동으로 닫아주세요.")>> naver_blog_comment_capturer.py
    echo     input("프로그램을 종료하려면 아무 키나 누르세요...")>> naver_blog_comment_capturer.py
    echo.>> naver_blog_comment_capturer.py
    echo if __name__ == "__main__":>> naver_blog_comment_capturer.py
    echo     main()>> naver_blog_comment_capturer.py
)

echo.
echo ====================================================
echo 모든 준비가 완료되었습니다! 
echo 이제 네이버 블로그 댓글 캡처 도구를 시작합니다...
echo ====================================================
echo.

REM 크롤러 실행
python naver_blog_comment_capturer.py

REM 가상환경 비활성화
call venv\Scripts\deactivate.bat

pause