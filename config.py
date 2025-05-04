import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False