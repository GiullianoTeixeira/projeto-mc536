import os
from flask import *
from dotenv import load_dotenv
from . import db, auth, waterbody, search

load_dotenv()
def create_app(test_config=None):
    
    # create and configure the app
    app = Flask(__name__, template_folder='templates', instance_relative_config=True)
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

    @app.route('/')
    def login():
        return render_template('login.html')
    
    db.init_app(app)
    app.register_blueprint(auth.bp)
    auth.init_app(app)
    app.register_blueprint(waterbody.bp)
    app.register_blueprint(search.bp)

    return app