import os
from flask import *
from . import db, auth, waterbody, search

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, template_folder='templates', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    @app.route('/')
    def login():
        return render_template('login.html')
    
    db.init_app(app)
    app.register_blueprint(auth.bp)
    auth.init_app(app)
    app.register_blueprint(waterbody.bp)
    app.register_blueprint(search.bp)

    return app