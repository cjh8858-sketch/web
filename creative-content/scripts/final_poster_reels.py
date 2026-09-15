#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram 릴스 포스터 최종 버전
Pretendard 폰트 + 개선된 레이아웃
주제(나의 오브제 찾기)를 메인으로!
"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import sys
from datetime import datetime

class FinalPosterGenerator:
    def __init__(self, output_dir="."):
        self.output_dir = output_dir
        self.width = 1080
        self.height = 1920

        # Pretendard 폰트 설정
        self.font_path_bold = "Pretendard-1.3.9/public/static/Pretendard-Bold.otf"
        self.font_path_medium = "Pretendard-1.3.9/public/static/Pretendard-Medium.otf"
        self.font_path_regular = "Pretendard-1.3.9/public/static/Pretendard-Regular.otf"

        # 폰트 로드
        try:
            # 메인 타이틀 (나의 오브제 찾기)
            self.font_main = ImageFont.truetype(self.font_path_bold, 160)

            # 서브 정보
            self.font_sub = ImageFont.truetype(self.font_path_bold, 45)

            # 작은 텍스트
            self.font_small = ImageFont.truetype(self.font_path_regular, 35)

            # 하단 텍스트
            self.font_footer = ImageFont.truetype(self.font_path_medium, 40)

            print(f"✅ Pretendard 폰트 로드 성공")
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
        최종 포스터 생성
        """

        print(f"\n🎬 포스터 생성 중: {os.path.basename(input_image_path)}")

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

        # 4. 반투명 오버레이
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 100))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        print(f"   ✅ 배경 처리 완료")

        # 5. 텍스트 그리기
        draw = ImageDraw.Draw(img)

        def draw_text_centered(text, font, color, y):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y), text, font=font, fill=color)

        # ===== 레이아웃 (개선된 버전) =====

        # 상단 작은 텍스트: "구미호"
        draw_text_centered('구미호', self.font_small, self.colors['yellow'], 180)

        # 중간 작은 텍스트: "취향채집하다"
        draw_text_centered('취향채집하다', self.font_sub, self.colors['white'], 280)

        # 구분선
        draw.line([(180, 420), (900, 420)], fill=self.colors['yellow'], width=3)

        # ===== 메인 타이틀 (큼!) =====
        draw_text_centered('나의 오브제', self.font_main, self.colors['white'], 550)
        draw_text_centered('찾기', self.font_main, self.colors['white'], 750)

        # 구분선
        draw.line([(180, 950), (900, 950)], fill=self.colors['yellow'], width=3)

        # 부연 설명
        draw_text_centered('사물로 나를 표현하다', self.font_footer, self.colors['white'], 1050)

        # 하단 정보
        draw_text_centered('2026 구미 문화예술교육 지원사업', self.font_footer, self.colors['gray'], 1750)
        draw_text_centered('상상의 발견', self.font_footer, self.colors['yellow'], 1830)

        print(f"   ✅ 텍스트 추가 완료")

        # 6. 저장
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{timestamp}_final_poster.png"

        output_path = os.path.join(self.output_dir, output_filename)
        img.save(output_path, quality=95)

        file_size = os.path.getsize(output_path) / (1024*1024)
        print(f"   ✅ 저장 완료: {output_filename} ({file_size:.2f}MB)")

        return output_path


# 실행
if __name__ == "__main__":
    print("="*60)
    print("🎬 Instagram 릴스 포스터 최종 버전")
    print("Pretendard 폰트 + 개선된 레이아웃")
    print("="*60)

    generator = FinalPosterGenerator(output_dir=".")

    input_image = "photo_4_main.jpg"

    if os.path.exists(input_image):
        result = generator.create_poster(input_image, "20260915_gumiho_final.png")
        if result:
            print(f"\n✅ 최종 완료!")
            print(f"📸 파일: {result}")
    else:
        print(f"❌ 파일 없음: {input_image}")
