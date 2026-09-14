import json
import time
import subprocess
from pathlib import Path
from config import Config

SESSION_STATE_PATH = Config.SESSION_STATE_PATH

def ensure_playwright_ready():
    """확인: Playwright가 설치되어 있는지, 아니면 자동 설치"""
    try:
        import playwright
        print("Playwright already installed")
    except ImportError:
        print("Installing Playwright...")
        subprocess.run(["pip", "install", "playwright"], check=True)
        print("Installing Chromium browser...")
        subprocess.run(["python", "-m", "playwright", "install", "chromium"], check=True)
        print("Playwright setup completed")

def launch_login_session(timeout_sec: int = 300) -> dict:
    """
    Non-headless 브라우저로 네이버 로그인 페이지를 띄워 사용자가 직접 로그인하도록 함.
    로그인 완료 후 storage_state를 저장.
    """
    try:
        from playwright.sync_api import sync_playwright

        ensure_playwright_ready()

        result = {
            "success": False,
            "message": "",
            "error": None
        }

        with sync_playwright() as p:
            # Non-headless 브라우저 실행
            browser = p.chromium.launch(headless=False, timeout=Config.PLAYWRIGHT_LAUNCH_TIMEOUT)
            context = browser.new_context()
            page = context.new_page()

            # 네이버 로그인 페이지로 이동
            print(f"Opening Naver login page...")
            page.goto("https://nid.naver.com/nidlogin.login", timeout=timeout_sec * 1000)

            # 로그인 완료 대기 - 특정 쿠키 또는 URL 변경을 감지
            # 네이버 로그인 후 특정 페이지로 자동 리다이렉트되거나 특정 쿠키가 설정됨
            login_completed = False
            start_time = time.time()

            while not login_completed and (time.time() - start_time) < timeout_sec:
                try:
                    # 쿠키 확인: NID_AUT 또는 NID_SES
                    cookies = context.cookies()
                    cookie_names = [c.get("name") for c in cookies]

                    if "NID_AUT" in cookie_names or "NID_SES" in cookie_names:
                        # 로그인 쿠키 감지
                        login_completed = True
                        print("Login successful - Naver cookies detected")
                        break

                    # 주기적으로 확인 (500ms)
                    time.sleep(0.5)

                except Exception as e:
                    print(f"Cookie check error: {e}")
                    time.sleep(1)

            if not login_completed:
                context.close()
                browser.close()
                result["error"] = f"Login timeout after {timeout_sec}s"
                return result

            # 로그인 성공 - storage_state 저장
            session_data = context.storage_state()

            Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(SESSION_STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            # 세션 메타 업데이트
            from db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()

            import datetime
            now = datetime.datetime.now().isoformat()
            cursor.execute(
                "INSERT OR REPLACE INTO naver_session_meta (id, saved_at, is_valid) VALUES (1, ?, 1)",
                (now,)
            )
            conn.commit()
            conn.close()

            context.close()
            browser.close()

            result["success"] = True
            result["message"] = "Login successful and session saved"
            return result

    except Exception as e:
        print(f"Error in launch_login_session: {e}")
        return {
            "success": False,
            "message": "",
            "error": str(e)
        }

def is_session_valid() -> bool:
    """
    저장된 storage_state가 유효한지 확인.
    네이버 블로그 글쓰기 페이지 진입 가능 여부로 판단.
    """
    try:
        if not SESSION_STATE_PATH.exists():
            print(f"Session file not found: {SESSION_STATE_PATH}")
            return False

        from playwright.sync_api import sync_playwright

        with open(SESSION_STATE_PATH, "r", encoding="utf-8") as f:
            session_data = json.load(f)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, timeout=Config.PLAYWRIGHT_LAUNCH_TIMEOUT)
            context = browser.new_context(storage_state=session_data)
            page = context.new_page()

            try:
                # 네이버 블로그 글쓰기 페이지로 이동 시도
                # 로그인되지 않으면 로그인 페이지로 리다이렉트됨
                response = page.goto("https://blog.naver.com/PostWrite", timeout=10000, wait_until="domcontentloaded")

                # 최종 URL이 글쓰기 페이지인지 확인
                current_url = page.url
                is_valid = "/PostWrite" in current_url or "/blog/" in current_url

                context.close()
                browser.close()

                print(f"Session validity check: {is_valid} (URL: {current_url})")
                return is_valid

            except Exception as e:
                print(f"Session check failed: {e}")
                context.close()
                browser.close()
                return False

    except Exception as e:
        print(f"Error checking session: {e}")
        return False

def publish_post(blog_id: str, post: dict, image_paths: dict) -> dict:
    """
    저장된 세션으로 네이버 블로그 스마트에디터에 글을 입력하고 발행.

    Args:
        blog_id: 네이버 블로그 ID (예: "your_blog_name")
        post: 글 정보 {"title": str, "intro": str, "sections": [...], "outro": str, "tags": [...]}
        image_paths: 섹션별 이미지 경로 {"section_0": "path/to/image.jpg", ...}

    Returns:
        {"success": bool, "url": str or "error": str}
    """
    try:
        if not SESSION_STATE_PATH.exists():
            return {"success": False, "error": "Session not found. Please login first."}

        from playwright.sync_api import sync_playwright

        with open(SESSION_STATE_PATH, "r", encoding="utf-8") as f:
            session_data = json.load(f)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, timeout=Config.PLAYWRIGHT_LAUNCH_TIMEOUT)
            context = browser.new_context(storage_state=session_data)
            page = context.new_page()

            try:
                # 글쓰기 페이지로 이동
                print(f"Navigating to blog write page...")
                page.goto("https://blog.naver.com/PostWrite", timeout=15000)

                # 스마트에디터 로딩 대기
                time.sleep(2)

                # 제목 입력
                print(f"Setting title: {post.get('title', '')}")
                _fill_smart_editor(page, post, image_paths)

                # 발행 버튼 클릭
                print("Publishing post...")
                publish_result = _click_publish_button(page)

                context.close()
                browser.close()

                if publish_result["success"]:
                    return {
                        "success": True,
                        "url": publish_result.get("url", "")
                    }
                else:
                    return {
                        "success": False,
                        "error": publish_result.get("error", "Failed to publish")
                    }

            except Exception as e:
                print(f"Error during publish: {e}")
                context.close()
                browser.close()
                return {"success": False, "error": str(e)}

    except Exception as e:
        print(f"Error in publish_post: {e}")
        return {"success": False, "error": str(e)}

def _fill_smart_editor(page, post: dict, image_paths: dict):
    """
    스마트에디터에 제목, 본문, 이미지, 태그를 입력.

    주의: 스마트에디터 구조는 페이지 구조에 따라 달라질 수 있으므로
    실제 구현 시 playwright codegen으로 셀렉터를 확인해야 함.
    """
    try:
        # 제목 입력 (M6 단계에서 실제 셀렉터 확인 필요)
        title = post.get("title", "")
        if title:
            try:
                # 일반적인 제목 입력 필드 시도
                title_input = page.locator("input[name='title'], input[id='postTitle'], input[placeholder*='제목']").first
                if title_input.is_visible():
                    title_input.clear()
                    title_input.fill(title)
                    print(f"Title entered: {title[:50]}...")
            except Exception as e:
                print(f"Title input failed (will retry in M6): {e}")

        # 본문 구성 (intro + sections + outro)
        content_lines = []

        # 인트로
        if post.get("intro"):
            content_lines.append(post["intro"])
            content_lines.append("")

        # 섹션들 (제목 + 본문 + 이미지)
        sections = post.get("sections", [])
        for idx, section in enumerate(sections):
            heading = section.get("heading", "")
            body = section.get("body", "")

            if heading:
                content_lines.append(f"[{heading}]")
            if body:
                content_lines.append(body)

            # 이미지 삽입 (경로가 있으면)
            image_key = f"section_{idx}"
            if image_key in image_paths:
                content_lines.append(f"[IMAGE: {image_paths[image_key]}]")

            content_lines.append("")

        # 아웃트로
        if post.get("outro"):
            content_lines.append(post["outro"])

        content = "\n".join(content_lines)

        # 에디터 본문 입력 (M6 단계에서 iframe 구조 확인 필요)
        try:
            # 스마트에디터는 iframe 내부의 contenteditable div 구조
            # 이 부분은 M6 단계에서 실제 페이지 검사 후 업데이트 필요
            editor_frame = page.frame("smarteditor_iframe")
            if editor_frame:
                editor = editor_frame.locator("body").first
                editor.click()
                editor.type(content, delay=10)  # 타이핑 속도 조절
                print(f"Content entered: {len(content)} chars")
            else:
                print("Smart editor iframe not found (will be fixed in M6)")

        except Exception as e:
            print(f"Content input failed (iframe structure to be confirmed in M6): {e}")

        # 태그 입력 (선택사항)
        tags = post.get("tags", [])
        if tags:
            try:
                tag_input = page.locator("input[name='tags'], input[id='tags'], input[placeholder*='태그']").first
                if tag_input.is_visible():
                    tag_input.fill(", ".join(tags))
                    print(f"Tags entered: {', '.join(tags[:3])}...")
            except Exception as e:
                print(f"Tag input failed: {e}")

    except Exception as e:
        print(f"Error filling smart editor: {e}")

def _click_publish_button(page) -> dict:
    """
    스마트에디터의 발행(등록) 버튼을 찾아 클릭하고 완료를 대기.

    주의: 발행 후 확인 팝업(카테고리, 공개설정 등)이 나올 수 있음 (M6에서 확인 필요)
    """
    try:
        # 발행 버튼 찾기 (일반적인 셀렉터들)
        publish_button_selectors = [
            "button:has-text('발행')",
            "button:has-text('등록')",
            "button[class*='publish']",
            "button[class*='register']",
            "button[id*='publish']",
            "//button[contains(text(), '발행')]",
            "//button[contains(text(), '등록')]"
        ]

        publish_button = None
        for selector in publish_button_selectors:
            try:
                button = page.locator(selector).first
                if button.is_visible():
                    publish_button = button
                    break
            except:
                continue

        if not publish_button:
            return {"success": False, "error": "Publish button not found"}

        print("Clicking publish button...")
        publish_button.click()

        # 발행 후 페이지 로드 대기 (M6에서 실제 완료 조건 확인 필요)
        time.sleep(3)

        # 최종 URL에서 블로그 글 주소 추출 (네이버 블로그 URL 형식)
        final_url = page.url
        if "blog.naver.com" in final_url:
            return {"success": True, "url": final_url}
        else:
            return {"success": False, "error": f"Unexpected URL after publish: {final_url}"}

    except Exception as e:
        print(f"Error clicking publish button: {e}")
        return {"success": False, "error": str(e)}
