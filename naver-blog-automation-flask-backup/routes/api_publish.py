from flask import Blueprint, jsonify, request
from db import get_db_connection

publish_bp = Blueprint("publish", __name__, url_prefix="/api/publish")

@publish_bp.route("/now", methods=["POST"])
def publish_now():
    """Manually trigger publish for an interest"""
    try:
        data = request.json
        interest_id = data.get("interest_id")

        if not interest_id:
            return jsonify({"success": False, "error": "Interest ID is required"}), 400

        # Run full pipeline immediately
        from services.scheduler_service import run_full_pipeline
        import threading

        # 백그라운드 스레드에서 실행 (응답을 빨리 반환하기 위해)
        thread = threading.Thread(target=run_full_pipeline, args=(interest_id,))
        thread.daemon = True
        thread.start()

        return jsonify({
            "success": True,
            "message": "Publishing started (background process)",
            "interest_id": interest_id
        })
    except Exception as e:
        print(f"Error triggering publish: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@publish_bp.route("/history", methods=["GET"])
def get_publish_history():
    """Get publishing history with filters"""
    try:
        interest_id = request.args.get("interest_id", type=int)
        limit = request.args.get("limit", default=50, type=int)

        conn = get_db_connection()
        cursor = conn.cursor()

        if interest_id:
            cursor.execute(
                """SELECT id, interest_id, keyword, title, naver_post_url, status, error_message, created_at
                   FROM publish_history WHERE interest_id = ? ORDER BY created_at DESC LIMIT ?""",
                (interest_id, limit)
            )
        else:
            cursor.execute(
                """SELECT id, interest_id, keyword, title, naver_post_url, status, error_message, created_at
                   FROM publish_history ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            )

        rows = cursor.fetchall()
        conn.close()

        history = [dict(row) for row in rows]
        return jsonify({"success": True, "data": history})
    except Exception as e:
        print(f"Error fetching publish history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@publish_bp.route("/history/<int:history_id>", methods=["GET"])
def get_publish_detail(history_id):
    """Get detailed info for a specific publish history entry"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, interest_id, keyword, title, naver_post_url, status, error_message, created_at
               FROM publish_history WHERE id = ?""",
            (history_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({"success": False, "error": "History entry not found"}), 404

        return jsonify({"success": True, "data": dict(row)})
    except Exception as e:
        print(f"Error fetching publish detail: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
