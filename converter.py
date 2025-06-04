#!/usr/bin/env python3
"""
이미지를 PDF로 변환하는 모듈 (웹서비스용)
"""

import os
from PIL import Image
from pathlib import Path
from typing import List, Optional


class ImageToPDFConverter:
    """이미지를 PDF로 변환하는 클래스 (웹서비스용)"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff'}
    
    def __init__(self, quality: int = 95):
        """
        Args:
            quality: 이미지 품질 (1-100)
        """
        self.quality = max(1, min(100, quality))
    
    def convert_images_to_pdf(self, image_paths: List[str], output_path: str) -> bool:
        """
        여러 이미지를 하나의 PDF로 변환
        
        Args:
            image_paths: 이미지 파일 경로 리스트
            output_path: 출력 PDF 파일 경로
            
        Returns:
            성공 여부
        """
        if not image_paths:
            print("❌ 변환할 이미지 파일이 없습니다.")
            return False
        
        try:
            processed_images = []
            
            for i, img_path in enumerate(image_paths, 1):
                print(f"   📷 처리 중 ({i}/{len(image_paths)}): {os.path.basename(img_path)}")
                
                if not os.path.exists(img_path):
                    print(f"   ⚠️  파일을 찾을 수 없습니다: {img_path}")
                    continue
                
                processed_img = self._process_image(img_path)
                if processed_img:
                    processed_images.append(processed_img)
            
            if not processed_images:
                print("   ❌ 유효한 이미지 파일이 없습니다.")
                return False
            
            return self._save_as_pdf(processed_images, output_path)
            
        except Exception as e:
            print(f"   ❌ 변환 중 오류 발생: {e}")
            return False
        finally:
            # 메모리 정리
            for img in processed_images:
                try:
                    img.close()
                except:
                    pass
    
    def _process_image(self, img_path: str) -> Optional[Image.Image]:
        """이미지를 PDF 변환에 적합하게 처리"""
        try:
            with Image.open(img_path) as img:
                # 이미지 복사 (원본 보호)
                img_copy = img.copy()
                
                print(f"   ✅ 이미지 로드: {img_copy.size}, {img_copy.mode}")
                
                # RGBA나 P 모드를 RGB로 변환
                if img_copy.mode in ('RGBA', 'P', 'LA'):
                    print(f"   🔄 모드 변환: {img_copy.mode} → RGB")
                    # 투명한 배경을 흰색으로 변환
                    background = Image.new('RGB', img_copy.size, (255, 255, 255))
                    if img_copy.mode == 'P':
                        img_copy = img_copy.convert('RGBA')
                    if img_copy.mode in ('RGBA', 'LA'):
                        if img_copy.mode == 'LA':
                            img_copy = img_copy.convert('RGBA')
                        background.paste(img_copy, mask=img_copy.split()[-1])
                    else:
                        background.paste(img_copy)
                    img_copy = background
                elif img_copy.mode != 'RGB':
                    print(f"   🔄 모드 변환: {img_copy.mode} → RGB")
                    img_copy = img_copy.convert('RGB')
                
                # 이미지 품질 최적화
                if self.quality < 95:
                    print(f"   🎯 품질 최적화: {self.quality}%")
                    import io
                    buffer = io.BytesIO()
                    img_copy.save(buffer, format='JPEG', quality=self.quality, optimize=True)
                    buffer.seek(0)
                    optimized_img = Image.open(buffer)
                    img_copy = optimized_img.copy()
                    optimized_img.close()
                    buffer.close()
                
                return img_copy
            
        except Exception as e:
            print(f"   ⚠️  이미지 처리 실패 {img_path}: {e}")
            return None
    
    def _save_as_pdf(self, images: List[Image.Image], output_path: str) -> bool:
        """이미지들을 PDF로 저장"""
        try:
            # 출력 디렉토리 생성
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                print(f"   📁 디렉토리 생성: {output_dir}")
            
            # PDF 저장
            first_image = images[0]
            other_images = images[1:] if len(images) > 1 else None
            
            save_kwargs = {
                "format": "PDF",
                "resolution": 150.0,  # 웹용으로 해상도 조정
                "quality": max(85, self.quality),  # PDF용 품질 보정
                "optimize": True
            }
            
            if other_images:
                save_kwargs["save_all"] = True
                save_kwargs["append_images"] = other_images
            
            first_image.save(output_path, **save_kwargs)
            
            # 파일 생성 및 크기 확인
            if not os.path.exists(output_path):
                print(f"   ❌ PDF 파일이 생성되지 않았습니다.")
                return False
                
            file_size = os.path.getsize(output_path)
            size_mb = file_size / (1024 * 1024)
            
            print(f"   ✅ PDF 변환 완료!")
            print(f"   📄 파일: {os.path.basename(output_path)}")
            print(f"   📊 이미지 수: {len(images)}개")
            print(f"   📏 파일 크기: {size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            print(f"   ❌ PDF 저장 실패: {e}")
            # 실패한 파일 제거
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            return False


# 웹서비스용 편의 함수
def create_pdf_from_images(image_paths: List[str], output_path: str, quality: int = 95) -> None:
    """
    웹서비스에서 사용할 PDF 변환 함수
    
    Args:
        image_paths: 이미지 파일 경로 리스트
        output_path: 출력 PDF 파일 경로
        quality: 이미지 품질 (1-100)
        
    Raises:
        Exception: 변환 실패 시
    """
    converter = ImageToPDFConverter(quality)
    success = converter.convert_images_to_pdf(image_paths, output_path)
    
    if not success:
        raise Exception("PDF 변환에 실패했습니다.")