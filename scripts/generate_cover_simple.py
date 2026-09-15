#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os

# 설정
input_file = "photo_4_main.jpg"
output_file = "20260915_gumiho_reels_cover.png"
width, height = 1080, 1920

print("🎬 Instagram 릴스 커버 생성 중...\n")

# 1. 이미지 로드
try:
    img = Image.open(input_file)
    print(f"✅ 이미지 로드: {input_file} ({img.size})")
except Exception as e:
    print(f"❌ 실패: {e}")
    exit()

# 2. 이미지 리사이징
aspect_ratio = img.width / img.height
target_ratio = width / height

if aspect_ratio > target_ratio:
    new_height = height
    new_width = int(new_height * aspect_ratio)
else:
    new_width = width
    new_height = int(new_width / aspect_ratio)

img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
left = (new_width - width) // 2
top = (new_height - height) // 2
img = img.crop((left, top, left + width, top + height))

print(f"✅ 리사이징 완료: {img.size}")

# 3. 배경 어둡게 처리
enhancer = ImageEnhance.Brightness(img)
img = enhancer.enhance(0.65)
print("✅ 배경 어둡게 처리 완료")

# 4. 반투명 오버레이 추가
overlay = Image.new('RGBA', (width, height), (0, 0, 0, 160))
img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
print("✅ 오버레이 추가 완료")

# 5. 텍스트 추가
draw = ImageDraw.Draw(img)

# 폰트 설정
font_paths = [
    "C:\\Windows\\Fonts\\NotoSansCJKkr-Bold.otf",
    "C:\\Windows\\Fonts\\arial.ttf",
]

font_title = None
for path in font_paths:
    if os.path.exists(path):
        try:
            font_title = ImageFont.truetype(path, 100)
            font_subtitle = ImageFont.truetype(path, 70)
            font_body = ImageFont.truetype(path, 45)
            print(f"✅ 폰트 로드: {os.path.basename(path)}")
            break
        except:
            pass

if not font_title:
    font_title = ImageFont.load_default()
    font_subtitle = ImageFont.load_default()
    font_body = ImageFont.load_default()
    print("⚠️  기본 폰트 사용")

# 텍스트 그리기 함수
def draw_text_centered(text, font, color, y):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    draw.text((x, y), text, font=font, fill=color)

# 색상
colors = {
    'yellow': (255, 193, 7),
    'white': (255, 255, 255),
    'gray': (180, 180, 180),
}

# 텍스트 추가
draw_text_centered('구미호', font_body, colors['yellow'], 180)
draw_text_centered('취향채집하다', font_title, colors['white'], 320)
draw_text_centered('나의 오브제 찾기', font_subtitle, colors['white'], 540)
draw_text_centered('2026 구미 문화예술교육 지원사업', font_body, colors['gray'], height - 160)

print("✅ 텍스트 추가 완료")

# 6. 저장
img.save(output_file, quality=95)
print(f"\n✅ 완료! 파일 저장: {output_file}")

file_size = os.path.getsize(output_file) / (1024*1024)
print(f"📊 파일 크기: {file_size:.2f} MB")
