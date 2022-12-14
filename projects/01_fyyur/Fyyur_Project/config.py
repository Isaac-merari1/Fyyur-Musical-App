import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456789@localhost:5432/fyyurdb'
SQLALCHEMY_TRACK_MODIFICATIONS = False

class DatabaseURI:
    DATABASE_NAME = "fyyurdb"
    username = 'postgres'
    password = '123456789'
    url = 'localhost:5432'
    SQLALCHEMY_DATABASE_URI = "postgres://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)