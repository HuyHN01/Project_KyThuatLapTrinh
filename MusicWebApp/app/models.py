
from datetime import datetime
from . import db  # Import db từ file __init__.py cùng cấp (trong thư mục app)

class Song(db.Model):
    __tablename__ = 'song'  # Tên của bảng trong cơ sở dữ liệu (nên viết thường)

    # Định nghĩa các cột (fields) cho bảng 'song'
    id = db.Column(db.Integer, primary_key=True)  # Khóa chính, tự động tăng
    title = db.Column(db.String(200), nullable=False, index=True)  # Tên bài hát, không được rỗng, có index
    artist = db.Column(db.String(150), nullable=True, index=True) # Tên nghệ sĩ, có thể rỗng, có index
    album = db.Column(db.String(150), nullable=True)              # Tên album, có thể rỗng
    genre = db.Column(db.String(100), nullable=True, index=True)  # Thể loại, có thể rỗng, có index
    image_url = db.Column(db.String(500), nullable=True)         # URL ảnh bìa, có thể rỗng
    stream_url = db.Column(db.String(500), nullable=True)        # URL để phát nhạc hoặc đường dẫn file, có thể rỗng
                                                                 # nullable=True vì có thể bạn chỉ crawl metadata trước
    source_url = db.Column(db.String(500), nullable=False, unique=True) # URL gốc của bài hát đã crawl, không rỗng và duy nhất
    crawled_at = db.Column(db.DateTime, default=datetime.utcnow) # Thời điểm dữ liệu được crawl, mặc định là thời gian hiện tại

    def __repr__(self):
        # Phương thức này giúp hiển thị đối tượng Song một cách dễ đọc khi debug
        return f'<Song {self.id}: {self.title} by {self.artist}>'

# Bạn có thể thêm các model khác ở đây nếu cần trong tương lai,
# nhưng theo yêu cầu hiện tại, chỉ cần model Song.
