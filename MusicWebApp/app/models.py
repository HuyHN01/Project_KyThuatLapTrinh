from datetime import datetime
from . import db

class Song(db.Model):
    __tablename__ = 'song'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    artist = db.Column(db.String(150), nullable=True, index=True)
    album = db.Column(db.String(150), nullable=True)
    genre = db.Column(db.String(100), nullable=True, index=True)
    image_url = db.Column(db.String(500), nullable=True)
    stream_url = db.Column(db.String(500), nullable=True)
    source_url = db.Column(db.String(500), nullable=False, unique=True)
    crawled_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Song {self.id}: {self.title} by {self.artist}>'
