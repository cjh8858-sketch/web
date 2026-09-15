#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram 릴스 커버 이미지 자동 생성
프로그램: 상상의 발견 × 취향채집하다
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os
from datetime import datetime

class ReelsCoverGenerator:
    def __init__(self, output_dir="."):
        self.output_dir = output_dir
        self.width = 1080
        self.height = 1920

        # 컬러 정의 (프로그램 색상)
        self.colors = {
            'black': (26, 26, 26),
            'white': (255, 255, 255),
            'dark_overlay': (0, 0, 0, 180),  # 반투명 검은색
            'blue': (70, 130, 180),
            'yellow': (255, 193, 7),
            'pink': (219, 112, 147),
            'green': (45, 93, 78),
        }

        # 폰트 경로 설정
        self.font_paths = self._setup_fonts()

    def _setup_fonts(self):
        """시스템에서 폰트 찾기"""
        possible_paths = [
            "C:\\Windows\\Fonts\\NotoSansCJKkr-Bold.otf",
            "C:\\Windows\\Fonts\\NotoSans-Bold.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJKkr-Bold.otf",
        ]

        fonts = {}
        for path in possible_paths:
            if os.path.exists(path):
                fonts['title'] = path
                fonts['subtitle'] = path
                fonts['body'] = path
                return fonts

        # 기본값 (시스템 폰트)
        return {
            'title': 'arial.ttf',
            'subtitle': 'arial.ttf',
            'body': 'arial.ttf',
        }

    def create_cover(self, input_image_path, output_filename=None):
        """
        릴스 커버 이미지 생성

        Args:
            input_image_path (str): 입력 사진 경로
            output_filename (str): 출력 파일명 (기본값: 날짜_relels_cover.png)

        Returns:
            str: 생성된 파일 경로
        """

        # 1. 입력 이미지 로드
        try:
            img = Image.open(input_image_path)
            print(f"✅ 이미지 로드 완료: {input_image_path}")
        except Exception as e:
            print(f"❌ 이미지 로드 실패: {e}")
            return None

        # 2. 이미지 리사이징 (1080x1920)
        img = self._resize_image(img)

        # 3. 배경 어둡게 처리
        img = self._darken_image(img)

        # 4. 투명한 오버레이 추가
        overlay = Image.new('RGBA', (self.width, self.height), self.colors['dark_overlay'])
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        # 5. 텍스트 오버레이 추가
        draw = ImageDraw.Draw(img)
        self._add_text_overlays(draw)

        # 6. 파일 저장
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{timestamp}_gumiho_relels_cover.png"

        output_path = os.path.join(self.output_dir, output_filename)
        img.save(output_path, quality=95)
        print(f"✅ 이미지 저장 완료: {output_path}")

        return output_path

    def _resize_image(self, img):
        """이미지를 1080x1920으로 리사이징"""
        aspect_ratio = img.width / img.height
        target_ratio = self.width / self.height

        if aspect_ratio > target_ratio:
            # 너비가 더 크면 높이 기준으로 스케일
            new_height = self.height
            new_width = int(new_height * aspect_ratio)
        else:
            # 높이가 더 크면 너비 기준으로 스케일
            new_width = self.width
            new_height = int(new_width / aspect_ratio)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 중앙 기준으로 크롭
        left = (new_width - self.width) // 2
        top = (new_height - self.height) // 2
        right = left + self.width
        bottom = top + self.height

        img = img.crop((left, top, right, bottom))
        return img

    def _darken_image(self, img):
        """이미지를 약간 어둡게 처리"""
        img_array = img.convert('RGB')
        dark_img = Image.new('RGB', img_array.size)
        dark_img.paste(img_array, (0, 0))

        # 밝기 감소 (0.6배)
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(dark_img)
        return enhancer.enhance(0.7)

    def _add_text_overlays(self, draw):
        """텍스트 오버레이 추가"""
        try:
            # 폰트 로드
            title_font = self._load_font('title', 80)
            subtitle_font = self._load_font('subtitle', 60)
            body_font = self._load_font('body', 40)
        except:
            print("⚠️  폰트 로드 실패, 기본 폰트 사용")
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            body_font = ImageFont.load_default()

        # 텍스트 배치
        texts = [
            {
                'text': '구미호',
                'font': body_font,
                'color': self.colors['yellow'],
                'y': 200,
                'size': 'small'
            },
            {
                'text': '취향채집하다',
                'font': title_font,
                'color': self.colors['white'],
                'y': 320,
                'size': 'large'
            },
            {
                'text': '나의 오브제 찾기',
                'font': subtitle_font,
                'color': self.colors['white'],
                'y': 520,
                'size': 'medium'
            },
        ]

        # 각 텍스트 그리기
        for text_obj in texts:
            self._draw_text_centered(
                draw,
                text_obj['text'],
                text_obj['font'],
                text_obj['color'],
                text_obj['y']
            )

        # 하단 필수 문구 (작은 글씨)
        footer_text = "2026 구미 문화예술교육 지원사업"
        try:
            footer_font = self._load_font('body', 32)
        except:
            footer_font = ImageFont.load_default()

        self._draw_text_centered(
            draw,
            footer_text,
            footer_font,
            (200, 200, 200),  # 연한 회색
            self.height - 150
        )

    def _draw_text_centered(self, draw, text, font, color, y_position):
        """중앙 정렬 텍스트 그리기"""
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
        except:
            text_width = len(text) * 20  # 기본값

        x_position = (self.width - text_width) // 2

        draw.text(
            (x_position, y_position),
            text,
            font=font,
            fill=color,
            anchor="lt"
        )

    def _load_font(self, font_type, size):
        """폰트 로드"""
        font_path = self.font_paths.get(font_type, 'arial.ttf')
        try:
            return ImageFont.truetype(font_path, size)
        except:
            return ImageFont.load_default()

    def process_batch(self, input_folder):
        """
        폴더 내 모든 이미지 처리

        Args:
            input_folder (str): 입력 이미지 폴더 경로
        """
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}

        files = [
            f for f in os.listdir(input_folder)
            if os.path.splitext(f)[1].lower() in supported_formats
        ]

        print(f"🔍 발견된 이미지: {len(files)}개\n")

        for filename in files:
            input_path = os.path.join(input_folder, filename)
            output_filename = f"{os.path.splitext(filename)[0]}_reels_cover.png"

            print(f"📸 처리 중: {filename}")
            self.create_cover(input_path, output_filename)
            print()


# 실행
if __name__ == "__main__":
    generator = ReelsCoverGenerator(output_dir=".")

    print("=" * 60)
    print("🎬 Instagram 릴스 커버 이미지 자동 생성")
    print("=" * 60 + "\n")

    # 사용 예시
    # 단일 이미지 처리
    input_image = "photo_4.jpg"  # 사진 4 파일명

    if os.path.exists(input_image):
        result = generator.create_cover(input_image, "20260915_gumiho_reels_cover.png")
        if result:
            print(f"\n✅ 완료! 파일: {result}")
    else:
        print(f"❌ 파일을 찾을 수 없습니다: {input_image}")
        print("\n💡 사용 방법:")
        print("1. create_cover('입력_이미지.jpg') - 단일 이미지 처리")
        print("2. process_batch('폴더_경로') - 배치 처리")
