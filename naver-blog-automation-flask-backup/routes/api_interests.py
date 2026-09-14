from flask import Blueprint, request, jsonify
from db import get_db_connection

interests_bp = Blueprint("interests", __name__, url_prefix="/api/interests")

@interests_bp.route("", methods=["GET"])
def get_interests():
    """Get all interests with their schedules"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, keyword, active, created_at FROM interests ORDER BY created_at DESC")
        interests = cursor.fetchall()

        result = []
        for interest in interests:
            cursor.execute(
                "SELECT id, run_hour, run_minute, enabled, last_run_at FROM schedules WHERE interest_id = ?",
                (interest["id"],)
            )
            schedule = cursor.fetchone()

            result.append({
                "id": interest["id"],
                "keyword": interest["keyword"],
                "active": interest["active"],
                "created_at": interest["created_at"],
                "schedule": {
                    "id": schedule["id"],
                    "run_hour": schedule["run_hour"],
                    "run_minute": schedule["run_minute"],
                    "enabled": schedule["enabled"],
                    "last_run_at": schedule["last_run_at"]
                } if schedule else None
            })

        conn.close()
        return jsonify({"success": True, "data": result})
    except Exception as e:
        print(f"Error fetching interests: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@interests_bp.route("", methods=["POST"])
def create_interest():
    """Create new interest with schedule"""
    try:
        data = request.json
        keyword = data.get("keyword", "").strip()
        run_hour = data.get("run_hour", 9)
        run_minute = data.get("run_minute", 0)

        if not keyword:
            return jsonify({"success": False, "error": "Keyword is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Create interest
        cursor.execute("INSERT INTO interests (keyword, active) VALUES (?, 1)", (keyword,))
        interest_id = cursor.lastrowid

        # Create schedule
        cursor.execute(
            "INSERT INTO schedules (interest_id, run_hour, run_minute, enabled) VALUES (?, ?, ?, 1)",
            (interest_id, run_hour, run_minute)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "data": {
                "id": interest_id,
                "keyword": keyword,
                "active": 1,
                "schedule": {
                    "run_hour": run_hour,
                    "run_minute": run_minute,
                    "enabled": 1
                }
            }
        }), 201
    except Exception as e:
        print(f"Error creating interest: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@interests_bp.route("/<int:interest_id>", methods=["PUT"])
def update_interest(interest_id):
    """Update interest and schedule"""
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update schedule if provided
        if "run_hour" in data or "run_minute" in data:
            run_hour = data.get("run_hour")
            run_minute = data.get("run_minute")
            enabled = data.get("enabled", 1)

            cursor.execute(
                "UPDATE schedules SET run_hour = ?, run_minute = ?, enabled = ? WHERE interest_id = ?",
                (run_hour, run_minute, enabled, interest_id)
            )

        conn.commit()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error updating interest: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@interests_bp.route("/<int:interest_id>", methods=["DELETE"])
def delete_interest(interest_id):
    """Delete interest and its schedule"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete schedule first
        cursor.execute("DELETE FROM schedules WHERE interest_id = ?", (interest_id,))

        # Delete publish history
        cursor.execute("DELETE FROM publish_history WHERE interest_id = ?", (interest_id,))

        # Delete interest
        cursor.execute("DELETE FROM interests WHERE id = ?", (interest_id,))

        conn.commit()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error deleting interest: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
