import os
import threading
import time
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Chỉ nhập URL API dữ liệu mà bạn có quyền sử dụng.
# Không điền mật khẩu, cookie, OTP hoặc token tài khoản Sunwin.
SOURCE_API_URL = os.getenv("SOURCE_API_URL", "").strip()
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "10"))

state = {
    "source_status": "not_configured",
    "message": "Chưa cấu hình API nguồn dữ liệu.",
    "updated_at": None,
    "result": None,
    "history": [],
}

def classify(total):
    # Quy tắc Tài/Xỉu phổ biến cho 3 xúc xắc: 4–10 Xỉu, 11–17 Tài.
    # Bộ ba (1-1-1 hoặc 6-6-6) được đánh dấu riêng.
    if total in (3, 18):
        return "Bộ ba"
    return "Tài" if 11 <= total <= 17 else "Xỉu"

def fetch_source():
    if not SOURCE_API_URL:
        state.update(source_status="not_configured",
                     message="Chưa có URL API nguồn hợp lệ.")
        return
    try:
        response = requests.get(SOURCE_API_URL, timeout=8)
        response.raise_for_status()
        data = response.json()

        # Hỗ trợ các tên trường trong đoạn code người dùng đã gửi.
        session = data.get("phien", data.get("Phiên"))
        dice = [
            data.get("xuc_xac_1", data.get("Xúc_xắc_1")),
            data.get("xuc_xac_2", data.get("Xúc_xắc_2")),
            data.get("xuc_xac_3", data.get("Xúc_xắc_3")),
        ]
        if session is None or any(v is None for v in dice):
            raise ValueError("API nguồn không trả đủ phiên và 3 xúc xắc.")

        dice = [int(v) for v in dice]
        if any(v < 1 or v > 6 for v in dice):
            raise ValueError("Giá trị xúc xắc ngoài khoảng 1–6.")
        total = sum(dice)
        result = {
            "session": session,
            "dice": dice,
            "total": total,
            "outcome": classify(total),
            "received_at": datetime.now(timezone.utc).isoformat(),
        }

        # Chỉ thêm lịch sử khi phiên thay đổi.
        if not state["result"] or str(state["result"]["session"]) != str(session):
            state["history"].insert(0, result)
            del state["history"][100:]
        state.update(source_status="ok", message="Đã nhận dữ liệu từ API nguồn.",
                     updated_at=result["received_at"], result=result)
    except Exception as exc:
        state.update(source_status="error",
                     message=f"Không lấy được dữ liệu nguồn: {exc}")

def updater():
    while True:
        fetch_source()
        time.sleep(max(5, POLL_SECONDS))

@app.get("/")
def home():
    return jsonify({"name": "NN SUNWIN VIP API", "status": "running"})

@app.get("/api/taixiu/sunwin")
def taixiu():
    return jsonify(state)

@app.get("/health")
def health():
    return jsonify({"status": "running", "source_status": state["source_status"]})

if __name__ == "__main__":
    threading.Thread(target=updater, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
