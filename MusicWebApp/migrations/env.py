# MusicWebApp/migrations/env.py
import logging
from logging.config import fileConfig

from flask import current_app # Dùng để lấy config từ app Flask

from alembic import context

# Thêm các dòng import này để Alembic có thể tìm thấy model của bạn:
import os
import sys
# Thêm đường dẫn của thư mục gốc dự án (MusicWebApp) vào sys.path
# Điều này cho phép import 'app' từ thư mục migrations
# Giả sử env.py nằm trong MusicWebApp/migrations/, '..' sẽ trỏ về MusicWebApp/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import instance db từ app/__init__.py (nơi bạn đã khởi tạo SQLAlchemy)
# và import tất cả các model từ app/models.py
# Đảm bảo rằng `app.db` là instance SQLAlchemy của bạn nếu bạn đặt tên khác.
# Nếu bạn khởi tạo db trực tiếp trong app/__init__.py (ví dụ: from app import db), thì dùng cách đó.
# Dựa trên cấu trúc bạn đã làm, chúng ta sẽ import db từ 'app'
from app import db as target_db_instance # Đổi tên thành target_db_instance để rõ ràng
# Import tất cả các model để chúng được đăng ký với metadata của target_db_instance
from app.models import * # Điều này sẽ import model Song (và các model khác nếu có)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine_url():
    """Lấy URL CSDL từ cấu hình ứng dụng Flask hiện tại."""
    try:
        # Cố gắng lấy URL từ current_app, đây là cách Flask-Migrate thường làm
        return current_app.config['SQLALCHEMY_DATABASE_URI'].replace('%', '%%')
    except Exception:
        # Nếu không có current_app (ví dụ: chạy alembic offline không có context Flask),
        # thử đọc trực tiếp từ alembic.ini (cần cấu hình sqlalchemy.url trong alembic.ini)
        # Hoặc bạn có thể hardcode nếu cần cho mục đích cụ thể, nhưng không khuyến nghị.
        # Đối với Flask-Migrate, nó sẽ đảm bảo current_app có sẵn.
        # Nếu vẫn lỗi, kiểm tra lại cách bạn gọi lệnh flask.
        return None


# Thiết lập sqlalchemy.url từ cấu hình ứng dụng Flask
# Điều này đảm bảo Alembic sử dụng cùng CSDL với ứng dụng Flask của bạn
db_url = get_engine_url()
if db_url:
    config.set_main_option('sqlalchemy.url', db_url)
else:
    logger.warning("Could not determine database URL from Flask app config for Alembic.")


# target_metadata nên trỏ đến metadata của instance SQLAlchemy từ ứng dụng của bạn
target_metadata = target_db_instance.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Sử dụng engine từ current_app nếu có thể (được khuyến nghị bởi Flask-Migrate)
    connectable = current_app.extensions['migrate'].db.get_engine()

    with connectable.connect() as connection:
        # Lấy configure_args từ extension Flask-Migrate
        # và thiết lập process_revision_directives nếu chưa có
        conf_args = current_app.extensions['migrate'].configure_args
        if conf_args.get("process_revision_directives") is None:
            def process_revision_directives(context, revision, directives):
                if getattr(config.cmd_opts, 'autogenerate', False):
                    script = directives[0]
                    if script.upgrade_ops.is_empty():
                        directives[:] = []
                        logger.info('No changes in schema detected.')
            conf_args["process_revision_directives"] = process_revision_directives

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            **conf_args # Truyền các đối số cấu hình từ Flask-Migrate
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
