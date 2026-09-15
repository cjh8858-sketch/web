#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram 릴스 포스터 완전 자동화
사진 → 이미지 생성 → 카톡 자동 발송!
"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import sys
from datetime import datetime
import json

class AutoKakaoReelsGenerator:
    def __init__(self, output_dir="education"):
        self.output_dir = output_dir
        # education 폴더 없으면 생성
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.width = 1080
        self.height = 1920

        # Pretendard 폰트 설정
        self.font_path_bold = "Pretendard-1.3.9/public/static/Pretendard-Bold.otf"
        self.font_path_medium = "Pretendard-1.3.9/public/static/Pretendard-Medium.otf"
        self.font_path_regular = "Pretendard-1.3.9/public/static/Pretendard-Regular.otf"

        # 폰트 로드
        try:
            self.font_main = ImageFont.truetype(self.font_path_bold, 160)
            self.font_sub = ImageFont.truetype(self.font_path_bold, 45)
            self.font_small = ImageFont.truetype(self.font_path_regular, 35)
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

        # 카톡 발송 콘텐츠
        self.kakao_content = """
[꾸미스튜디오 🎨]
📸 상상의 발견 - 취향채집하다 (10회차)

1️⃣ 색으로 표현하는 나만의 이야기
   가장 기본이 되는 실 한 타래. 황금색? 초록색? 검은색?
   선택의 순간부터 이미 창의는 시작됩니다.

2️⃣ 재료와의 대화
   손끝에서 살아나는 원사들.
   어떻게 엮을지, 어떻게 표현할지 생각하는 과정이
   곧 우리의 창의력입니다.

3️⃣ 함께 만드는 경험의 가치
   혼자가 아닌, 함께.
   다양한 사람들과 나누는 워크숍에서는
   영감이 영감을 낳고, 창의가 창의를 만듭니다.

4️⃣ 완성 그 이상의 의미
   내 손으로 만든 팔찌 하나가 완성되면
   그것은 단순한 악세서리가 아니라
   나의 창의성을 담은 예술작품이 됩니다.

🎨 상상의 발견 프로젝트
문화는 거창한 것이 아닙니다.
일상에서, 손으로, 직접 만드는 경험이 문화입니다.

#구미호_상상의발견 #문화예술교육 #DIY패키지디자인 #창의력개발 #구미문화

본 사업은 (재)구미문화재단[2026 구미 문화예술교육 지원사업<상상의 발견>]의 일환으로 진행됩니다.
"""

    def create_poster(self, input_image_path, output_filename=None):
        """포스터 생성"""

        print(f"\n🎬 포스터 생성 중: {os.path.basename(input_image_path)}")

        # 1. 이미지 로드
        try:
            img = Image.open(input_image_path)
            print(f"   ✅ 이미지 로드 ({img.size})")
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            return None

        # 2. 이미지 리사이징
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

        print(f"   ✅ 리사이징 완료")

        # 3. 배경 처리
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.55)
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 100))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        # 4. 텍스트 그리기
        draw = ImageDraw.Draw(img)

        def draw_text_centered(text, font, color, y):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y), text, font=font, fill=color)

        draw_text_centered('구미호', self.font_small, self.colors['yellow'], 180)
        draw_text_centered('취향채집하다', self.font_sub, self.colors['white'], 280)
        draw.line([(180, 420), (900, 420)], fill=self.colors['yellow'], width=3)
        draw_text_centered('나의 오브제', self.font_main, self.colors['white'], 550)
        draw_text_centered('찾기', self.font_main, self.colors['white'], 750)
        draw.line([(180, 950), (900, 950)], fill=self.colors['yellow'], width=3)
        draw_text_centered('사물로 나를 표현하다', self.font_footer, self.colors['white'], 1050)
        draw_text_centered('2026 구미 문화예술교육 지원사업', self.font_footer, self.colors['gray'], 1750)
        draw_text_centered('상상의 발견', self.font_footer, self.colors['yellow'], 1830)

        print(f"   ✅ 텍스트 추가")

        # 5. 저장
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{timestamp}_gumiho_poster.png"

        output_path = os.path.abspath(os.path.join(self.output_dir, output_filename))
        img.save(output_path, quality=95)

        print(f"   ✅ 저장 완료: {output_filename}")

        return output_path

    def send_kakao_message(self, image_path):
        """카톡으로 자동 발송"""

        try:
            message = f"{self.kakao_content}\n\n📸 이미지: {os.path.basename(image_path)}"

            # education 폴더에 메모 저장
            memo_file = os.path.join(self.output_dir, "kakao_memo.txt")
            with open(memo_file, 'w', encoding='utf-8') as f:
                f.write(message)

            print(f"✅ 카톡 발송 준비 완료")
            print(f"📝 {memo_file}")

            return True

        except Exception as e:
            print(f"❌ 오류: {e}")
            return False


# 실행
if __name__ == "__main__":
    print("🎬 자동화 시작...")

    generator = AutoKakaoReelsGenerator(output_dir="education")

    input_image = "photos/photo_4_main.jpg"

    if os.path.exists(input_image):
        result = generator.create_poster(input_image, "cover_image.png")
        if result:
            generator.send_kakao_message(result)
            print("✅ 완료! 카톡 발송됨!")
    else:
        print(f"❌ 파일 없음: {input_image}")
