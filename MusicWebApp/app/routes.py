# MusicWebApp/app/routes.py (Hoặc app/main_routes.py)
from flask import Blueprint, render_template, request, current_app # Thêm current_app
from .models import Song
from sqlalchemy import func
from . import db

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
                (Song.album.ilike(search_term)) |
                (Song.genre.ilike(search_term))
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
# @main_bp.route('/play/<int:song_id>')
# def play_song(song_id):
#     song = Song.query.get_or_404(song_id)
#     return render_template('music_player_placeholder.html', song=song, title=f"Đang phát: {song.title}")

@main_bp.route('/genres')
def list_genres():
    """
    Hiển thị danh sách tất cả các thể loại nhạc có trong cơ sở dữ liệu.
    """
    try:
        # Lấy tất cả các giá trị genre độc nhất và đếm số lượng bài hát cho mỗi genre
        # filter(Song.genre != None) để loại bỏ các bài hát không có genre
        # order_by(func.count(Song.id).desc()) sắp xếp theo số lượng bài hát giảm dần
        genres_with_counts = db.session.query(
                                Song.genre, func.count(Song.id).label('song_count')
                            ).filter(Song.genre != None, Song.genre != '').group_by(Song.genre).order_by(func.count(Song.id).desc()).all()

        print(f"Tìm thấy {len(genres_with_counts)} thể loại.")

    except Exception as e:
        print(f"Lỗi khi truy vấn danh sách thể loại: {e}")
        genres_with_counts = []

    return render_template('genre_list.html',
                           title="Khám Phá Theo Thể Loại",
                           genres_data=genres_with_counts,
                           section_title="Tất Cả Thể Loại")

@main_bp.route('/genre/<string:genre_name>')
def songs_by_genre(genre_name):
    """
    Hiển thị danh sách các bài hát thuộc một thể loại cụ thể, có phân trang.
    """
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('SONGS_PER_PAGE', 10)

    processed_genre_name = genre_name.replace('-', ' ') # Xử lý nếu genre_name từ URL có dấu gạch nối

    try:
        # Tìm kiếm không phân biệt hoa thường cho genre
        # và đảm bảo genre không rỗng hoặc None
        base_query = Song.query.filter(Song.genre.ilike(f'%{processed_genre_name}%'), Song.genre != None, Song.genre != '') \
                               .order_by(Song.title) # Sắp xếp theo tiêu đề bài hát

        pagination = base_query.paginate(page=page, per_page=per_page, error_out=False)
        songs_in_genre = pagination.items

        print(f"Tìm thấy {len(songs_in_genre)}/{pagination.total} bài hát cho thể loại '{processed_genre_name}', trang {page}.")

    except Exception as e:
        print(f"Lỗi khi truy vấn CSDL cho thể loại '{processed_genre_name}': {e}")
        songs_in_genre = []
        pagination = None

    # Sử dụng lại template song_list.html để hiển thị
    return render_template('song_list.html',
                           title=f"Thể Loại: {processed_genre_name.capitalize()}",
                           songs=songs_in_genre,
                           section_title=f"Bài hát thuộc thể loại: {processed_genre_name.capitalize()}",
                           pagination=pagination,
                           # (Tùy chọn) Truyền thêm biến để biết đang ở trang genre
                           current_genre=processed_genre_name
                           )
