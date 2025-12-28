import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Get the directory of this file and load .env from there
load_dotenv('/var/www/delivery-box/app/.env')

class Config:
    """Database configuration"""
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'delivery_box')
    DB_PORT = os.getenv('DB_PORT', 3306)
    
    # URL-encode the password to handle special characters like @
    encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ''
    
    # SQLAlchemy configuration
    if encoded_password:
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    else:
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True