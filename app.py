import os
import sys
import uuid
import json
import queue
import threading
import openpyxl
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from mark_as_paid import get_access_token, find_order_id, mark_as_paid as shopify_mark_paid

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# session_id -> {"order_numbers": [...], "filename": str, "q": Queue|None}
_sessions: dict = {}
_sessions_lock = threading.Lock()

UPLOAD_DIR = os.path.join(BASE_DIR, "_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Pages ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ── Upload: parse xlsx files, return preview JSON list ────────────────────────

@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("file")
    results = []

    for f in files:
        if not f or not f.filename:
            continue
        if not f.filename.lower().endswith(".xlsx"):
            return jsonify({"error": f"File '{f.filename}' is not a .xlsx file. Only .xlsx files are supported."}), 400

        tmp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}.xlsx")
        f.save(tmp_path)

        try:
            wb = openpyxl.load_workbook(tmp_path, read_only=True, data_only=True)
            ws = wb.active

            headers = None
            order_id_col = None
            rows = []
            order_numbers = []

            for row in ws.iter_rows(values_only=True):
                if headers is None:
                    headers = [str(c).strip() if c is not None else "" for c in row]
                    for idx, h in enumerate(headers):
                        if h.lower() == "orderid":
                            order_id_col = idx
                            break
                    if order_id_col is None:
                        return jsonify({"error": f"No 'OrderId' column found in file '{f.filename}'. Check your column headers."}), 400
                    continue

                row_vals = [str(v) if v is not None else "" for v in row]
                rows.append(row_vals)

                val = row[order_id_col]
                if val is not None and str(val).strip():
                    order_numbers.append(str(val).strip())

            wb.close()

            # Deduplicate preserving order
            seen: set = set()
            unique_orders = []
            for n in order_numbers:
                if n not in seen:
                    seen.add(n)
                    unique_orders.append(n)

            session_id = uuid.uuid4().hex
            with _sessions_lock:
                _sessions[session_id] = {
                    "order_numbers": unique_orders,
                    "filename": f.filename,
                    "q": None,
                }

            results.append({
                "session_id": session_id,
                "filename": f.filename,
                "headers": headers,
                "rows": rows[:50],        # preview cap
                "total_rows": len(rows),
                "order_count": len(unique_orders),
                "order_id_col": order_id_col,
            })

        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    if not results:
        return jsonify({"error": "No valid files were uploaded."}), 400

    return jsonify(results)

# ── Remove: delete a file session from cache ─────────────────────────────────

@app.route("/api/remove", methods=["POST"])
def remove_session():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    with _sessions_lock:
        if session_id in _sessions:
            del _sessions[session_id]
            return jsonify({"ok": True})
    return jsonify({"error": "Session not found"}), 404

# ── Process: start background thread ─────────────────────────────────────────

@app.route("/api/process", methods=["POST"])
def process():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")

    with _sessions_lock:
        session = _sessions.get(session_id)

    if not session:
        return jsonify({"error": "Invalid or expired session"}), 400
    if session.get("q") is not None:
        return jsonify({"error": "Already processing"}), 400

    q: queue.Queue = queue.Queue()
    with _sessions_lock:
        _sessions[session_id]["q"] = q

    order_numbers = session["order_numbers"]

    def run():
        def emit(evt_type, **kwargs):
            q.put({"type": evt_type, **kwargs})

        try:
            emit("log", level="info", message="Obtaining Shopify access token...")
            token = get_access_token()
            emit("log", level="success", message="Access token obtained")
            emit("log", level="info", message=f"Processing {len(order_numbers)} order(s)...")
            emit("separator")

            totals = {"success": 0, "already_paid": 0, "not_found": 0, "error": 0}

            for order_number in order_numbers:
                emit("log", level="info", message=f"Order #{order_number}")
                try:
                    gid, status = find_order_id(token, order_number)

                    if gid is None:
                        emit("log", level="warning", message="  Not found in Shopify")
                        totals["not_found"] += 1
                        continue

                    if status == "PAID":
                        emit("log", level="muted", message="  Already PAID — skipped")
                        totals["already_paid"] += 1
                        continue

                    resp = shopify_mark_paid(token, gid)
                    errors = (
                        resp.get("data", {})
                        .get("orderMarkAsPaid", {})
                        .get("userErrors", [])
                    )

                    if errors:
                        msgs = "; ".join(e["message"] for e in errors)
                        emit("log", level="error", message=f"  Error: {msgs}")
                        totals["error"] += 1
                    else:
                        emit("log", level="success", message="  Marked as PAID")
                        totals["success"] += 1

                except Exception as exc:
                    emit("log", level="error", message=f"  Exception: {exc}")
                    totals["error"] += 1

            emit("separator")
            emit("summary", **totals)
            emit("done")

        except Exception as exc:
            emit("log", level="error", message=f"Fatal error: {exc}")
            emit("done")

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"ok": True})

# ── Stream: SSE endpoint ──────────────────────────────────────────────────────

@app.route("/api/stream/<session_id>")
def stream(session_id):
    def generate():
        import time
        # Wait up to 10 s for the process endpoint to attach a queue
        deadline = time.time() + 10
        q = None
        while time.time() < deadline:
            with _sessions_lock:
                s = _sessions.get(session_id)
                if s and s.get("q"):
                    q = s["q"]
                    break
            time.sleep(0.1)

        if q is None:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found'})}\n\n"
            return

        while True:
            try:
                event = q.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") == "done":
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Shopify COD Dashboard")
    print("  Open -> http://localhost:8080\n")
    app.run(debug=True, threaded=True, port=8080)
