#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram 릴스 포스터 스타일
실제 사진 위에 텍스트 오버레이
"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os

# 설정
input_file = "photo_4_main.jpg"
output_file = "20260915_gumiho_poster_reels.png"
width, height = 1080, 1920

print("🎬 포스터 스타일 릴스 커버 생성 중...\n")

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
img_dark = enhancer.enhance(0.55)
print("✅ 배경 어둡게 처리 완료")

# 4. 반투명 검은색 오버레이 추가
overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
img_with_overlay = Image.alpha_composite(img_dark.convert('RGBA'), overlay).convert('RGB')
print("✅ 오버레이 추가 완료")

# 5. 텍스트 그리기 준비
draw = ImageDraw.Draw(img_with_overlay)

# 폰트 설정
font_paths = [
    "C:\\Windows\\Fonts\\NotoSansCJKkr-Bold.otf",
    "C:\\Windows\\Fonts\\arial.ttf",
]

font_xl = None
font_lg = None
font_md = None

for path in font_paths:
    if os.path.exists(path):
        try:
            font_xl = ImageFont.truetype(path, 140)
            font_lg = ImageFont.truetype(path, 90)
            font_md = ImageFont.truetype(path, 50)
            print(f"✅ 폰트 로드: {os.path.basename(path)}")
            break
        except:
            pass

if not font_xl:
    font_xl = ImageFont.load_default()
    font_lg = ImageFont.load_default()
    font_md = ImageFont.load_default()
    print("⚠️  기본 폰트 사용")

# 색상
colors = {
    'yellow': (255, 193, 7),
    'white': (255, 255, 255),
    'gray': (200, 200, 200),
}

# 텍스트 그리기 함수 (중앙 정렬)
def draw_text_centered(text, font, color, y, with_stroke=False):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2

    # 테두리 효과 (선택)
    if with_stroke:
        offset = 3
        for adj_x in range(x-offset, x+offset+1):
            for adj_y in range(y-offset, y+offset+1):
                if (adj_x, adj_y) != (x, y):
                    draw.text((adj_x, adj_y), text, font=font, fill=(0, 0, 0))

    draw.text((x, y), text, font=font, fill=color)

# 6. 텍스트 추가

# 상단 라벨 "구미호"
draw_text_centered('구미호', font_md, colors['yellow'], 200)

# 메인 타이틀 (한 글자씩 줄바꿈)
# "취향"
draw_text_centered('취향', font_xl, colors['white'], 350)

# "채집"
draw_text_centered('채집', font_xl, colors['white'], 520)

# "하다"
draw_text_centered('하다', font_xl, colors['white'], 690)

# 중간 구분
draw.line([(240, 900), (840, 900)], fill=colors['yellow'], width=3)

# 서브타이틀
draw_text_centered('나의 오브제 찾기', font_lg, colors['yellow'], 1000)

# 부연 설명
draw_text_centered('사물로 나를 표현하다', font_md, colors['white'], 1150)

# 하단 정보
draw_text_centered('2026 구미 문화예술교육 지원사업', font_md, colors['gray'], 1750)
draw_text_centered('상상의 발견', font_md, colors['yellow'], 1830)

print("✅ 텍스트 추가 완료")

# 7. 저장
img_with_overlay.save(output_file, quality=95)
print(f"\n✅ 완료! 파일 저장: {output_file}")

file_size = os.path.getsize(output_file) / (1024*1024)
print(f"📊 파일 크기: {file_size:.2f} MB")
print(f"📐 크기: {width}x{height}px (릴스 규격)")
