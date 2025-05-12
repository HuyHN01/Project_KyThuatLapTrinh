# MusicWebApp/app/models.py
from datetime import datetime, date
from app import db # Import db từ __init__.py của app

# Bảng liên kết cho Playlist và Song (Many-to-Many)
# Các ForeignKey ở đây sử dụng tên bảng viết thường và tên cột (ví dụ: 'playlist.id', 'song.id')
playlist_songs = db.Table('playlist_songs',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id', ondelete='CASCADE'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id', ondelete='CASCADE'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)

# Bảng liên kết cho User và Song (Favorite Songs - Many-to-Many)
favorite_songs = db.Table('favorite_songs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id', ondelete='CASCADE'), primary_key=True),
    db.Column('favorited_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    __tablename__ = 'user' # Tên bảng sẽ là 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships: Sử dụng tên class dưới dạng chuỗi
    playlists = db.relationship('Playlist', backref='owner', lazy='dynamic', cascade="all, delete")
    favorited = db.relationship(
        'Song',
        secondary=favorite_songs,
        backref=db.backref('favorited_by', lazy='dynamic'),
        lazy='dynamic'
    )
    listen_history = db.relationship('ListenHistory', backref='user', lazy='dynamic', cascade="all, delete")

    # Các phương thức set_password và check_password nên được chuyển sang services/routes
    # hoặc sử dụng một mixin class nếu bạn muốn tái sử dụng.
    # Để đơn giản, tạm import ở đây.
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Artist(db.Model):
    __tablename__ = 'artist' # Tên bảng sẽ là 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True, index=True)
    bio = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(256), nullable=True)

    songs = db.relationship('Song', backref='artist_details', lazy='dynamic')
    albums = db.relationship('Album', backref='artist_details', lazy='dynamic')

    def __repr__(self):
        return f'<Artist {self.name}>'

class Genre(db.Model):
    __tablename__ = 'genre' # Tên bảng sẽ là 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)

    songs = db.relationship('Song', backref='genre_details', lazy='dynamic')
    albums = db.relationship('Album', backref='genre_details', lazy='dynamic')

    def __repr__(self):
        return f'<Genre {self.name}>'

class Album(db.Model):
    __tablename__ = 'album' # Tên bảng sẽ là 'album'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    # ForeignKey tham chiếu đến 'tên_bảng.tên_cột'
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=True)
    release_date = db.Column(db.Date, nullable=True)
    cover_image_url = db.Column(db.String(256), nullable=True)

    songs = db.relationship('Song', backref='album_details', lazy='dynamic', cascade="all, delete")

    def __repr__(self):
        return f'<Album {self.title}>'

class Song(db.Model):
    __tablename__ = 'song' # Tên bảng sẽ là 'song'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    file_path = db.Column(db.String(256), nullable=False)
    release_date = db.Column(db.Date, nullable=True)
    cover_image_url = db.Column(db.String(256), nullable=True)
    lyrics = db.Column(db.Text, nullable=True)
    play_count = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Mối quan hệ `playlists` và `favorited_by` được tạo tự động thông qua backref
    # từ model Playlist và User.
    # Mối quan hệ `listen_events` được tạo qua backref từ ListenHistory.

    def __repr__(self):
        return f'<Song {self.title}>'

class Playlist(db.Model):
    __tablename__ = 'playlist' # Tên bảng sẽ là 'playlist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)

    songs = db.relationship(
        'Song',
        secondary=playlist_songs,
        backref=db.backref('playlists', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Playlist {self.name}>'

class ListenHistory(db.Model):
    __tablename__ = 'listen_history' # Tên bảng sẽ là 'listen_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False, index=True)
    listened_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Mối quan hệ này cho phép truy cập `ListenHistory.song` để lấy thông tin bài hát
    song = db.relationship('Song', backref='listen_events') # 'Song' là chuỗi

    def __repr__(self):
        return f'<ListenHistory User {self.user_id} song {self.song_id} at {self.listened_at}>'
