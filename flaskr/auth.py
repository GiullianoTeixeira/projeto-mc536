from flask import *
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from . import model
from flask_login import *
import mysql.connector

bp = Blueprint('auth', __name__)
login_manager = LoginManager()

def init_app(app):
    login_manager.init_app(app)

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_type = request.form.get("userType")
        error = None

        if user_type == "PF":
            id = request.form.get("cpf")
            password = request.form.get("passwordPF")
            name = request.form.get("name")
            date_of_birth = request.form.get("dob")
            user = model.UserPF(id, password, name, date_of_birth)
        elif user_type == "PJ":
            id = request.form.get("cnpj")
            password = request.form.get("passwordPJ")
            razao_social = request.form.get("razaoSocial")
            representative = request.form.get("representative")
            is_govt = True if request.form.get("govInstitution") == 'on' else False
            user = model.UserPJ(id, password, razao_social, representative, is_govt)
        
        if not name:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        if error is None:
            try:
                model.create_user(get_db(), user)
                flash("Registration successful!", "success")
            except mysql.connector.IntegrityError:
                error = f"User {name} is already registered."
                flash(error)
            else:
                return render_template("login.html")
        else:
            flash(error)
    
        return render_template("register.html")
            
    elif request.method == "GET":
        return render_template("register.html")
    
@bp.route("/login", methods=["GET", "POST"])
def login_handler():
    if request.method == "POST":
        user = model.get_user_by_id(get_db(), request.form.get("username"))
        if user is not None and user.password == request.form.get("password"):
            login_user(user)
            session['user_id'] = user.id
            return redirect(url_for("search.search"))
        else:
            return "Login failed"
        
    elif request.method == "GET":
        return render_template("login.html")
    

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    if not db or not db.is_connected():
        print("DB connection in load_user() is not available")
    return model.get_user_by_id(db, user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to access this page", "danger")
    return redirect(url_for('auth.login'))

@bp.context_processor
def inject_user_id():
    return dict(user_id=current_user.id if current_user.is_authenticated else None)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for('auth.login'))