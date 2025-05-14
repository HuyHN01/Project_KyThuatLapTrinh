# MusicWebApp/app/routes.py (Hoặc app/main_routes.py)
from flask import Blueprint, render_template, request, current_app # Thêm current_app
from .models import Song

main_bp = Blueprint('main_routes', __name__, template_folder='templates')

@main_bp.route('/')
@main_bp.route('/index')
@main_bp.route('/songs')
def index():
    """
    Hiển thị trang chủ với danh sách tất cả các bài hát, có phân trang.
    """
    # Lấy số trang từ query parameter 'page', mặc định là trang 1, kiểu integer
    page = request.args.get('page', 1, type=int)

    # Lấy số lượng item trên mỗi trang từ cấu hình (hoặc đặt giá trị cố định)
    # Bạn có thể thêm PER_PAGE = 10 vào file config.py
    # Hoặc đặt trực tiếp ở đây:
    per_page = current_app.config.get('SONGS_PER_PAGE', 10) # Lấy từ config hoặc mặc định 10

    try:
        # Sử dụng .paginate() thay vì .all()
        pagination = Song.query.order_by(Song.crawled_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        # pagination.items chứa danh sách các bài hát cho trang hiện tại
        songs_on_page = pagination.items

        print(f"Trang {page}: Đã lấy {len(songs_on_page)} bài hát từ CSDL (trên tổng số {pagination.total} bài).")
    except Exception as e:
        print(f"Lỗi khi truy vấn CSDL cho trang chủ (phân trang): {e}")
        songs_on_page = []
        pagination = None # Không có đối tượng pagination nếu lỗi

    return render_template('song_list.html',
                           title="Tất Cả Bài Hát",
                           songs=songs_on_page, # Chỉ truyền các bài hát của trang hiện tại
                           section_title="Tất Cả Bài Hát",
                           pagination=pagination) # Truyền đối tượng pagination vào template

@main_bp.route('/search')
def search():
    """
    Xử lý tìm kiếm bài hát và hiển thị kết quả, có phân trang.
    """
    query_param = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('SONGS_PER_PAGE', 10)

    songs_on_page = []
    pagination = None
    page_title = "Tìm Kiếm Bài Hát"
    section_title_text = "Kết quả tìm kiếm"

    if query_param:
        search_term = f'%{query_param}%'
        try:
            # Xây dựng query cơ sở
            base_query = Song.query.filter(
                (Song.title.ilike(search_term)) |
                (Song.artist.ilike(search_term)) |
                (Song.album.ilike(search_term))
            ).order_by(Song.title)

            # Thực hiện phân trang trên query đó
            pagination = base_query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            songs_on_page = pagination.items

            print(f"Tìm kiếm cho '{query_param}', trang {page}: tìm thấy {len(songs_on_page)}/{pagination.total} kết quả.")
            page_title = f"Kết quả cho: '{query_param}'"
            section_title_text = f"Kết quả cho: \"{query_param}\" (Trang {page})"
        except Exception as e:
            print(f"Lỗi khi truy vấn CSDL cho tìm kiếm '{query_param}' (phân trang): {e}")
            songs_on_page = []
            pagination = None
    else:
        section_title_text = "Vui lòng nhập từ khóa để tìm kiếm"

    return render_template('song_list.html',
                           title=page_title,
                           songs=songs_on_page, # Chỉ truyền các bài hát của trang hiện tại
                           search_query_display=query_param,
                           section_title=section_title_text,
                           pagination=pagination) # Truyền đối tượng pagination

# Route play_song giữ nguyên như trước (placeholder)
@main_bp.route('/play/<int:song_id>')
def play_song(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template('music_player_placeholder.html', song=song, title=f"Đang phát: {song.title}")
