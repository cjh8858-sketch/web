from flask import Blueprint, jsonify, request
from db import get_db_connection
import json

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/naver/login", methods=["POST"])
def start_naver_login():
    """Start Naver login session via Playwright"""
    try:
        from services.naver_publisher import launch_login_session

        result = launch_login_session()
        if result.get("success"):
            return jsonify({"success": True, "message": "Naver login completed"})
        else:
            return jsonify({"success": False, "error": result.get("error", "Login failed")}), 400
    except Exception as e:
        print(f"Error starting Naver login: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@auth_bp.route("/naver/status", methods=["GET"])
def check_naver_session_status():
    """Check if Naver session is valid"""
    try:
        from services.naver_publisher import is_session_valid

        is_valid = is_session_valid()
        return jsonify({"success": True, "is_valid": is_valid})
    except Exception as e:
        print(f"Error checking session status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@auth_bp.route("/naver/logout", methods=["POST"])
def logout_naver():
    """Clear Naver session"""
    try:
        from config import Config
        import os

        if Config.SESSION_STATE_PATH.exists():
            os.remove(Config.SESSION_STATE_PATH)

        # Update session meta
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO naver_session_meta (id, saved_at, is_valid) VALUES (1, NULL, 0)"
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Logged out"})
    except Exception as e:
        print(f"Error logging out: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
