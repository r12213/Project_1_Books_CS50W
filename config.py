import os


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "anotherSECRETkeyLOL")
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    GOODREADS_API_KEY = os.getenv("GOODREADS_API_KEY")


class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite://'
