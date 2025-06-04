#!/usr/bin/env python3
"""
FastAPI 웹서버 - 이미지를 PDF로 변환
개별 PDF ZIP 다운로드 기능 포함
"""

import os
import zipfile
from uuid import uuid4
from datetime import datetime
from typing import List
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask
import uvicorn
from PIL import Image

print("🚀 FastAPI 이미지-PDF 변환 서버 시작")

# 임시 디렉토리 설정
UPLOAD_DIR = "temp_uploads"
OUTPUT_DIR = "temp_outputs"

# 디렉토리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

print(f"📁 업로드 폴더: {UPLOAD_DIR}")
print(f"📁 출력 폴더: {OUTPUT_DIR}")

# FastAPI 앱 생성
app = FastAPI(
    title="🖼️ Image to PDF Converter",
    description="이미지를 PDF로 변환하는 웹 서비스 (개별/합본 지원)",
    version="2.0.0"
)

# 정적 파일과 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def cleanup_files(file_paths: List[str]) -> None:
    """임시 파일들을 정리하는 함수"""
    if not file_paths:
        return
        
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   🗑️  삭제: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"   ❌ 삭제 실패: {os.path.basename(file_path)} - {str(e)}")
    
    print(f"🧹 임시 파일 정리 완료")


def create_pdf_from_images(image_paths: List[str], output_path: str, quality: int = 95):
    """이미지들을 PDF로 변환"""
    if not image_paths:
        raise ValueError("이미지 파일이 없습니다.")
    
    print(f"   🖼️  이미지 파일 처리 시작: {len(image_paths)}개")
    
    try:
        images = []
        
        for i, image_path in enumerate(image_paths):
            print(f"   📖 처리 중: {os.path.basename(image_path)}")
            
            # 파일 존재 확인
            if not os.path.exists(image_path):
                print(f"   ❌ 파일 없음: {image_path}")
                continue
                
            try:
                # 이미지 열기
                with Image.open(image_path) as img:
                    print(f"   ✅ 이미지 로드: {img.size}, {img.mode}")
                    
                    # 이미지 복사 (원본 보호)
                    img_copy = img.copy()
                    
                    # RGBA를 RGB로 변환 (PDF는 RGBA 지원 안 함)
                    if img_copy.mode in ('RGBA', 'LA', 'P'):
                        print(f"   🔄 모드 변환: {img_copy.mode} → RGB")
                        # 흰색 배경으로 변환
                        background = Image.new('RGB', img_copy.size, (255, 255, 255))
                        if img_copy.mode == 'P':
                            img_copy = img_copy.convert('RGBA')
                        if img_copy.mode == 'RGBA':
                            background.paste(img_copy, mask=img_copy.split()[-1])
                        else:
                            background.paste(img_copy)
                        img_copy = background
                    elif img_copy.mode != 'RGB':
                        print(f"   🔄 모드 변환: {img_copy.mode} → RGB")
                        img_copy = img_copy.convert('RGB')
                    
                    # 이미지 품질 최적화
                    if quality < 95:
                        print(f"   🎯 품질 최적화: {quality}%")
                        import io
                        buffer = io.BytesIO()
                        img_copy.save(buffer, format='JPEG', quality=quality, optimize=True)
                        buffer.seek(0)
                        img_copy = Image.open(buffer)
                        # 버퍼에서 다시 복사하여 메모리 안전성 확보
                        img_copy = img_copy.copy()
                        buffer.close()
                    
                    images.append(img_copy)
                    print(f"   ✅ 이미지 추가 완료: #{i+1}")
                
            except Exception as img_error:
                print(f"   ❌ 이미지 처리 실패: {os.path.basename(image_path)} - {str(img_error)}")
                continue
        
        # 변환된 이미지 확인
        if not images:
            raise ValueError("처리 가능한 이미지가 없습니다.")
            
        print(f"   📄 PDF 생성 시작: {len(images)}개 이미지")
        
        # 출력 디렉토리 확인
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # PDF 저장
        images[0].save(
            output_path,
            "PDF",
            resolution=150.0,
            save_all=True,
            append_images=images[1:] if len(images) > 1 else None,
            quality=quality if quality >= 95 else 95  # PDF 저장시 품질 보정
        )
        
        # 파일 생성 확인
        if not os.path.exists(output_path):
            raise Exception("PDF 파일이 생성되지 않았습니다.")
            
        file_size = os.path.getsize(output_path)
        print(f"   📄 PDF 생성 완료: {len(images)}개 이미지 → {os.path.basename(output_path)} ({file_size:,} bytes)")
        
        # 이미지 객체들 메모리 해제
        for img in images:
            img.close()
        
    except Exception as e:
        print(f"   ❌ PDF 생성 오류: {str(e)}")
        # 실패한 PDF 파일 삭제
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        raise Exception(f"PDF 생성 실패: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/convert")
async def convert_images(
    files: List[UploadFile] = File(...),
    convert_type: str = Form("merged"),  # "merged" 또는 "individual"
    filename: str = Form("converted"),
    quality: int = Form(95)
):
    """
    이미지를 PDF로 변환하는 API
    
    Args:
        files: 업로드된 이미지 파일들
        convert_type: 변환 타입 ("merged": 합본, "individual": 개별)
        filename: 출력 파일명 (확장자 제외)
        quality: 이미지 품질 (1-100)
    
    Returns:
        - merged: PDF 파일 직접 반환
        - individual: ZIP 파일 다운로드 URL 반환
    """
    if not files:
        raise HTTPException(status_code=400, detail="파일이 업로드되지 않았습니다.")
    
    print(f"\n📥 변환 요청:")
    print(f"   파일 수: {len(files)}")
    print(f"   변환 타입: {convert_type}")
    print(f"   파일명: {filename}")
    print(f"   품질: {quality}")
    
    temp_files = []
    output_paths = []
    
    try:
        # 안전한 파일명 생성
        safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_filename:
            safe_filename = "converted"
        
        # 1. 업로드된 파일들 저장
        for i, file in enumerate(files):
            print(f"   📥 처리 중: {file.filename}")
            
            # 파일 형식 검증
            if not file.content_type or not file.content_type.startswith('image/'):
                print(f"   ❌ 지원하지 않는 형식: {file.content_type}")
                raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식: {file.filename}")
            
            # 파일 내용 읽기
            content = await file.read()
            if not content:
                print(f"   ❌ 빈 파일: {file.filename}")
                continue
                
            # 임시 파일 저장
            file_extension = os.path.splitext(file.filename)[1].lower()
            if not file_extension:
                file_extension = '.jpg'  # 기본 확장자
                
            temp_file_path = os.path.join(UPLOAD_DIR, f"{uuid4()}{file_extension}")
            
            try:
                with open(temp_file_path, "wb") as buffer:
                    buffer.write(content)
                
                # 파일 크기 확인
                file_size = os.path.getsize(temp_file_path)
                if file_size == 0:
                    print(f"   ❌ 빈 파일 저장됨: {file.filename}")
                    os.remove(temp_file_path)
                    continue
                    
                temp_files.append(temp_file_path)
                print(f"   💾 저장 완료: {file.filename} ({file_size:,} bytes)")
                
            except Exception as save_error:
                print(f"   ❌ 저장 실패: {file.filename} - {str(save_error)}")
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                continue
        
        # 저장된 파일 확인
        if not temp_files:
            raise HTTPException(status_code=400, detail="처리 가능한 이미지 파일이 없습니다.")
        
        # 2. 변환 타입에 따라 처리
        print(f"   🔄 변환 타입 체크: '{convert_type}', 파일 수: {len(files)}")
        
        if convert_type == "individual" and len(files) > 1:
            print(f"   📦 개별 PDF 모드 실행")
            # 개별 PDF 생성
            zip_filename = f"{safe_filename}_pdfs.zip"
            zip_path = os.path.join(OUTPUT_DIR, zip_filename)
            
            print(f"📦 개별 PDF → ZIP 생성 시작")
            
            individual_pdfs = []  # 생성된 개별 PDF 파일들 추적
            
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, temp_file in enumerate(temp_files):
                        try:
                            # 원본 파일명 가져오기 (안전하게)
                            if i < len(files):
                                original_name = files[i].filename
                            else:
                                original_name = f"image_{i+1}.jpg"
                                
                            # 안전한 파일명 생성
                            base_name = os.path.splitext(original_name)[0]
                            safe_base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
                            if not safe_base_name:
                                safe_base_name = f"image_{i+1}"
                                
                            pdf_name = f"{safe_base_name}.pdf"
                            individual_pdf_path = os.path.join(OUTPUT_DIR, f"temp_{uuid4()}.pdf")
                            
                            print(f"   📄 개별 PDF 생성 중: {pdf_name}")
                            
                            # 단일 이미지로 PDF 생성
                            create_pdf_from_images([temp_file], individual_pdf_path, quality)
                            
                            # 파일 존재 확인
                            if not os.path.exists(individual_pdf_path):
                                print(f"   ❌ PDF 생성 실패: {pdf_name}")
                                continue
                                
                            # ZIP에 추가
                            zip_file.write(individual_pdf_path, pdf_name)
                            individual_pdfs.append(individual_pdf_path)
                            
                            print(f"   ✅ PDF 추가 완료: {pdf_name}")
                            
                        except Exception as pdf_error:
                            print(f"   ❌ 개별 PDF 생성 오류 ({i+1}): {str(pdf_error)}")
                            continue
                
                # 생성된 PDF가 있는지 확인
                if not individual_pdfs:
                    raise Exception("생성된 PDF 파일이 없습니다.")
                    
                print(f"📦 ZIP 파일 생성 완료: {zip_filename} ({len(individual_pdfs)}개 PDF)")
                
                # 개별 PDF 파일들을 output_paths에 추가
                output_paths.extend(individual_pdfs)
                
                # 임시 파일 정리
                cleanup_files(temp_files + individual_pdfs)
                
                # ZIP 파일 다운로드 URL 반환
                return JSONResponse({
                    "message": f"개별 PDF 변환 완료 ({len(individual_pdfs)}개)",
                    "file_count": len(individual_pdfs),
                    "download_url": f"/download/{zip_filename}",
                    "filename": zip_filename
                })
                
            except Exception as zip_error:
                # ZIP 생성 실패 시 개별 PDF 파일들 정리
                for pdf_path in individual_pdfs:
                    try:
                        if os.path.exists(pdf_path):
                            os.remove(pdf_path)
                    except:
                        pass
                raise Exception(f"ZIP 파일 생성 실패: {str(zip_error)}")
        
        else:
            print(f"   📄 합본 PDF 모드 실행")
            # 합본 PDF 생성 (기본값)
            pdf_filename = f"{safe_filename}.pdf"
            pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
            
            # 모든 이미지를 하나의 PDF로 변환
            create_pdf_from_images(temp_files, pdf_path, quality)
            output_paths.append(pdf_path)
            
            print(f"📄 합본 PDF 생성 완료: {pdf_filename}")
            
            # PDF 파일 직접 반환
            def cleanup_task():
                cleanup_files(temp_files + output_paths)
                
            return FileResponse(
                path=pdf_path,
                filename=pdf_filename,
                media_type='application/pdf',
                background=BackgroundTask(cleanup_task)
            )
    
    except Exception as e:
        print(f"❌ 변환 오류: {str(e)}")
        # 오류 시 임시 파일 정리
        cleanup_files(temp_files + output_paths)
        raise HTTPException(status_code=500, detail=f"PDF 변환 중 오류가 발생했습니다: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """ZIP 파일 다운로드 엔드포인트"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    def cleanup_task():
        cleanup_files([file_path])
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/zip',
        background=BackgroundTask(cleanup_task)
    )


@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "features": ["merged_pdf", "individual_pdf", "zip_download"],
        "upload_dir": UPLOAD_DIR,
        "output_dir": OUTPUT_DIR
    }


if __name__ == "__main__":
    print("\n🌟 서버 실행:")
    print("   메인: http://localhost:8000")
    print("   API 문서: http://localhost:8000/docs")
    print("   상태 확인: http://localhost:8000/health")
    print("\n⚙️  기능:")
    print("   ✅ 합본 PDF")
    print("   ✅ 개별 PDF (ZIP)")
    print("   ✅ 품질 조절")
    print("   ✅ 파일명 커스터마이징")
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)