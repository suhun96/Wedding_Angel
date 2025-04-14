@echo off
echo ===== 네이버 블로그 댓글 수집기 환경 설정 =====
echo 가상 환경 생성 및 패키지 설치를 시작합니다...

REM Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python이 설치되어 있지 않습니다. Python을 먼저 설치해주세요.
    echo https://www.python.org/downloads/
    pause
    exit /b
)

REM 가상환경 설정
if not exist "venv" (
    echo 가상환경을 생성합니다...
    python -m venv venv
) else (
    echo 이미 가상환경이 존재합니다.
)

REM 가상환경 활성화 및 패키지 설치
echo 가상환경을 활성화하고 필요한 패키지를 설치합니다...
call venv\Scripts\activate.bat
pip install selenium requests webdriver-manager pillow

REM 최신 크롬 드라이버 다운로드와 설정은 webdriver-manager가 자동으로 처리

echo.
echo ===== 설정 완료! =====
echo 이제 naver_comment_scraper.py를 실행하여 프로그램을 시작하세요.
echo.
python naver_comment_scraper.py
pause