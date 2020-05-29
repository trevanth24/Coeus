import secrets

class Config:
    SECRET_KEY = secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db' #Path to SQLite Database (three slashes indicate a relative path)
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'trevanth24@gmail.com' #os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = 'Teslamodel@3' #os.environ.get('EMAIL_PASS')