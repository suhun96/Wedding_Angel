@echo off
chcp 65001 > nul
cls

echo ===== 네이버 블로그 댓글 테스트 =====
echo.

REM Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python이 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b
)

REM 필요한 패키지 설치
echo 필요한 패키지를 설치합니다...
pip install selenium webdriver-manager

REM 테스트 스크립트 실행
echo.                                     
echo 테스트 스크립트를 실행합니다...
echo.
python naver_comment_test.py

pause