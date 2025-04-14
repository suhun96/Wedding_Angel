@echo off
echo 네이버 블로그 댓글 캡처 도구를 실행합니다...
echo.

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 패키지 업데이트 확인 및 설치
echo 필요한 패키지가 모두 설치되어 있는지 확인합니다...
pip install selenium webdriver-manager pillow --quiet

REM 크롤러 실행
python naver_blog_comment_capturer.py

REM 가상환경 비활성화
call venv\Scripts\deactivate.bat

pause