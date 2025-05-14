 # MusicWebApp/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config # Import lớp Config từ file config.py ở thư mục gốc

# Khởi tạo các extension mà không gắn liền với app cụ thể ngay lập tức
# Chúng sẽ được gắn với app bên trong hàm create_app (Application Factory pattern)
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Hàm tạo ứng dụng (Application Factory).
    Giúp tạo nhiều instance của ứng dụng với các cấu hình khác nhau nếu cần (ví dụ: cho testing).
    """
    app = Flask(__name__, instance_relative_config=True) # instance_relative_config=True cho phép load config từ thư mục instance/

    # Load cấu hình từ đối tượng Config
    app.config.from_object(config_class)

    # (Tùy chọn) Load thêm cấu hình từ file trong thư mục instance/ nếu có (ví dụ: instance/config.py)
    # File này có thể chứa các thông tin nhạy cảm và không nên đưa lên Git.
    # app.config.from_pyfile('config.py', silent=True) # silent=True để không báo lỗi nếu file không tồn tại

    # Khởi tạo các extension với ứng dụng Flask
    db.init_app(app)
    migrate.init_app(app, db) # Flask-Migrate cần cả app và db

    # Đăng ký Blueprints (nếu có) sẽ được thực hiện ở đây
    from .routes import main_bp # Hoặc from .main_routes import main_bp nếu bạn tạo file riêng
    app.register_blueprint(main_bp)

    # (Tùy chọn) Thêm 'now' vào biến toàn cục của Jinja
    from datetime import datetime
    app.jinja_env.globals.update(now=datetime.utcnow)

    # Import các model ở đây để đảm bảo chúng được đăng ký với SQLAlchemy
    # trước khi các lệnh db (như migrate) được chạy từ bên ngoài.
    # Tuy nhiên, việc import này thường được xử lý tốt hơn trong run.py hoặc migrations/env.py
    # khi cần thiết cho context của Alembic. Tạm thời có thể chưa cần ở đây.
    # from . import models

    return app
