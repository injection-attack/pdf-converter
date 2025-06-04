#!/usr/bin/env python3
"""
FastAPI 웹서버 - 이미지를 PDF로 변환
브라우저에서 드래그 앤 드롭으로 이미지 업로드 후 PDF 변환
"""

import os
import uuid
import shutil
from datetime import datetime, timedelta
from typing import List
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# 기존 변환 모듈 import
from converter import ImageToPDFConverter, ImageFinder

print("🚀 FastAPI 이미지-PDF 변환 서버 시작")

# Pillow 버전 확인
try:
    from PIL import Image
    print(f"💡 Pillow 버전: {Image.__version__}")
except Exception as e:
    print(f"⚠️  Pillow 로드 실패: {e}")

# 임시 파일 저장소 (자동 생성됨)
UPLOAD_FOLDER = "temp_uploads"
OUTPUT_FOLDER = "temp_outputs"

# 폴더 자동 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

print(f"📁 임시 폴더 생성: {UPLOAD_FOLDER}")
print(f"📁 임시 폴더 생성: {OUTPUT_FOLDER}")

# FastAPI 앱 생성
app = FastAPI(
    title="🖼️ Image to PDF Converter",
    description="이미지 파일들을 PDF로 변환하는 웹 서비스",
    version="1.0.0"
)

# 정적 파일과 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/convert")
async def convert_images(
    files: List[UploadFile] = File(...),
    quality: int = Form(95)
):
    """
    이미지 파일들을 PDF로 변환
    
    Args:
        files: 업로드된 이미지 파일들
        quality: 이미지 품질 (1-100)
    
    Returns:
        변환된 PDF 파일
    """
    if not files:
        raise HTTPException(status_code=400, detail="업로드된 파일이 없습니다")
    
    # 세션 ID 생성 (고유한 작업 식별용)
    session_id = str(uuid.uuid4())
    session_upload_dir = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_upload_dir, exist_ok=True)
    
    try:
        # 업로드된 파일들 저장
        image_paths = []
        supported_types = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 
            'image/gif', 'image/webp'
        ]
        
        for file in files:
            if file.content_type not in supported_types:
                continue
                
            # 안전한 파일명 생성
            file_extension = Path(file.filename).suffix.lower()
            safe_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(session_upload_dir, safe_filename)
            
            # 파일 저장
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            image_paths.append(file_path)
        
        if not image_paths:
            raise HTTPException(status_code=400, detail="유효한 이미지 파일이 없습니다")
        
        # PDF 변환
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"converted_{timestamp}_{session_id[:8]}.pdf"
        pdf_path = os.path.join(OUTPUT_FOLDER, pdf_filename)
        
        # 이미지들을 이름순으로 정렬
        image_paths.sort()
        
        converter = ImageToPDFConverter(quality)
        success = converter.convert_images_to_pdf(image_paths, pdf_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="PDF 변환에 실패했습니다")
        
        print(f"✅ PDF 변환 완료: {pdf_filename}")
        
        # 변환된 PDF 반환
        def cleanup():
            """임시 파일 정리"""
            try:
                if os.path.exists(session_upload_dir):
                    shutil.rmtree(session_upload_dir)
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                print(f"🧹 임시 파일 정리 완료: {session_id}")
            except Exception as e:
                print(f"⚠️  정리 중 오류: {e}")
        
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=f"converted_images_{timestamp}.pdf",
            background=cleanup  # 다운로드 후 자동 정리
        )
        
    except Exception as e:
        # 오류 발생시 임시 파일 정리
        try:
            if os.path.exists(session_upload_dir):
                shutil.rmtree(session_upload_dir)
        except:
            pass
        
        print(f"❌ 변환 오류: {e}")
        raise HTTPException(status_code=500, detail=f"변환 중 오류 발생: {str(e)}")


@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "upload_folder": UPLOAD_FOLDER,
        "output_folder": OUTPUT_FOLDER,
        "folders_exist": {
            "upload": os.path.exists(UPLOAD_FOLDER),
            "output": os.path.exists(OUTPUT_FOLDER),
            "static": os.path.exists("static"),
            "templates": os.path.exists("templates")
        }
    }


@app.on_event("startup")
async def startup_event():
    """서버 시작시 실행"""
    print("✅ 서버 시작 완료")
    print(f"📁 업로드 폴더: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"📁 출력 폴더: {os.path.abspath(OUTPUT_FOLDER)}")


def cleanup_old_files():
    """1시간 이상 된 임시 파일들 정리"""
    try:
        now = datetime.now()
        cutoff_time = now - timedelta(hours=1)
        
        # 임시 업로드 폴더 정리
        for item in os.listdir(UPLOAD_FOLDER):
            item_path = os.path.join(UPLOAD_FOLDER, item)
            if os.path.isdir(item_path):
                item_time = datetime.fromtimestamp(os.path.getctime(item_path))
                if item_time < cutoff_time:
                    shutil.rmtree(item_path)
                    print(f"🧹 오래된 업로드 폴더 정리: {item}")
        
        # 임시 출력 파일 정리
        for item in os.listdir(OUTPUT_FOLDER):
            item_path = os.path.join(OUTPUT_FOLDER, item)
            if os.path.isfile(item_path):
                item_time = datetime.fromtimestamp(os.path.getctime(item_path))
                if item_time < cutoff_time:
                    os.remove(item_path)
                    print(f"🧹 오래된 PDF 파일 정리: {item}")
                    
    except Exception as e:
        print(f"⚠️  파일 정리 중 오류: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료시 정리"""
    print("🛑 서버 종료 중...")
    cleanup_old_files()
    print("👋 서버 종료 완료")


if __name__ == "__main__":
    print("\n🌟 서버 실행 방법:")
    print("   브라우저에서 http://localhost:8000 접속")
    print("   API 문서: http://localhost:8000/docs")
    print("   서버 상태: http://localhost:8000/health")
    print("\n⏹️  종료하려면 Ctrl+C를 누르세요.\n")
    
    # 서버 실행
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000,
        reload=False  # 프로덕션에서는 False
    )