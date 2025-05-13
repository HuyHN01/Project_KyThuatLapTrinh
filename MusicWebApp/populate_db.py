# MusicWebApp/populate_db.py
import sys
import os

# Thêm thư mục gốc của dự án vào sys.path để có thể import 'app' và 'api_clients'
# Điều này hữu ích khi chạy script này độc lập.
# Nếu cấu trúc thư mục của bạn khác, hãy điều chỉnh đường dẫn này.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db  # Import từ package app (app/__init__.py)
from app.models import Song     # Import model Song
from api_clients.jamendo_client import search_tracks, JAMENDO_CLIENT_ID # Import hàm và Client ID

# Tạo một instance ứng dụng Flask và đẩy application context
# Điều này cần thiết để SQLAlchemy (db.session) và các extension khác của Flask
# hoạt động đúng cách khi chạy script này bên ngoài một HTTP request.
app = create_app()
app_context = app.app_context()
app_context.push()

def populate_songs_from_jamendo_api(search_queries, tracks_per_query=10):
    """
    Lấy dữ liệu bài hát từ Jamendo API dựa trên danh sách từ khóa tìm kiếm
    và lưu vào cơ sở dữ liệu.

    Args:
        search_queries (list): Danh sách các chuỗi từ khóa tìm kiếm.
        tracks_per_query (int): Số lượng bài hát tối đa muốn lấy cho mỗi từ khóa.
    """
    if not JAMENDO_CLIENT_ID or JAMENDO_CLIENT_ID == 'YOUR_ACTUAL_JAMENDO_CLIENT_ID':
        print("LỖI: JAMENDO_CLIENT_ID chưa được cấu hình trong api_clients/jamendo_client.py.")
        print("Vui lòng cập nhật Client ID thực tế của bạn.")
        return

    print("Bắt đầu quá trình lấy và lưu dữ liệu từ Jamendo API...")
    total_songs_added_overall = 0

    for query in search_queries:
        print(f"\nĐang xử lý từ khóa tìm kiếm: '{query}' (lấy tối đa {tracks_per_query} bài hát)")

        # Gọi hàm search_tracks từ jamendo_client
        # Bạn có thể tùy chỉnh các tham số khác như 'order', 'imagesize' nếu muốn
        tracks_data_from_api = search_tracks(query, limit=tracks_per_query, order='popularity_week')

        if not tracks_data_from_api:
            print(f"  Không tìm thấy bài hát nào hoặc có lỗi khi lấy dữ liệu cho từ khóa '{query}'.")
            continue

        songs_added_for_this_query = 0
        for track_data in tracks_data_from_api:
            # Kiểm tra xem bài hát đã tồn tại trong CSDL chưa dựa trên source_url (link Jamendo)
            # hoặc jamendo_id nếu bạn quyết định lưu jamendo_id vào model Song và tạo index cho nó.
            # Hiện tại model Song có source_url là unique.

            source_url = track_data.get('source_url')
            if not source_url:
                print(f"  Bỏ qua bài hát '{track_data.get('title')}' vì thiếu source_url.")
                continue

            existing_song = Song.query.filter_by(source_url=source_url).first()

            if existing_song:
                print(f"  Bài hát '{track_data.get('title')}' (Nguồn: {source_url}) đã tồn tại trong CSDL. Bỏ qua.")
                continue

            # Tạo đối tượng Song mới để lưu vào CSDL
            # Đảm bảo các trường bạn lấy từ track_data khớp với các trường trong model Song
            new_song = Song(
                title=track_data.get('title'),
                artist=track_data.get('artist_name'),
                album=track_data.get('album_name'),
                genre=track_data.get('genre'),
                image_url=track_data.get('image_url'),
                stream_url=track_data.get('stream_url'), # Rất quan trọng
                source_url=source_url
                # crawled_at sẽ tự động được thêm do có default=datetime.utcnow trong model Song
            )
            db.session.add(new_song)
            songs_added_for_this_query += 1
            print(f"  Đã chuẩn bị thêm: '{new_song.title}' bởi {new_song.artist}")

        if songs_added_for_this_query > 0:
            try:
                db.session.commit() # Lưu tất cả các bài hát mới của query này vào CSDL
                print(f"  => Đã thêm thành công {songs_added_for_this_query} bài hát mới cho từ khóa '{query}' vào CSDL.")
                total_songs_added_overall += songs_added_for_this_query
            except Exception as e:
                db.session.rollback() # Hoàn tác các thay đổi trong session nếu có lỗi khi commit
                print(f"  LỖI khi commit vào CSDL cho từ khóa '{query}': {e}")
                # Bạn có thể muốn ghi log chi tiết lỗi ở đây
        else:
            print(f"  Không có bài hát mới nào được thêm vào CSDL cho từ khóa '{query}'.")

    print(f"\n===== HOÀN TẤT QUÁ TRÌNH POPULATE DATABASE =====")
    print(f"Tổng cộng đã thêm {total_songs_added_overall} bài hát mới vào cơ sở dữ liệu.")

if __name__ == '__main__':
    # Danh sách các từ khóa tìm kiếm bạn muốn sử dụng để lấy dữ liệu ban đầu
    # Hãy chọn các từ khóa đa dạng để có bộ dữ liệu phong phú hơn
    initial_search_queries = [
        "lofi hip hop",
        "acoustic chill",
        "upbeat pop electronic",
        "relaxing piano solo",
        "indie folk playlist",
        "cinematic trailer score",
        "epic fantasy music",
        "ambient space"
    ]

    # Số lượng bài hát muốn lấy cho mỗi từ khóa
    num_tracks_per_query = 5 # Bắt đầu với số lượng nhỏ để kiểm tra, có thể tăng sau

    print("Khởi chạy script để populate cơ sở dữ liệu từ Jamendo API...")
    populate_songs_from_jamendo_api(initial_search_queries, num_tracks_per_query)
    print("Script populate_db.py đã chạy xong.")

    # Quan trọng: Pop application context sau khi hoàn tất
    # Mặc dù script sẽ kết thúc, nhưng đây là thực hành tốt.
    app_context.pop()
