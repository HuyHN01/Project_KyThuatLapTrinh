
# MusicWebApp/config.py
import os
from urllib.parse import quote_plus
# Lấy đường dẫn thư mục gốc của dự án
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'keSPH42aN0WZlR3' # Rất quan trọng: Thay đổi key này!

    # Cấu hình SQLAlchemy cho SQL Server với pyodbc
    # =====================================================================

    # **LỰA CHỌN 1: SỬ DỤNG WINDOWS AUTHENTICATION (XÁC THỰC WINDOWS)**
    # Đây là cách phổ biến nếu bạn đang phát triển trên máy Windows cá nhân
    # và SQL Server của bạn được cài đặt để cho phép Windows Authentication.
    # SQL Server sẽ sử dụng tài khoản Windows hiện tại của bạn để kết nối.

    DB_DRIVER_NAME = 'ODBC Driver 18 for SQL Server' # Hoặc một driver khác bạn đã cài, ví dụ: '{SQL Server Native Client 11.0}' hoặc đơn giản là '{SQL Server}'
                                                # Kiểm tra tên driver chính xác trong "ODBC Data Source Administrator" trên máy của bạn.
    DB_SERVER = 'MyHLaptop'                  # Tên Server của bạn như trong SSMS.
                                                # Nếu là instance mặc định, chỉ cần tên server.
                                                # Nếu là named instance, ví dụ: 'MYHAI-LAPTOP\SQLEXPRESS'
    DB_DATABASE = 'MyMusicAppDB'                # Tên cơ sở dữ liệu bạn muốn tạo hoặc sử dụng.
                                                # Bạn cần TỰ TẠO database này TRƯỚC trong SSMS nếu nó chưa tồn tại.
                                                # Hoặc, một số cấu hình có thể cho phép tạo nếu chưa có, nhưng an toàn hơn là tạo trước.

    # Encode tên driver để sử dụng trong URI
    ENCODED_DB_DRIVER = quote_plus(DB_DRIVER_NAME) # <<-- ĐỊNH NGHĨA BIẾN NÀY Ở ĐÂY

    SQLALCHEMY_DATABASE_URI = (
        f'mssql+pyodbc://@{DB_SERVER}/{DB_DATABASE}'
        f'?driver={ENCODED_DB_DRIVER}'
        f'&Trusted_Connection=yes'
        f'&Encrypt=no' # <<-- THÊM THAM SỐ NÀY
    )
    # Chú ý: DB_DRIVER.replace(" ", "+") để thay thế khoảng trắng bằng dấu '+' cho URL.

    # **LỰA CHỌN 2: SỬ DỤNG SQL SERVER AUTHENTICATION (XÁC THỰC SQL SERVER)**
    # Bạn cần tạo một user login riêng trong SQL Server và cấp quyền cho user đó trên database.

    # DB_DRIVER_SQLAUTH = '{ODBC Driver 17 for SQL Server}'
    # DB_SERVER_SQLAUTH = 'MYHAI-LAPTOP'
    # DB_DATABASE_SQLAUTH = 'MyMusicAppDB' # Tên database
    # DB_USERNAME_SQLAUTH = 'your_sql_server_username' # Tên đăng nhập SQL Server bạn đã tạo
    # DB_PASSWORD_SQLAUTH = 'your_sql_server_password' # Mật khẩu của user đó

    # SQLALCHEMY_DATABASE_URI = (
    #    f'mssql+pyodbc://{DB_USERNAME_SQLAUTH}:{DB_PASSWORD_SQLAUTH}'
    #    f'@{DB_SERVER_SQLAUTH}/{DB_DATABASE_SQLAUTH}'
    #    f'?driver={DB_DRIVER_SQLAUTH.replace(" ", "+")}'
    # )

    # =====================================================================

    SQLALCHEMY_TRACK_MODIFICATIONS = False # Tắt thông báo không cần thiết của SQLAlchemy

    # Các cấu hình khác (nếu có)
    # ví dụ: cấu hình mail, ...
