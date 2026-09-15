from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from db import get_db_connection
import datetime
import pytz

scheduler = BackgroundScheduler(timezone="Asia/Seoul")

def init_scheduler(app):
    """
    Flask 앱 시작 시 데이터베이스에 저장된 스케줄을 읽어 APScheduler에 등록.
    """
    try:
        # DB에서 활성화된 스케줄 읽기
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, interest_id, run_hour, run_minute FROM schedules WHERE enabled = 1"
        )
        schedules = cursor.fetchall()
        conn.close()

        # 각 스케줄을 APScheduler에 등록
        for schedule in schedules:
            schedule_id = schedule["id"]
            interest_id = schedule["interest_id"]
            run_hour = schedule["run_hour"]
            run_minute = schedule["run_minute"]

            register_daily_job(interest_id, run_hour, run_minute, schedule_id)

        # 스케줄러 시작
        if not scheduler.running:
            scheduler.start()
            print(f"Scheduler started with {len(schedules)} jobs")

    except Exception as e:
        print(f"Error initializing scheduler: {e}")

def register_daily_job(interest_id: int, hour: int, minute: int, schedule_id: int = None):
    """
    관심분야에 대한 매일 실행 잡을 등록.

    Args:
        interest_id: 관심분야 ID
        hour: 실행 시간 (0-23)
        minute: 실행 분 (0-59)
        schedule_id: 스케줄 ID (없으면 DB에서 조회)
    """
    try:
        if schedule_id is None:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM schedules WHERE interest_id = ?", (interest_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                schedule_id = row["id"]

        job_id = f"interest_{interest_id}"

        # 기존 잡이 있으면 제거
        try:
            scheduler.remove_job(job_id)
            print(f"Removed existing job: {job_id}")
        except:
            pass

        # 새 잡 등록
        trigger = CronTrigger(hour=hour, minute=minute, timezone="Asia/Seoul")
        scheduler.add_job(
            func=run_full_pipeline,
            trigger=trigger,
            args=[interest_id],
            id=job_id,
            name=f"Interest {interest_id} ({hour:02d}:{minute:02d})",
            replace_existing=True
        )

        print(f"Job registered: {job_id} at {hour:02d}:{minute:02d}")

    except Exception as e:
        print(f"Error registering job for interest {interest_id}: {e}")

def remove_job(interest_id: int):
    """
    관심분야에 대한 스케줄 잡 제거.
    """
    try:
        job_id = f"interest_{interest_id}"
        scheduler.remove_job(job_id)
        print(f"Job removed: {job_id}")
    except Exception as e:
        print(f"Error removing job for interest {interest_id}: {e}")

def run_full_pipeline(interest_id: int):
    """
    전체 파이프라인 실행: 수집 → 작성 → 이미지 선정 → 발행.

    각 단계의 성공/실패를 publish_history에 기록.
    """
    try:
        print(f"\n{'='*60}")
        print(f"Starting full pipeline for interest_id: {interest_id}")
        print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # 1. 관심분야 정보 조회
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT keyword FROM interests WHERE id = ?", (interest_id,))
        interest = cursor.fetchone()
        conn.close()

        if not interest:
            print(f"Interest not found: {interest_id}")
            return

        keyword = interest["keyword"]
        print(f"\n[1/4] Collecting content for keyword: {keyword}")

        # 2. 콘텐츠 수집
        try:
            from services.naver_search import collect_source_material
            source_materials = collect_source_material(keyword, display=5)

            if not source_materials:
                _record_failure(interest_id, keyword, "콘텐츠 수집 실패: 결과 없음")
                return

            print(f"  ✓ Collected {len(source_materials)} materials")
        except Exception as e:
            _record_failure(interest_id, keyword, f"콘텐츠 수집 실패: {str(e)}")
            return

        # 3. AI 글쓰기
        print(f"\n[2/4] Generating blog post with AI")
        try:
            from services.ai_writer import generate_blog_post
            result = generate_blog_post(keyword, source_materials)

            if not result["success"]:
                _record_failure(interest_id, keyword, f"글쓰기 실패: {result.get('error', 'Unknown')}")
                return

            post = result["data"]
            print(f"  ✓ Generated post: {post.get('title', 'N/A')}")
        except Exception as e:
            _record_failure(interest_id, keyword, f"글쓰기 실패: {str(e)}")
            return

        # 4. 이미지 처리
        print(f"\n[3/4] Finding and selecting images")
        image_paths = {}
        try:
            from services.image_search import find_images_for_section, judge_image_fit, download_image

            sections = post.get("sections", [])
            for idx, section in enumerate(sections):
                image_keyword = section.get("image_keyword", "")
                if not image_keyword:
                    continue

                # 이미지 검색
                candidates = find_images_for_section(image_keyword, min_count=3)
                if not candidates:
                    print(f"  ⚠ No images found for: {image_keyword}")
                    continue

                # 이미지 적합성 판단
                judgment = judge_image_fit(section.get("body", ""), candidates)
                selected_url = judgment.get("selected_url", "")

                if not selected_url:
                    print(f"  ⚠ Failed to judge image for section {idx}")
                    continue

                # 이미지 다운로드
                image_filename = f"section_{idx}.jpg"
                image_path = str(Config.IMAGES_DIR / image_filename)
                downloaded = download_image(selected_url, image_path)

                if downloaded:
                    image_paths[f"section_{idx}"] = downloaded
                    print(f"  ✓ Image {idx+1}: {judgment.get('reason', 'Selected')}")

            if not image_paths:
                print(f"  ⚠ No images downloaded, continuing without images")
        except Exception as e:
            print(f"  ⚠ Image processing error: {e}")
            # 이미지 없이도 진행 가능

        # 5. 발행
        print(f"\n[4/4] Publishing to Naver blog")
        try:
            from services.naver_publisher import publish_post
            from routes.api_settings import get_setting

            blog_id = get_setting("naver_blog_id")
            if not blog_id:
                _record_failure(interest_id, keyword, "블로그 ID 설정 필요")
                return

            publish_result = publish_post(blog_id, post, image_paths)

            if not publish_result["success"]:
                _record_failure(
                    interest_id,
                    keyword,
                    publish_result.get("error", "Unknown publish error")
                )
                return

            post_url = publish_result.get("url", "")
            _record_success(interest_id, keyword, post.get("title", "N/A"), post_url)
            print(f"  ✓ Published: {post_url}")

        except Exception as e:
            _record_failure(interest_id, keyword, f"발행 실패: {str(e)}")
            return

        print(f"\n{'='*60}")
        print(f"Pipeline completed successfully!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"Fatal error in pipeline: {e}")
        _record_failure(interest_id, keyword, f"파이프라인 오류: {str(e)}")

def _record_success(interest_id: int, keyword: str, title: str, post_url: str):
    """발행 성공 기록"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.datetime.now().isoformat()
        cursor.execute(
            """INSERT INTO publish_history
               (interest_id, keyword, title, naver_post_url, status, created_at)
               VALUES (?, ?, ?, ?, 'success', ?)""",
            (interest_id, keyword, title, post_url, now)
        )

        # 마지막 실행 시간 업데이트
        cursor.execute(
            "UPDATE schedules SET last_run_at = ? WHERE interest_id = ?",
            (now, interest_id)
        )

        conn.commit()
        conn.close()
        print(f"Success recorded in database")
    except Exception as e:
        print(f"Error recording success: {e}")

def _record_failure(interest_id: int, keyword: str, error_message: str):
    """발행 실패 기록"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.datetime.now().isoformat()
        cursor.execute(
            """INSERT INTO publish_history
               (interest_id, keyword, status, error_message, created_at)
               VALUES (?, ?, 'failed', ?, ?)""",
            (interest_id, keyword, error_message, now)
        )

        # 마지막 실행 시간 업데이트
        cursor.execute(
            "UPDATE schedules SET last_run_at = ? WHERE interest_id = ?",
            (now, interest_id)
        )

        conn.commit()
        conn.close()
        print(f"Failure recorded: {error_message}")
    except Exception as e:
        print(f"Error recording failure: {e}")

# 원본 코드에서 Config import 누락
from config import Config
