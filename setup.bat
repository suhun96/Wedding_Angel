@echo off
chcp 65001 > nul
echo ======================================================
echo      네이버 블로그 댓글 캡처 도구 설치를 시작합니다
echo ======================================================
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

echo.
echo 설치가 완료되었습니다!
echo 네이버 블로그 댓글 캡처 도구를 실행하려면 run.bat 파일을 더블클릭하세요.
echo.
pause