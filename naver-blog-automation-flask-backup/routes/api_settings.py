from flask import Blueprint, request, jsonify
from db import get_db_connection

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")

def get_setting(key):
    """Helper to get a setting value"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_setting(key, value):
    """Helper to set a setting value"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

@settings_bp.route("", methods=["GET"])
def get_settings():
    """Get all settings (API keys and blog ID)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        conn.close()

        settings = {row["key"]: row["value"] for row in rows}
        return jsonify({"success": True, "data": settings})
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@settings_bp.route("/naver", methods=["POST"])
def set_naver_settings():
    """Set Naver API Client ID/Secret"""
    try:
        data = request.json
        client_id = data.get("client_id", "").strip()
        client_secret = data.get("client_secret", "").strip()

        if not client_id or not client_secret:
            return jsonify({"success": False, "error": "Client ID and Secret are required"}), 400

        set_setting("naver_client_id", client_id)
        set_setting("naver_client_secret", client_secret)

        return jsonify({"success": True, "message": "Naver settings saved"})
    except Exception as e:
        print(f"Error setting Naver settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@settings_bp.route("/images", methods=["POST"])
def set_image_settings():
    """Set Unsplash and Pixabay API keys"""
    try:
        data = request.json
        unsplash_key = data.get("unsplash_key", "").strip()
        pixabay_key = data.get("pixabay_key", "").strip()

        if unsplash_key:
            set_setting("unsplash_key", unsplash_key)
        if pixabay_key:
            set_setting("pixabay_key", pixabay_key)

        return jsonify({"success": True, "message": "Image settings saved"})
    except Exception as e:
        print(f"Error setting image settings: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@settings_bp.route("/blog", methods=["POST"])
def set_blog_id():
    """Set Naver blog ID"""
    try:
        data = request.json
        blog_id = data.get("blog_id", "").strip()

        if not blog_id:
            return jsonify({"success": False, "error": "Blog ID is required"}), 400

        set_setting("naver_blog_id", blog_id)
        return jsonify({"success": True, "message": "Blog ID saved"})
    except Exception as e:
        print(f"Error setting blog ID: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@settings_bp.route("/naver/test", methods=["POST"])
def test_naver_api():
    """Test Naver API credentials by making a sample search"""
    try:
        # 먼저 저장된 credentials 확인
        client_id = get_setting("naver_client_id")
        client_secret = get_setting("naver_client_secret")

        print(f"[TEST] Client ID: {client_id}")
        print(f"[TEST] Client Secret: {'***' if client_secret else 'NOT SET'}")

        if not client_id or not client_secret:
            return jsonify({"success": False, "error": "Client ID or Secret not configured. Please save them first in settings."}), 400

        from services.naver_search import search_news

        try:
            print(f"[TEST] Attempting Naver API call with query='테스트'")
            results = search_news("테스트", display=1)
            print(f"[TEST] Naver API returned {len(results)} results")

            if results:
                return jsonify({"success": True, "message": "Naver API credentials are valid"})
            else:
                return jsonify({"success": False, "error": "Naver API returned no results"}), 400
        except Exception as api_error:
            import traceback
            print(f"[TEST] Naver API test error: {api_error}")
            print(f"[TEST] Traceback: {traceback.format_exc()}")
            return jsonify({"success": False, "error": f"API test failed: {str(api_error)}"}), 400
    except Exception as e:
        import traceback
        print(f"[TEST] Error testing Naver API: {e}")
        print(f"[TEST] Traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500
