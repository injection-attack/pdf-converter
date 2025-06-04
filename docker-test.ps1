# Windows PowerShell용 Docker 테스트 스크립트

Write-Host "🐳 Docker 이미지 빌드 및 테스트" -ForegroundColor Cyan

# 이미지 이름
$IMAGE_NAME = "pdf-converter"
$CONTAINER_NAME = "pdf-converter-test"

# Docker가 실행 중인지 확인
Write-Host "🔍 Docker 상태 확인 중..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker 확인됨: $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker가 설치되지 않았거나 실행 중이 아닙니다." -ForegroundColor Red
    Write-Host "💡 Docker Desktop을 설치하고 실행해주세요." -ForegroundColor Yellow
    exit 1
}

# 기존 컨테이너 정리
Write-Host "🧹 기존 컨테이너 정리..." -ForegroundColor Yellow
docker stop $CONTAINER_NAME 2>$null | Out-Null
docker rm $CONTAINER_NAME 2>$null | Out-Null

# Docker 이미지 빌드
Write-Host "🔨 Docker 이미지 빌드 중..." -ForegroundColor Blue
docker build -t $IMAGE_NAME .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 이미지 빌드 성공!" -ForegroundColor Green
    
    # 컨테이너 실행
    Write-Host "🚀 컨테이너 실행 중..." -ForegroundColor Blue
    docker run -d --name $CONTAINER_NAME -p 8000:8000 $IMAGE_NAME
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 컨테이너 실행 성공!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 접속 주소:" -ForegroundColor Cyan
        Write-Host "   메인 페이지: http://localhost:8000" -ForegroundColor White
        Write-Host "   API 문서:   http://localhost:8000/docs" -ForegroundColor White
        Write-Host "   서버 상태:  http://localhost:8000/health" -ForegroundColor White
        Write-Host ""
        Write-Host "📋 Docker 명령어:" -ForegroundColor Cyan
        Write-Host "   로그 확인:    docker logs $CONTAINER_NAME" -ForegroundColor White
        Write-Host "   컨테이너 중지: docker stop $CONTAINER_NAME" -ForegroundColor White
        Write-Host "   컨테이너 제거: docker rm $CONTAINER_NAME" -ForegroundColor White
        Write-Host ""
        Write-Host "⏱️  30초 후 헬스체크 실행..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        
        # 헬스체크
        Write-Host "🔍 헬스체크 중..." -ForegroundColor Blue
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
            Write-Host "✅ 헬스체크 성공! 서버가 정상 동작 중입니다." -ForegroundColor Green
            Write-Host "📊 서버 상태:" -ForegroundColor Cyan
            $response | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor White
            
            # 브라우저 열기
            Write-Host ""
            Write-Host "🌐 브라우저를 열까요? (y/N): " -ForegroundColor Yellow -NoNewline
            $open = Read-Host
            if ($open -eq 'y' -or $open -eq 'Y') {
                Start-Process "http://localhost:8000"
                Write-Host "✅ 브라우저에서 열었습니다!" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "❌ 헬스체크 실패. 로그를 확인하세요:" -ForegroundColor Red
            docker logs $CONTAINER_NAME
        }
        
    } else {
        Write-Host "❌ 컨테이너 실행 실패" -ForegroundColor Red
        exit 1
    }
    
} else {
    Write-Host "❌ 이미지 빌드 실패" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 테스트 완료!" -ForegroundColor Green