"""MoneyAgent API Server — Flask REST API"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"

app = Flask(__name__, static_folder=None)
CORS(app)


def _read_json(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/api/status")
def api_status():
    return jsonify({
        "running": True,
        "status": "running",
        "last_updated": datetime.now().isoformat(),
    })


@app.route("/api/ledger")
def api_ledger():
    ledger = _read_json("ledger.json")
    months = ledger.get("months", {})
    current = datetime.now().strftime("%Y-%m")
    month_data = months.get(current, {"income": [], "expenses": []})

    total_income = sum(i.get("amount", 0) for i in month_data.get("income", []))
    total_expense = sum(e.get("amount", 0) for e in month_data.get("expenses", []))

    return jsonify({
        "month": current,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_profit": total_income - total_expense,
        "income_details": month_data.get("income", []),
        "expense_details": month_data.get("expenses", []),
    })


@app.route("/api/ledger/history")
def api_ledger_history():
    ledger = _read_json("ledger.json")
    months = ledger.get("months", {})
    history = []
    for month, data in sorted(months.items()):
        income = sum(i.get("amount", 0) for i in data.get("income", []))
        expense = sum(e.get("amount", 0) for e in data.get("expenses", []))
        history.append({
            "month": month, "income": income,
            "expense": expense, "profit": income - expense,
        })
    return jsonify(history)


@app.route("/api/channels")
def api_channels():
    return jsonify([
        {"id": "github_sponsors", "name": "GitHub Sponsors", "enabled": True, "revenue": 0},
        {"id": "medium", "name": "Medium", "enabled": False, "revenue": 0},
        {"id": "kofi", "name": "Ko-fi", "enabled": False, "revenue": 0},
        {"id": "twitter", "name": "X/Twitter", "enabled": False, "revenue": 0},
    ])


@app.route("/api/evolution")
def api_evolution():
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-20", "--format=%h|%s|%ai|%an"],
            cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=5
        )
        logs = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 3)
                logs.append({
                    "hash": parts[0], "message": parts[1] if len(parts) > 1 else "",
                    "date": parts[2] if len(parts) > 2 else "",
                    "author": parts[3] if len(parts) > 3 else "",
                })
        return jsonify(logs)
    except Exception:
        return jsonify([])


@app.route("/api/notifications")
def api_notifications():
    notifs = _read_json("notifications.json")
    if isinstance(notifs, dict):
        notifs = []
    return jsonify(notifs)


@app.route("/api/resources")
def api_resources():
    try:
        import psutil
        return jsonify({
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_mb": psutil.virtual_memory().used / 1024 / 1024,
            "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024,
            "disk_gb": psutil.disk_usage(str(PROJECT_DIR)).used / 1024 / 1024 / 1024,
            "disk_total_gb": psutil.disk_usage(str(PROJECT_DIR)).total / 1024 / 1024 / 1024,
        })
    except Exception:
        return jsonify({"cpu_percent": 0, "memory_mb": 0, "disk_gb": 0})


@app.route("/api/payment/<payment_id>", methods=["PUT"])
def api_approve_payment(payment_id):
    data = request.get_json() or {}
    status = data.get("status", "approved")
    path = DATA_DIR / "payment_requests.json"
    if path.exists():
        with open(path, "r") as f:
            requests = json.load(f)
        for req in requests:
            if req.get("id") == payment_id:
                req["status"] = status
        with open(path, "w") as f:
            json.dump(requests, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True, "id": payment_id, "status": status})


# 生产模式: serve React 静态文件
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path=""):
    frontend_dist = PROJECT_DIR / "frontend" / "dist"
    if not (frontend_dist / "index.html").exists():
        return jsonify({"error": "Frontend not built. Run: cd frontend && npm run build"}), 404
    if path and (frontend_dist / path).exists():
        return send_from_directory(str(frontend_dist), path)
    return send_from_directory(str(frontend_dist), "index.html")


if __name__ == "__main__":
    print("MoneyAgent API Server starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
