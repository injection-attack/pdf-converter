# Python 3.12 슬림 이미지 사용 (가벼움)
FROM python:3.12-slim

# 메타데이터
LABEL maintainer="PDF Converter App"
LABEL description="Image to PDF converter web application"

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 이미지 처리 라이브러리 설치
RUN apt-get update && apt-get install -y \
    # 이미지 처리용 라이브러리들
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    # 빌드 도구 (설치 후 삭제 예정)
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python 의존성 파일 복사 (캐싱 최적화)
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 불필요한 빌드 도구 제거 (이미지 크기 최적화)
RUN apt-get remove -y gcc g++ && \
    apt-get autoremove -y

# 애플리케이션 코드 복사
COPY app.py .
COPY converter.py .
COPY static/ ./static/
COPY templates/ ./templates/

# 임시 폴더 생성 및 권한 설정
RUN mkdir -p temp_uploads temp_outputs && \
    chmod 755 temp_uploads temp_outputs

# 비루트 사용자 생성 (보안 강화)
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# 비루트 사용자로 전환
USER app

# 포트 노출 (Railway가 자동으로 설정)
EXPOSE 8000

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 서버 실행 명령어
CMD ["python", "app.py"]