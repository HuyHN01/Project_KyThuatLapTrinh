 # MusicWebApp/run.py
from app import create_app, db # Import db từ app
# Import tất cả các model để Flask-Migrate có thể phát hiện
from app.models import User, Artist, Album, Genre, Song, Playlist, ListenHistory, playlist_songs, favorite_songs

app = create_app()

@app.shell_context_processor
def make_shell_context():
    # Hàm này cho phép bạn truy cập db và các model trong `flask shell`
    return {
        'db': db,
        'User': User,
        'Artist': Artist,
        'Album': Album,
        'Genre': Genre,
        'Song': Song,
        'Playlist': Playlist,
        'ListenHistory': ListenHistory,
        'playlist_songs': playlist_songs,
        'favorite_songs': favorite_songs
    }

if __name__ == '__main__':
    app.run(debug=True)
