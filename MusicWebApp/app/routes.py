# MusicWebApp/app/routes.py (hoặc app/main_routes.py)
from flask import Blueprint, render_template, request
from .models import Song # Import model Song
# Nếu db được khởi tạo trong __init__.py và bạn cần dùng session trực tiếp (ít khi cần cho query)
# from . import db

# Giữ nguyên tên blueprint là 'main_routes' để url_for trong base_layout.html hoạt động
main_bp = Blueprint('main_routes', __name__,
                    template_folder='../templates') # Đảm bảo trỏ đúng đến thư mục templates của app
                                                    # Nếu routes.py và templates/ cùng trong app/, thì có thể là 'templates'
                                                    # Hoặc không cần nếu Flask tự tìm thấy (thường là vậy)

@main_bp.route('/')
@main_bp.route('/index')
@main_bp.route('/songs') # Thêm route /songs cho rõ ràng
def index():
    # Lấy tất cả các bài hát từ CSDL
    # Sắp xếp theo thời gian được crawl gần nhất (crawled_at giảm dần)
    # Hoặc bạn có thể sắp xếp theo tiêu chí khác, ví dụ: Song.title
    try:
        songs_from_db = Song.query.order_by(Song.crawled_at.desc()).all()
        # Dòng debug để kiểm tra xem có lấy được bài hát không
        print(f"Tìm thấy {len(songs_from_db)} bài hát trong CSDL.")
        # if songs_from_db:
        #     print(f"Bài hát đầu tiên: {songs_from_db[0].title}")
    except Exception as e:
        print(f"Lỗi khi truy vấn CSDL: {e}")
        songs_from_db = [] # Trả về danh sách rỗng nếu có lỗi

    # Truyền danh sách bài hát vào template 'song_list.html'
    # Template này sẽ nằm trong MusicWebApp/app/templates/song_list.html
    return render_template('song_list.html',
                           title="Trang Chủ - Tất Cả Bài Hát",
                           songs=songs_from_db)

# Route cho tìm kiếm (sẽ làm chi tiết hơn ở Công việc 3.3)
@main_bp.route('/search')
def search():
    query_param = request.args.get('query', '')

    if query_param:
        search_term = f'%{query_param}%' # Thêm ký tự đại diện cho ilike
        search_results = Song.query.filter(
            (Song.title.ilike(search_term)) |
            (Song.artist.ilike(search_term))
        ).order_by(Song.title).all()
        print(f"Tìm kiếm cho '{query_param}', tìm thấy {len(search_results)} kết quả.")
    else:
        search_results = []
        print("Không có từ khóa tìm kiếm, trả về danh sách rỗng.")

    # Sử dụng cùng template song_list.html để hiển thị kết quả tìm kiếm
    return render_template('song_list.html',
                           title=f"Kết quả tìm kiếm cho: '{query_param}'" if query_param else "Tìm Kiếm",
                           songs=search_results,
                           search_query=query_param)

# >>> THÊM ROUTE NÀY <<<
@main_bp.route('/play/<int:song_id>')
def play_song(song_id):
    # Tạm thời, route này chỉ lấy thông tin bài hát và có thể render một template đơn giản
    # Hoặc chỉ trả về một thông báo. Mục đích chính là để url_for không bị lỗi.
    song = Song.query.get_or_404(song_id) # Lấy bài hát hoặc trả về lỗi 404 nếu không tìm thấy

    # Bạn sẽ tạo template music_player_page.html ở Công việc 3.4
    # Tạm thời, có thể render một placeholder hoặc chỉ trả về tên bài hát
    # return f"Sẽ phát bài hát: {song.title} - {song.artist}"
    return render_template('music_player_placeholder.html', song=song, title=f"Đang phát: {song.title}")
