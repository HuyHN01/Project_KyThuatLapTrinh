 # MusicWebApp/run.py
from app import create_app, db # Import hàm create_app và instance db từ package app
from app.models import Song    # Import model Song (và các model khác nếu có sau này)

# Tạo instance ứng dụng Flask bằng cách gọi application factory
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Cung cấp context cho Flask shell.
    Cho phép bạn truy cập db và các model trực tiếp trong `flask shell` mà không cần import.
    """
    return {'db': db, 'Song': Song}

if __name__ == '__main__':
    # Chạy ứng dụng Flask development server
    # debug=True sẽ tự động reload server khi có thay đổi code và hiển thị traceback lỗi chi tiết hơn.
    # KHÔNG BAO GIỜ dùng debug=True trong môi trường production.
    app.run(debug=True)
