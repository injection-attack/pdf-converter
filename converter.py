#!/usr/bin/env python3
"""
이미지를 PDF로 변환하는 프로그램
지원 형식: JPG, PNG, BMP, TIFF, GIF, WebP
"""

import os
import sys
from PIL import Image
from pathlib import Path
import argparse
from typing import List, Optional


class ImageToPDFConverter:
    """이미지를 PDF로 변환하는 클래스"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    
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
                print(f"📷 처리 중 ({i}/{len(image_paths)}): {os.path.basename(img_path)}")
                
                if not os.path.exists(img_path):
                    print(f"⚠️  파일을 찾을 수 없습니다: {img_path}")
                    continue
                
                processed_img = self._process_image(img_path)
                if processed_img:
                    processed_images.append(processed_img)
            
            if not processed_images:
                print("❌ 유효한 이미지 파일이 없습니다.")
                return False
            
            return self._save_as_pdf(processed_images, output_path)
            
        except Exception as e:
            print(f"❌ 변환 중 오류 발생: {e}")
            return False
    
    def _process_image(self, img_path: str) -> Optional[Image.Image]:
        """이미지를 PDF 변환에 적합하게 처리"""
        try:
            img = Image.open(img_path)
            
            # RGBA나 P 모드를 RGB로 변환
            if img.mode in ('RGBA', 'P'):
                # 투명한 배경을 흰색으로 변환
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            return img
            
        except Exception as e:
            print(f"⚠️  이미지 처리 실패 {img_path}: {e}")
            return None
    
    def _save_as_pdf(self, images: List[Image.Image], output_path: str) -> bool:
        """이미지들을 PDF로 저장"""
        try:
            # 출력 디렉토리 생성
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"📁 디렉토리 생성: {output_dir}")
            
            # PDF 저장
            first_image = images[0]
            other_images = images[1:] if len(images) > 1 else None
            
            save_kwargs = {
                "format": "PDF",
                "resolution": 100.0,
                "quality": self.quality,
                "optimize": True
            }
            
            if other_images:
                save_kwargs["save_all"] = True
                save_kwargs["append_images"] = other_images
            
            first_image.save(output_path, **save_kwargs)
            
            # 파일 크기 확인
            file_size = os.path.getsize(output_path)
            size_mb = file_size / (1024 * 1024)
            
            print(f"✅ PDF 변환 완료!")
            print(f"   📄 파일: {output_path}")
            print(f"   📊 이미지 수: {len(images)}개")
            print(f"   📏 파일 크기: {size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ PDF 저장 실패: {e}")
            return False


class ImageFinder:
    """이미지 파일을 찾는 클래스"""
    
    @staticmethod
    def find_images_in_folder(folder_path: str, recursive: bool = False) -> List[str]:
        """
        폴더에서 이미지 파일들을 찾아 반환
        
        Args:
            folder_path: 폴더 경로
            recursive: 하위 폴더까지 검색할지 여부
            
        Returns:
            이미지 파일 경로 리스트 (이름순 정렬)
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            print(f"❌ 폴더를 찾을 수 없습니다: {folder_path}")
            return []
        
        image_files = []
        pattern = "**/*" if recursive else "*"
        
        for file in folder.glob(pattern):
            if file.is_file() and file.suffix.lower() in ImageToPDFConverter.SUPPORTED_FORMATS:
                image_files.append(str(file))
        
        return sorted(image_files)
    
    @staticmethod
    def validate_image_files(file_paths: List[str]) -> List[str]:
        """이미지 파일 경로 유효성 검증"""
        valid_files = []
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                ext = Path(file_path).suffix.lower()
                if ext in ImageToPDFConverter.SUPPORTED_FORMATS:
                    valid_files.append(file_path)
                else:
                    print(f"⚠️  지원하지 않는 형식: {file_path}")
            else:
                print(f"⚠️  파일을 찾을 수 없음: {file_path}")
        
        return valid_files


def interactive_mode():
    """대화형 모드로 프로그램 실행"""
    print("🖼️  === 이미지를 PDF로 변환 ===\n")
    
    # 모드 선택
    print("변환 모드를 선택하세요:")
    print("1. 개별 파일 지정")
    print("2. 폴더 내 모든 이미지")
    print("3. 폴더 내 모든 이미지 (하위 폴더 포함)")
    
    while True:
        mode = input("\n선택 (1/2/3): ").strip()
        if mode in ['1', '2', '3']:
            break
        print("❌ 1, 2, 3 중에서 선택해주세요.")
    
    # 이미지 파일 수집
    if mode == '1':
        files_input = input("\n이미지 파일들을 입력하세요 (공백으로 구분): ").strip()
        if not files_input:
            print("❌ 파일이 입력되지 않았습니다.")
            return
        image_paths = ImageFinder.validate_image_files(files_input.split())
    else:
        folder_path = input("\n이미지가 있는 폴더 경로를 입력하세요: ").strip()
        if not folder_path:
            print("❌ 폴더 경로가 입력되지 않았습니다.")
            return
        
        recursive = (mode == '3')
        image_paths = ImageFinder.find_images_in_folder(folder_path, recursive)
    
    if not image_paths:
        print("❌ 변환할 이미지 파일이 없습니다.")
        return
    
    # 출력 설정
    output_path = input(f"\n출력 PDF 파일명 (기본값: output.pdf): ").strip()
    if not output_path:
        output_path = "output.pdf"
    
    if not output_path.endswith('.pdf'):
        output_path += '.pdf'
    
    # 품질 설정
    quality_input = input("이미지 품질 1-100 (기본값: 95): ").strip()
    try:
        quality = int(quality_input) if quality_input else 95
        quality = max(1, min(100, quality))
    except ValueError:
        quality = 95
    
    # 파일 목록 표시
    print(f"\n📋 변환할 이미지 ({len(image_paths)}개):")
    for i, img_path in enumerate(image_paths, 1):
        print(f"   {i:2d}. {os.path.basename(img_path)}")
    
    print(f"\n⚙️  설정:")
    print(f"   📄 출력: {output_path}")
    print(f"   🎛️  품질: {quality}")
    
    # 변환 실행
    confirm = input("\n변환을 시작하시겠습니까? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ 변환이 취소되었습니다.")
        return
    
    print(f"\n🚀 변환을 시작합니다...")
    converter = ImageToPDFConverter(quality)
    success = converter.convert_images_to_pdf(image_paths, output_path)
    
    if success:
        print("\n🎉 변환이 성공적으로 완료되었습니다!")
    else:
        print("\n💥 변환 중 오류가 발생했습니다.")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='이미지 파일들을 PDF로 변환',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s image1.jpg image2.png -o result.pdf
  %(prog)s /path/to/images --folder -o combined.pdf
  %(prog)s /path/to/images --folder --recursive -q 80
  %(prog)s  (대화형 모드)
        """
    )
    
    parser.add_argument('input', nargs='*', help='입력 이미지 파일들 또는 폴더')
    parser.add_argument('-o', '--output', default='output.pdf', help='출력 PDF 파일명')
    parser.add_argument('-q', '--quality', type=int, default=95, help='이미지 품질 1-100')
    parser.add_argument('--folder', action='store_true', help='입력을 폴더로 처리')
    parser.add_argument('--recursive', action='store_true', help='하위 폴더까지 검색 (--folder와 함께 사용)')
    
    args = parser.parse_args()
    
    # 대화형 모드
    if not args.input:
        interactive_mode()
        return
    
    # 명령행 모드
    image_paths = []
    
    if args.folder:
        for folder_path in args.input:
            folder_images = ImageFinder.find_images_in_folder(folder_path, args.recursive)
            image_paths.extend(folder_images)
    else:
        image_paths = ImageFinder.validate_image_files(args.input)
    
    if not image_paths:
        print("❌ 변환할 이미지 파일이 없습니다.")
        return
    
    print(f"📋 찾은 이미지 파일: {len(image_paths)}개")
    
    converter = ImageToPDFConverter(args.quality)
    success = converter.convert_images_to_pdf(image_paths, args.output)
    
    if success:
        print("\n🎉 변환이 성공적으로 완료되었습니다!")
    else:
        print("\n💥 변환 중 오류가 발생했습니다.")


if __name__ == "__main__":
    main()