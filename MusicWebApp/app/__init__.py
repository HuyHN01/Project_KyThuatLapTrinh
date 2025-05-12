 # MusicWebApp/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate # Thêm dòng này
from config import Config

db = SQLAlchemy()
migrate = Migrate() # Thêm dòng này

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db) # Thêm dòng này, truyền cả app và db

    # Đăng ký Blueprints (sẽ làm ở các bước sau)
    # from app.routes import bp as main_bp # Ví dụ
    # app.register_blueprint(main_bp)

    # from app.auth_routes import auth_bp # Ví dụ
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
