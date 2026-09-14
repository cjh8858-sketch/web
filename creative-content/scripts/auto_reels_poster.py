#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram 릴스 포스터 자동 생성 (한글 지원)
실제 교육 사진 위에 한글 텍스트 자동 오버레이
"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import sys
from datetime import datetime

class ReelsPosterGenerator:
    def __init__(self, output_dir="."):
        self.output_dir = output_dir
        self.width = 1080
        self.height = 1920

        # 한글 폰트 설정
        self.font_path = "C:\\Windows\\Fonts\\NotoSansKR-VF.ttf"

        if not os.path.exists(self.font_path):
            print(f"❌ 폰트 파일 없음: {self.font_path}")
            sys.exit(1)

        try:
            self.font_xl = ImageFont.truetype(self.font_path, 140)
            self.font_lg = ImageFont.truetype(self.font_path, 90)
            self.font_md = ImageFont.truetype(self.font_path, 50)
            print(f"✅ 한글 폰트 로드 성공: NotoSansKR")
        except Exception as e:
            print(f"❌ 폰트 로드 실패: {e}")
            sys.exit(1)

        # 색상
        self.colors = {
            'yellow': (255, 193, 7),
            'white': (255, 255, 255),
            'gray': (200, 200, 200),
        }

    def create_poster(self, input_image_path, output_filename=None):
        """
        릴스 포스터 생성

        Args:
            input_image_path (str): 입력 사진 경로
            output_filename (str): 출력 파일명

        Returns:
            str: 생성된 파일 경로
        """

        print(f"\n🎬 포스터 생성 중: {input_image_path}")

        # 1. 이미지 로드
        try:
            img = Image.open(input_image_path)
            print(f"   ✅ 이미지 로드 ({img.size})")
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            return None

        # 2. 이미지 리사이징 (1080x1920)
        aspect_ratio = img.width / img.height
        target_ratio = self.width / self.height

        if aspect_ratio > target_ratio:
            new_height = self.height
            new_width = int(new_height * aspect_ratio)
        else:
            new_width = self.width
            new_height = int(new_width / aspect_ratio)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        left = (new_width - self.width) // 2
        top = (new_height - self.height) // 2
        img = img.crop((left, top, left + self.width, top + self.height))

        print(f"   ✅ 리사이징 완료 ({self.width}x{self.height})")

        # 3. 배경 어둡게 처리
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.55)
        print(f"   ✅ 배경 어둡게 처리")

        # 4. 반투명 오버레이
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 100))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        print(f"   ✅ 오버레이 추가")

        # 5. 텍스트 그리기
        draw = ImageDraw.Draw(img)

        def draw_text_centered(text, font, color, y):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y), text, font=font, fill=color)

        # 텍스트 추가
        draw_text_centered('구미호', self.font_md, self.colors['yellow'], 200)
        draw_text_centered('취향', self.font_xl, self.colors['white'], 350)
        draw_text_centered('채집', self.font_xl, self.colors['white'], 520)
        draw_text_centered('하다', self.font_xl, self.colors['white'], 690)

        # 구분선
        draw.line([(240, 900), (840, 900)], fill=self.colors['yellow'], width=3)

        # 서브타이틀
        draw_text_centered('나의 오브제 찾기', self.font_lg, self.colors['yellow'], 1000)
        draw_text_centered('사물로 나를 표현하다', self.font_md, self.colors['white'], 1150)

        # 하단 정보
        draw_text_centered('2026 구미 문화예술교육 지원사업', self.font_md, self.colors['gray'], 1750)
        draw_text_centered('상상의 발견', self.font_md, self.colors['yellow'], 1830)

        print(f"   ✅ 텍스트 추가")

        # 6. 저장
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{timestamp}_gumiho_poster_reels.png"

        output_path = os.path.join(self.output_dir, output_filename)
        img.save(output_path, quality=95)

        file_size = os.path.getsize(output_path) / (1024*1024)
        print(f"   ✅ 저장 완료: {output_filename} ({file_size:.2f}MB)")

        return output_path

    def process_batch(self, input_folder):
        """
        폴더 내 모든 이미지 처리

        Args:
            input_folder (str): 입력 폴더 경로
        """
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}

        files = [
            f for f in os.listdir(input_folder)
            if os.path.splitext(f)[1].lower() in supported_formats
        ]

        print(f"\n{'='*60}")
        print(f"🎬 Instagram 릴스 포스터 자동 생성")
        print(f"{'='*60}")
        print(f"📸 발견된 이미지: {len(files)}개\n")

        for filename in files:
            input_path = os.path.join(input_folder, filename)
            output_filename = f"{os.path.splitext(filename)[0]}_poster.png"
            self.create_poster(input_path, output_filename)

        print(f"\n{'='*60}")
        print(f"✅ 모든 이미지 처리 완료!")
        print(f"{'='*60}")


# 실행
if __name__ == "__main__":
    generator = ReelsPosterGenerator(output_dir=".")

    # 단일 이미지 처리
    input_image = "photo_4_main.jpg"

    if os.path.exists(input_image):
        result = generator.create_poster(input_image, "20260915_gumiho_poster_final.png")
        if result:
            print(f"\n✅ 최종 결과: {result}")
    else:
        print(f"❌ 파일 없음: {input_image}")
        print(f"\n💡 사용 방법:")
        print(f"   generator = ReelsPosterGenerator()")
        print(f"   generator.create_poster('이미지.jpg')")
        print(f"   generator.process_batch('폴더_경로')  # 배치 처리")
