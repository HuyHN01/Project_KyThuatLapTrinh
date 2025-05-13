import os
from urllib.parse import quote_plus # Dùng để encode tên driver nếu có khoảng trắng

# Lấy đường dẫn thư mục gốc của dự án một cách an toàn
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # SECRET_KEY cần thiết cho session, flash messages, và các tính năng bảo mật của Flask (ví dụ: CSRF với Flask-WTF)
    # Thay thế bằng một chuỗi ký tự ngẫu nhiên, phức tạp và giữ bí mật!
    # Bạn có thể tạo bằng: python -c 'import secrets; print(secrets.token_hex(16))'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'keSPH42aN0WZlR3' # THAY THẾ BẰNG KEY THỰC TẾ

    # --- Cấu hình SQLAlchemy cho SQL Server với pyodbc ---
    # Thay thế các giá trị này cho phù hợp với thiết lập SQL Server của bạn

    # Tên driver ODBC chính xác bạn đã xác định từ ODBC Data Source Administrator (tab Drivers)
    # Ví dụ: 'ODBC Driver 18 for SQL Server', 'ODBC Driver 17 for SQL Server', 'SQL Server Native Client 11.0'
    # KHÔNG BAO GỒM dấu ngoặc nhọn {} ở đây.
    DB_DRIVER_NAME = 'ODBC Driver 18 for SQL Server'  # <<-- KIỂM TRA VÀ THAY THẾ NẾU CẦN

    # Tên Server SQL của bạn (như bạn dùng để kết nối trong SSMS)
    # Ví dụ: 'MYHAI-LAPTOP', 'MYHAI-LAPTOP\SQLEXPRESS' (nếu là named instance)
    DB_SERVER = 'MyHLaptop'  # <<-- KIỂM TRA VÀ THAY THẾ BẰNG TÊN SERVER CỦA BẠN

    # Tên Database bạn đã tạo trong SQL Server
    DB_DATABASE = 'MyMusicAppDB'

    # Encode tên driver để đảm bảo an toàn khi đưa vào URL
    ENCODED_DB_DRIVER = quote_plus(DB_DRIVER_NAME)

    # Lựa chọn kết nối (Windows Authentication được khuyến nghị cho môi trường phát triển cục bộ trên Windows)
    # Nếu bạn dùng Windows Authentication:
    SQLALCHEMY_DATABASE_URI = (
        f'mssql+pyodbc://@{DB_SERVER}/{DB_DATABASE}'
        f'?driver={ENCODED_DB_DRIVER}'
        f'&Trusted_Connection=yes'  # Cho phép kết nối bằng tài khoản Windows hiện tại
        f'&Encrypt=no'              # Tắt SSL nếu server dùng self-signed cert và bạn gặp lỗi SSL
                                    # Nếu server yêu cầu SSL và bạn có cert đáng tin cậy, có thể đặt là yes
                                    # Hoặc dùng TrustServerCertificate=yes nếu server yêu cầu SSL nhưng cert không đáng tin
    )

    # Nếu bạn muốn dùng SQL Server Authentication (tạo user/password riêng trong SQL Server):
    # DB_USERNAME = 'your_sql_username'
    # DB_PASSWORD = 'your_sql_password_here'
    # SQLALCHEMY_DATABASE_URI = (
    #     f'mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}'
    #     f'@{DB_SERVER}/{DB_DATABASE}'
    #     f'?driver={ENCODED_DB_DRIVER}'
    #     f'&Encrypt=no' # Hoặc các tùy chọn SSL khác
    # )

    # Tắt thông báo không cần thiết của Flask-SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # (Tùy chọn) Các cấu hình khác cho ứng dụng của bạn có thể được thêm ở đây
    # ví dụ:
    # ITEMS_PER_PAGE = 10
