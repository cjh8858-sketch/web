# 네이버 블로그 자동화 (Naver Blog Automation)

## 개요

네이버 블로그 자동화 플랫폼은 사용자가 관심분야를 입력하면 자동으로 네이버 뉴스/인기 블로그를 수집하고, Claude AI가 표준적인 블로그 톤으로 새 글을 작성하며, 무료 이미지를 자동 선정한 뒤, 네이버 블로그에 완전 자동으로 발행하는 개인용 로컬 웹 대시보드입니다.

**핵심 특징:**
- 관심분야별 자동 글감 수집 (네이버 오픈API)
- Claude Code CLI를 통한 AI 글쓰기 (사용자의 Claude Pro/Max 구독 활용)
- Unsplash + Pixabay를 활용한 이미지 자동 선정
- Playwright를 통한 네이버 블로그 자동 발행
- APScheduler 기반 스케줄 자동화
- 로컬 PC에서 상시 실행

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask 웹 대시보드                          │
│  (localhost:5000, 관심분야 관리, 설정, 발행이력 조회)         │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────┬──────────────────┐
        ↓                  ↓                  ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 콘텐츠 수집   │  │ AI 글쓰기     │  │ 이미지 처리   │
│ (naver_      │  │ (ai_writer.py│  │ (image_      │
│  search.py)  │  │ +            │  │  search.py)  │
│              │  │ Claude CLI)  │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
    ↓                  ↓                  ↓
네이버 오픈API     subprocess로       Unsplash/
(뉴스/블로그)     claude -p 호출     Pixabay API
    ↓                  ↓                  ↓
                 ┌──────────────────────────────┐
                 │   네이버 블로그 발행           │
                 │ (naver_publisher.py +        │
                 │  Playwright 자동화)          │
                 └──────────────────────────────┘
                           ↓
                    APScheduler
                   (스케줄 기반 자동실행)
```

**스택:**
- 웹프레임워크: Flask 3.0.0
- 자동화 브라우저: Playwright
- 스케줄링: APScheduler (BackgroundScheduler)
- 데이터베이스: SQLite (관심분야, 스케줄, 발행이력)
- AI: Claude Code CLI (-p 모드, 비대화형)
- 이미지 API: Unsplash, Pixabay
- API: 네이버 오픈API (검색)

---

## 설치 및 실행

### 1. 환경 준비

**필수 요구사항:**
- Python 3.8+
- Claude Code CLI 설치 및 로그인 (`claude --version` 으로 확인)
- Windows 11 Home 이상

### 2. 설치 단계

```bash
# 프로젝트 디렉토리로 이동
cd naver-blog-automation

# 가상 환경 생성 (권장)
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (최초 1회만)
python -m playwright install chromium

# 데이터베이스 초기화
python db.py
```

### 3. .env 파일 생성

```bash
# .env.example을 .env로 복사
cp .env.example .env
```

`.env` 파일을 편집하여 필요시 포트, 타임아웃 등을 조정:

```
FLASK_ENV=development
FLASK_PORT=5000
FLASK_HOST=127.0.0.1
CLAUDE_CLI_TIMEOUT_SEC=180
```

### 4. 서버 실행

```bash
python app.py
```

서버가 시작되면 브라우저에서 `http://localhost:5000` 으로 접속합니다.

### 5. 초기 설정

1. **대시보드 접속:** http://localhost:5000
2. **설정 페이지** → **API 설정** 에서:
   - 네이버 Client ID/Secret 입력
   - Unsplash/Pixabay API 키 입력
   - 네이버 블로그 ID 입력
   - 각 항목별로 저장 버튼 클릭

3. **네이버 로그인:**
   - 대시보드 로그인 섹션의 "네이버 로그인" 버튼 클릭
   - Playwright가 자동으로 네이버 로그인 창을 띄움
   - 사용자가 직접 로그인 수행 (자동화 아님)
   - 로그인 완료 후 자동으로 세션 저장

4. **관심분야 추가:**
   - 대시보드 "관심분야 관리" 섹션에서 키워드 입력
   - 발행 시간 설정 (기본값: 매일 09:00)
   - "관심분야 추가" 버튼 클릭

### 6. 자동 발행 설정 (M7 단계)

관심분야별로 스케줄이 자동으로 생성되면, APScheduler가 설정된 시간마다 다음 파이프라인을 자동 실행:

1. 네이버 뉴스/블로그 검색 (콘텐츠 수집)
2. Claude AI로 글 작성
3. Unsplash/Pixabay에서 이미지 검색
4. 이미지 적합성 AI 판단
5. 네이버 블로그에 자동 발행

---

## API 구조

### 대시보드 라우트

| 경로 | 메서드 | 설명 |
|------|--------|------|
| `/` | GET | 메인 대시보드 (관심분야 관리) |
| `/settings` | GET | API 키 및 설정 입력 페이지 |
| `/history` | GET | 발행 이력 조회 페이지 |

### REST API 엔드포인트

#### 관심분야 관리

| 경로 | 메서드 | 설명 |
|------|--------|------|
| `/api/interests` | GET | 모든 관심분야 조회 (스케줄 포함) |
| `/api/interests` | POST | 관심분야 생성 |
| `/api/interests/<id>` | PUT | 관심분야/스케줄 수정 |
| `/api/interests/<id>` | DELETE | 관심분야 삭제 |

#### 설정 관리

| 경로 | 메서드 | 설명 |
|------|--------|------|
| `/api/settings` | GET | 모든 설정 조회 |
| `/api/settings/naver` | POST | 네이버 API 키 저장 |
| `/api/settings/images` | POST | 이미지 API 키 저장 |
| `/api/settings/blog` | POST | 네이버 블로그 ID 저장 |
| `/api/settings/naver/test` | POST | 네이버 API 연결 테스트 |

#### 인증 (로그인)

| 경로 | 메서드 | 설명 |
|------|--------|------|
| `/api/auth/naver/login` | POST | 네이버 로그인 시작 |
| `/api/auth/naver/status` | GET | 세션 유효성 확인 |
| `/api/auth/naver/logout` | POST | 로그아웃 |

#### 발행

| 경로 | 메서드 | 설명 |
|------|--------|------|
| `/api/publish/now` | POST | 수동 발행 트리거 (M7) |
| `/api/publish/history` | GET | 발행 이력 조회 |
| `/api/publish/history/<id>` | GET | 발행 이력 상세 조회 |

---

## 서비스 모듈

### `services/naver_search.py`
네이버 오픈API 검색 클라이언트

**주요 함수:**
- `search_news(query, display=10)`: 뉴스 검색
- `search_blogs(query, display=10)`: 블로그 검색
- `collect_source_material(keyword)`: 뉴스+블로그 통합 수집

### `services/ai_writer.py`
Claude Code CLI 서브프로세스 래퍼

**주요 함수:**
- `call_claude_cli(prompt, json_schema=None, tools="", timeout=180)`: CLI 호출
- `generate_blog_post(keyword, source_materials)`: 블로그 글 생성

### `services/image_search.py`
Unsplash/Pixabay 이미지 검색 및 적합성 판단

**주요 함수:**
- `search_unsplash(query, count=5)`: Unsplash 검색
- `search_pixabay(query, count=5)`: Pixabay 검색
- `find_images_for_section(image_keyword)`: 섹션별 이미지 검색
- `judge_image_fit(section_body, candidates)`: 적합성 판단

### `services/naver_publisher.py`
Playwright 기반 네이버 블로그 자동 로그인 및 발행

**주요 함수:**
- `ensure_playwright_ready()`: Playwright 설치 확인
- `launch_login_session(timeout_sec=300)`: 로그인 세션 생성
- `is_session_valid()`: 세션 유효성 확인
- `publish_post(blog_id, post, image_paths)`: 블로그 발행

### `services/scheduler_service.py`
APScheduler 스케줄 관리 (M7)

**주요 함수:**
- `init_scheduler(app)`: 스케줄러 초기화
- `register_daily_job(interest_id, hour, minute)`: 일일 잡 등록
- `remove_job(interest_id)`: 잡 제거
- `run_full_pipeline(interest_id)`: 전체 파이프라인 실행

---

## 데이터베이스 스키마

### `settings` 테이블
API 키 및 설정값 저장

```
key                 value
naver_client_id     xxx
naver_client_secret xxx
unsplash_key        xxx
pixabay_key         xxx
naver_blog_id       xxx
```

### `interests` 테이블
추적할 관심분야

```
id    keyword         active  created_at
1     Python          1       2026-01-15 10:30:00
2     머신러닝        1       2026-01-16 14:22:00
```

### `schedules` 테이블
각 관심분야의 발행 일정

```
id    interest_id  run_hour  run_minute  enabled  last_run_at
1     1            9         0           1        2026-01-20 09:15:42
2     2            14        30          1        NULL
```

### `publish_history` 테이블
발행 이력 추적

```
id    interest_id  keyword      title              naver_post_url              status   error_message  created_at
1     1            Python       Python 기초 정리     https://blog.naver.com/... success  NULL           2026-01-20 09:15:42
2     2            머신러닝     ML 모델 비교        NULL                        failed   Timeout        2026-01-21 14:30:10
```

### `naver_session_meta` 테이블
Playwright 로그인 세션 메타데이터

```
id  saved_at                 is_valid
1   2026-01-22 10:45:00      1
```

---

## 트러블슈팅

### Claude CLI 관련 문제

#### 문제: `claude: command not found`
**해결:**
1. Claude Code CLI가 설치되어 있는지 확인: `claude --version`
2. 미설치 시 설치: [Claude Code 공식 문서](https://claude.com/claude-code) 참고
3. 설치 후 로그인: `claude login`

#### 문제: `subprocess.TimeoutExpired`
**해결:**
- `.env` 파일에서 `CLAUDE_CLI_TIMEOUT_SEC` 값을 늘려봅니다 (기본값: 180초)
- 프롬프트가 너무 길다면 source_materials 개수를 줄입니다
- Claude Code CLI의 응답 속도가 느린 경우 로컬 네트워크 상태를 확인합니다

#### 문제: `is_error: true` 응답
**해결:**
- `result` 필드의 오류 메시지를 확인합니다
- Claude Code 세션이 유효한지 확인: `claude login`
- 프롬프트에 특수문자나 인코딩 문제가 있는지 확인

### Playwright 관련 문제

#### 문제: `playwright: command not found`
**해결:**
```bash
python -m playwright install chromium
```

#### 문제: 네이버 로그인 버튼 클릭 후 브라우저 창이 열리지 않음
**해결:**
1. `.env`에서 `PLAYWRIGHT_LAUNCH_TIMEOUT` 값 확인 (기본값: 30000ms)
2. Windows 방화벽에서 Python이 차단되지 않았는지 확인
3. Playwright 기본 브라우저(Chromium)가 올바르게 설치되었는지 확인: `python -m playwright install chromium`

#### 문제: 로그인 후 세션이 저장되지 않음
**해결:**
1. `data/` 폴더가 존재하고 쓰기 권한이 있는지 확인
2. `data/naver_session.json` 파일이 정상적으로 생성되었는지 확인
3. 안티바이러스/보안 소프트웨어가 파일 생성을 차단하는지 확인

### 네이버 API 관련 문제

#### 문제: `401 Unauthorized`
**해결:**
- 설정 페이지에서 Client ID/Secret을 다시 확인
- [네이버 개발자센터](https://developers.naver.com)에서 애플리케이션이 활성 상태인지 확인
- "검색" API 권한이 승인되었는지 확인

#### 문제: `429 Too Many Requests`
**해결:**
- 네이버 검색 API는 일 25,000회 호출 한도가 있습니다
- 발행 스케줄 주기를 조정하여 호출 빈도를 줄입니다
- 여러 관심분야가 동시에 발행되지 않도록 시간을 분산시킵니다

### 이미지 API 관련 문제

#### 문제: `Unsplash/Pixabay 검색 결과가 없음`
**해결:**
- API 키가 올바르게 설정되었는지 설정 페이지에서 확인
- 키워드가 너무 구체적이거나 한국어일 경우 영문으로 변경
- 여러 이미지 검색 후 선택 기능은 M5 단계에서 세부 구현됩니다

### 스마트에디터 자동화 문제

#### 문제: 글 발행이 실패하거나 내용이 입력되지 않음
**해결:**
- 네이버 로그인 상태를 확인: 대시보드 → "네이버 로그인" 섹션
- `data/naver_session.json`이 있고 유효한지 확인
- 네이버 블로그 스마트에디터 UI가 변경되었을 수 있으므로 셀렉터를 다시 확인
- `services/naver_publisher.py`의 `_fill_smart_editor()` 함수의 셀렉터를 업데이트합니다

#### 셀렉터 업데이트 방법:
```bash
# 실제 글쓰기 페이지에서 Playwright 코드 생성기 실행
python -m playwright codegen --save-trace trace.zip https://blog.naver.com/[블로그ID]/PostWrite
# 브라우저에서 실제 글 입력 과정을 한 번 수행
# 생성된 코드에서 selector를 복사해 naver_publisher.py에 반영
```

### 기타 문제

#### 문제: `total_cost_usd` 필드가 응답에 표시됨 (과금 우려)
**설명:** Claude Code CLI 응답에 포함된 `total_cost_usd`는 **구독 크레딧 사용량의 환산 표시일 뿐이며, 실제 API 과금이 아닙니다.** 사용자의 Claude Pro/Max 구독 안에서 처리되므로 추가 비용이 발생하지 않습니다.

#### 문제: 서버가 자꾸 종료됨
**해결:**
- 백그라운드에서 실행하는 것을 권장합니다:
  - Windows: `start python app.py`
  - macOS/Linux: `python app.py &`
- 더 안정적인 실행을 위해 `flask run --reload` 옵션 제거 (현재는 포함 안 됨)
- 로그 파일 확인: `logs/app.log`

---

## 개발 단계별 마일스톤

| M | 내용 | 상태 |
|---|------|------|
| M1 | 뼈대: Flask 앱, DB 스키마, 대시보드 UI, 관심분야 CRUD | ✓ 완료 |
| M2 | 네이버 로그인/세션: Playwright 자동화 | 예정 |
| M3 | 콘텐츠 수집: 네이버 오픈API 클라이언트 | 예정 |
| M4 | AI 글쓰기: Claude CLI 서브프로세스 | 예정 |
| M5 | 이미지 처리: Unsplash/Pixabay + 적합성 판단 | 예정 |
| M6 | 발행 자동화: 스마트에디터 DOM 조사 및 입력 | 예정 |
| M7 | 전체 파이프라인 + 스케줄러 통합 | 예정 |

---

## 라이선스 및 저작권

이 프로젝트는 개인 사용자를 위한 로컬 자동화 도구입니다.

---

## 문의 및 피드백

개선 사항이나 버그 보고는 [Claude Code 이슈](https://github.com/anthropics/claude-code/issues)로 부탁드립니다.
