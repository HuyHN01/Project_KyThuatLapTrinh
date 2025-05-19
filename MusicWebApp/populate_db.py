import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db
from app.models import Song
from api_clients.jamendo_client import search_tracks, JAMENDO_CLIENT_ID

app = create_app()
app_context = app.app_context()
app_context.push()

def populate_songs_from_jamendo_api(search_queries, tracks_per_query=10):
    if not JAMENDO_CLIENT_ID or JAMENDO_CLIENT_ID == 'YOUR_ACTUAL_JAMENDO_CLIENT_ID':
        print("LỖI: JAMENDO_CLIENT_ID chưa được cấu hình trong api_clients/jamendo_client.py.")
        print("Vui lòng cập nhật Client ID thực tế của bạn.")
        return

    print("Bắt đầu quá trình lấy và lưu dữ liệu từ Jamendo API...")
    total_songs_added_overall = 0

    for query in search_queries:
        print(f"\nĐang xử lý từ khóa tìm kiếm: '{query}' (lấy tối đa {tracks_per_query} bài hát)")

        tracks_data_from_api = search_tracks(query, limit=tracks_per_query, order='popularity_week')

        if not tracks_data_from_api:
            print(f"  Không tìm thấy bài hát nào hoặc có lỗi khi lấy dữ liệu cho từ khóa '{query}'.")
            continue

        songs_added_for_this_query = 0
        for track_data in tracks_data_from_api:
            source_url = track_data.get('source_url')
            if not source_url:
                print(f"  Bỏ qua bài hát '{track_data.get('title')}' vì thiếu source_url.")
                continue

            existing_song = Song.query.filter_by(source_url=source_url).first()

            if existing_song:
                print(f"  Bài hát '{track_data.get('title')}' (Nguồn: {source_url}) đã tồn tại trong CSDL. Bỏ qua.")
                continue

            new_song = Song(
                title=track_data.get('title'),
                artist=track_data.get('artist_name'),
                album=track_data.get('album_name'),
                genre=track_data.get('genre'),
                image_url=track_data.get('image_url'),
                stream_url=track_data.get('stream_url'),
                source_url=source_url
            )
            db.session.add(new_song)
            songs_added_for_this_query += 1
            print(f"  Đã chuẩn bị thêm: '{new_song.title}' bởi {new_song.artist}")

        if songs_added_for_this_query > 0:
            try:
                db.session.commit()
                print(f"  => Đã thêm thành công {songs_added_for_this_query} bài hát mới cho từ khóa '{query}' vào CSDL.")
                total_songs_added_overall += songs_added_for_this_query
            except Exception as e:
                db.session.rollback()
                print(f"  LỖI khi commit vào CSDL cho từ khóa '{query}': {e}")
        else:
            print(f"  Không có bài hát mới nào được thêm vào CSDL cho từ khóa '{query}'.")

    print(f"\n===== HOÀN TẤT QUÁ TRÌNH POPULATE DATABASE =====")
    print(f"Tổng cộng đã thêm {total_songs_added_overall} bài hát mới vào cơ sở dữ liệu.")

if __name__ == '__main__':
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

    num_tracks_per_query = 5

    print("Khởi chạy script để populate cơ sở dữ liệu từ Jamendo API...")
    populate_songs_from_jamendo_api(initial_search_queries, num_tracks_per_query)
    print("Script populate_db.py đã chạy xong.")

    app_context.pop()
