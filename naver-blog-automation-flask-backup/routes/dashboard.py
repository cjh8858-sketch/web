from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
    """Main dashboard page"""
    return render_template("index.html")

@dashboard_bp.route("/settings")
def settings():
    """Settings page for API keys and blog ID"""
    return render_template("settings.html")

@dashboard_bp.route("/history")
def history():
    """Publishing history page"""
    return render_template("history.html")
