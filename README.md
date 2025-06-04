# 🖼️ PDF Converter

이미지 파일들을 PDF로 변환하는 Python 프로그램입니다.

## 📁 프로젝트 구조

```
PDF_CONVERTER/
├── images/           # 테스트용 이미지들
├── output/           # 생성된 PDF 저장
├── app.py           # 웹서버 (FastAPI)
├── converter.py     # CLI 프로그램
├── environment.yml  # Conda 환경
└── README.md        # 이 파일
```

## 🚀 설치 및 실행

### 1. 환경 설정
```bash
conda env create -f environment.yml
conda activate image_to_pdf
```

### 2. 사용 방법

**CLI 모드 (터미널):**
```bash
# 개별 파일 변환
python converter.py image1.jpg image2.png -o result.pdf

# 폴더 전체 변환
python converter.py images/ --folder -o combined.pdf

# 대화형 모드
python converter.py
```

**웹서버 모드 (브라우저):**
```bash
# 서버 시작
python app.py

# 브라우저에서 접속
# http://localhost:8000
```

## ✨ 기능

- 📸 **지원 형식**: JPG, PNG, BMP, TIFF, GIF, WebP
- 📚 **배치 변환**: 여러 이미지를 하나의 PDF로
- 🎛️ **품질 조절**: 1-100 범위에서 설정
- 🌐 **웹 인터페이스**: 드래그 앤 드롭 지원
- 📱 **반응형**: 모바일에서도 사용 가능

## 📡 API 사용

**파일 업로드:**
```bash
curl -X POST "http://localhost:8000/convert" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -F "quality=90" \
  --output result.pdf
```

## 🛠️ 개발자 정보

- **CLI**: `converter.py` - 터미널에서 사용
- **웹서버**: `app.py` - 웹 브라우저에서 사용
- **API 문서**: http://localhost:8000/docs

## 📋 요구사항

- Python 3.12+
- Pillow (이미지 처리)
- FastAPI + uvicorn (웹서버)

---

**🎉 즐거운 PDF 변환 되세요!**