import mysql.connector
from flask import *
import os
from dotenv import load_dotenv

def get_db():
    load_dotenv()
    if not hasattr(g, 'db') or not g.db.is_connected():
        current_app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
        current_app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
        current_app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
        current_app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
        current_app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DB']
            )
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            g.db = None
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    