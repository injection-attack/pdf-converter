@echo off
chcp 65001 >nul
echo.
echo 🐳 Docker 이미지 빌드 및 테스트
echo ================================

set IMAGE_NAME=pdf-converter
set CONTAINER_NAME=pdf-converter-test

echo.
echo 🔍 Docker 상태 확인 중...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker가 설치되지 않았거나 실행 중이 아닙니다.
    echo 💡 Docker Desktop을 설치하고 실행해주세요.
    pause
    exit /b 1
)
echo ✅ Docker 확인됨

echo.
echo 🧹 기존 컨테이너 정리...
docker stop %CONTAINER_NAME% >nul 2>&1
docker rm %CONTAINER_NAME% >nul 2>&1

echo.
echo 🔨 Docker 이미지 빌드 중...
docker build -t %IMAGE_NAME% .
if %errorlevel% neq 0 (
    echo ❌ 이미지 빌드 실패
    pause
    exit /b 1
)
echo ✅ 이미지 빌드 성공!

echo.
echo 🚀 컨테이너 실행 중...
docker run -d --name %CONTAINER_NAME% -p 8000:8000 %IMAGE_NAME%
if %errorlevel% neq 0 (
    echo ❌ 컨테이너 실행 실패
    pause
    exit /b 1
)
echo ✅ 컨테이너 실행 성공!

echo.
echo 🌐 접속 주소:
echo    메인 페이지: http://localhost:8000
echo    API 문서:   http://localhost:8000/docs
echo    서버 상태:  http://localhost:8000/health
echo.
echo 📋 Docker 명령어:
echo    로그 확인:    docker logs %CONTAINER_NAME%
echo    컨테이너 중지: docker stop %CONTAINER_NAME%
echo    컨테이너 제거: docker rm %CONTAINER_NAME%

echo.
echo ⏱️  30초 후 헬스체크 실행...
timeout /t 30 /nobreak >nul

echo.
echo 🔍 헬스체크 중...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% eq 0 (
    echo ✅ 헬스체크 성공! 서버가 정상 동작 중입니다.
    echo.
    set /p open="🌐 브라우저를 열까요? (y/N): "
    if /i "%open%"=="y" (
        start http://localhost:8000
        echo ✅ 브라우저에서 열었습니다!
    )
) else (
    echo ❌ 헬스체크 실패. 로그를 확인하세요:
    docker logs %CONTAINER_NAME%
)

echo.
echo 🎉 테스트 완료!
pause