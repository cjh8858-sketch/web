# 🎨 꾸미스튜디오 창의 콘텐츠 자동화 시스템
## 상상의 발견 × 나의 오브제 찾기 × 시그니처 찾기

---

## 📋 개요

이 저장소는 **매주 다른 주제로 진행되는 문화예술 교육 콘텐츠를 자동으로 생성**합니다.

```
📸 사진 + 📝 교육자료
    ↓
🤖 자동 분석 + 이미지 생성 + 글 작성
    ↓
🎨 Artifact로 배포 (다운로드 + 복사 가능)
    ↓
📱 카톡 자동 발송
```

---

## 🏗️ 폴더 구조

```
creative-content/
├── photos/              # 📸 매주 수업 사진 (INPUT)
├── education/           # 📝 교육자료 & 분석
├── outputs/             # 🎨 생성된 콘텐츠 (완성된 이미지 + 글)
├── scripts/             # 🔧 자동화 스크립트
├── archives/            # 📦 지난주 콘텐츠 백업
├── Creative_Content_Auto_PRD.md  # 📋 전체 가이드
├── README.md            # 📖 이 파일 (빠른 시작)
└── .gitignore          # 🔒 깃 무시 규칙
```

---

## 🚀 **시작 방법 (매주 반복)**

### Step 1️⃣ - 사진 준비
```bash
# 사진 폴더에 수업 사진 넣기
photos/
├── photo_1.jpg
├── photo_2.jpg
└── photo_3.jpg
```

### Step 2️⃣ - 교육자료 정보
```bash
# 교육자료 폴더에 정보 넣기
education/
├── 주제.txt          # "팔찌" 또는 "북커버" 등
├── 교육내용.txt       # 수업의 핵심 메시지
└── (선택) 교육자료.pdf
```

### Step 3️⃣ - Claude에게 보내기
**Claude 앱에서:**
1. 이 대화 열기
2. 사진 + 교육자료 정보 보내기
3. 자동으로 처리됨!

```
📸 사진 첨부
📝 주제: "팔찌 만드는 수업"
📝 핵심: "색으로 나를 표현하기"
```

### Step 4️⃣ - 결과 받기
**Artifact에서:**
- 🖼️ 이미지 다운로드
- 📝 글 복사
- 📱 카톡 확인

### Step 5️⃣ - GitHub 저장
```bash
# 자동으로 커밋됩니다
git add .
git commit -m "주간 콘텐츠: 팔찌 만드는 수업 (09/15)"
git push origin main
```

---

## 📊 파일 구조 상세

### `photos/` - 수업 사진
```
photos/
├── 2026_09_15_bracelet/
│   ├── photo_1.jpg      (전체 수업장면)
│   ├── photo_2.jpg      (참가자 작업장면)
│   └── photo_3.jpg      (완성된 팔찌)
└── 2026_09_22_bookcover/
    └── ...
```

### `education/` - 교육자료
```
education/
├── 2026_09_15_bracelet/
│   ├── 주제.txt         "팔찌 만들기"
│   ├── 핵심메시지.txt    "색으로 나를 표현한다"
│   └── (선택) 커리큘럼.pdf
└── 2026_09_22_bookcover/
    └── ...
```

### `outputs/` - 생성된 콘텐츠
```
outputs/
├── 2026_09_15_bracelet/
│   ├── cover_image.png     (생성된 포스터)
│   ├── content_text.md     (글)
│   └── kakao_message.txt   (카톡 발송용)
└── 2026_09_22_bookcover/
    └── ...
```

---

## 🎯 **매주 체크리스트**

```
[ ] 주제 결정 (팔찌? 북커버? 가방?)
[ ] 사진 촬영 (수업 장면)
[ ] 교육자료 정리 (주제/핵심메시지)
[ ] Claude 앱에서 보내기
    - 사진 첨부
    - 주제 & 교육내용 입력
[ ] Artifact에서 받기
    - 이미지 다운로드
    - 글 복사
[ ] 카톡 확인
[ ] GitHub에 커밋
    - git add .
    - git commit -m "주간 콘텐츠: [주제] (MM/DD)"
    - git push
```

---

## 📝 **Claude에게 보낼 정보 형식**

```
📸 사진: [1-3장의 수업 사진]

📋 주제: [팔찌/북커버/가방 등]

📝 교육 내용:
- 핵심 메시지: "색으로 나를 표현한다"
- 수업 목표: 자신의 취향을 색으로 표현하고 공유
- 참가자 반응: (선택) "매우 집중했고, 완성도가 높았음"
```

---

## 🛠️ **Python 스크립트 사용 (선택)**

컴퓨터에서 직접 처리하고 싶다면:

```bash
# 스크립트 디렉토리로 이동
cd scripts/

# 이미지 생성
python final_poster_reels.py

# 카톡 자동 발송
python auto_kakao_reels.py
```

---

## 📱 **결과물 예시**

### 생성되는 것

1. **이미지** (1080×1920px)
   ```
   - Pretendard 폰트
   - 실제 수업 사진을 배경으로
   - 주제 텍스트 오버레이
   - 브랜드 컬러 (노란색 라인)
   ```

2. **글** (자동 생성)
   ```
   [현장 스케치]
   색으로 표현하는 나만의 이야기...
   
   1️⃣ 색 선택의 의미
   2️⃣ 손으로 만드는 과정
   3️⃣ 함께하는 경험
   4️⃣ 완성의 의미
   
   #구미호_상상의발견 #문화예술교육 ...
   
   본 사업은 (재)구미문화재단...
   ```

3. **카톡 메시지**
   - 이미지 + 글이 자동으로 발송됨

---

## 🔐 GitHub 관리

### 커밋 메시지 규칙
```
git commit -m "주간 콘텐츠: [주제] (MM/DD)"

예시:
- "주간 콘텐츠: 팔찌 만들기 (09/15)"
- "주간 콘텐츠: 북커버 디자인 (09/22)"
- "주간 콘텐츠: 에코백 만들기 (09/29)"
```

### 자동 커밋 (GitHub Actions 예정)
- [ ] 매주 정해진 시간에 자동 커밋
- [ ] 변경사항 자동 정리
- [ ] 통계 자동 생성

---

## 📚 **상세 가이드**

더 자세한 내용은 **`Creative_Content_Auto_PRD.md`** 를 참고하세요:
- 5가지 핵심 원칙
- 레이아웃 계층 구조
- 자동화 워크플로우
- GitHub 활용법

---

## ✅ **준비 완료 체크**

- [x] 폴더 구조 생성
- [x] .gitignore 설정
- [x] README.md 작성
- [x] PRD 완성
- [x] Python 스크립트 준비
- [ ] 첫 콘텐츠 생성
- [ ] GitHub 첫 커밋

---

## 📞 **문제 해결**

### 이미지가 생성되지 않음
```bash
# Python 설치 확인
python --version

# 필요한 라이브러리 확인
pip install Pillow

# Pretendard 폰트 확인
ls Pretendard-1.3.9/
```

### 카톡 발송이 안 됨
```bash
# Play MCP 연결 확인
/mcp
```

### 폴더 구조 복구
```bash
mkdir -p photos education outputs scripts archives
```

---

## 🎬 **다음 단계**

1. **이번 주 콘텐츠 생성**
   - 사진 준비
   - 교육자료 정리
   - Claude에게 보내기

2. **GitHub 첫 커밋**
   ```bash
   git add .
   git commit -m "초기 설정: 자동화 시스템 구축"
   git push origin main
   ```

3. **매주 반복**
   - 새로운 주제
   - 새로운 사진
   - 자동으로 처리
   - 결과 저장

---

## 📞 **연락처**
- 꾸미스튜디오: @qoomee_studio
- GitHub: qoomee_studio/creative-content

---

**Last Updated:** 2026-09-15  
**Status:** ✅ Ready to go!  
**Next:** 첫 콘텐츠 생성 준비 중...

