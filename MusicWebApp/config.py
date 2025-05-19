import os
from urllib.parse import quote_plus

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'keSPH42aN0WZlR3'

    DB_DRIVER_NAME = 'ODBC Driver 18 for SQL Server'
    DB_SERVER = 'MyHLaptop'
    DB_DATABASE = 'MyMusicAppDB'

    ENCODED_DB_DRIVER = quote_plus(DB_DRIVER_NAME)

    SQLALCHEMY_DATABASE_URI = (
        f'mssql+pyodbc://@{DB_SERVER}/{DB_DATABASE}'
        f'?driver={ENCODED_DB_DRIVER}'
        f'&Trusted_Connection=yes'
        f'&Encrypt=no'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SONGS_PER_PAGE = 10
