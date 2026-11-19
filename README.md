# NN SUNWIN VIP API

## Lưu ý quan trọng
Máy chủ riêng này chỉ chuyển tiếp và chuẩn hóa dữ liệu từ một API nguồn hợp lệ.
Nó KHÔNG tự truy cập Sunwin, không đăng nhập tài khoản và không tạo ra xúc xắc.
Nếu chưa có `SOURCE_API_URL` hoạt động, API sẽ báo `not_configured` hoặc `error`,
không bịa dữ liệu.

Không nhập mật khẩu, cookie, OTP hay token tài khoản vào cấu hình.

## Chạy thử
1. Cài Python 3.10 trở lên.
2. `pip install -r requirements.txt`
3. Đặt biến môi trường `SOURCE_API_URL` thành URL API nguồn mà bạn có quyền sử dụng.
4. Chạy `python app.py`.
5. Mở `/api/taixiu/sunwin`.

## Đưa lên Render
1. Đưa các file trong ZIP lên một GitHub repository.
2. Trên Render, tạo Web Service từ repository đó.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Trong Environment, thêm `SOURCE_API_URL` và nhập URL API nguồn hợp lệ.
6. Nếu chưa có URL nguồn, để trống; dịch vụ vẫn chạy nhưng không có dữ liệu phiên.

## Dữ liệu API trả về
`source_status`, `message`, `updated_at`, `result`, `history`.
Khi có dữ liệu, `result` gồm `session`, `dice`, `total`, `outcome`, `received_at`.

Lưu ý: Tài/Xỉu là kết quả ngẫu nhiên; lịch sử không đảm bảo dự đoán chính xác.
