from flask import *
from flask_login import *
import mysql.connector
import os
from dotenv import load_dotenv
import model, useful_queries

load_dotenv()

app = Flask(__name__, template_folder='templates')

login_manager = LoginManager()
login_manager.init_app(app)

# Configure MySQL connection
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

def get_db():
    if not hasattr(g, 'db') or not g.db.is_connected():
        try:
            g.db = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DB']
            )
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            g.db = None
    
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    if not db or not db.is_connected():
        print("DB connection in load_user() is not available")
    return model.get_user_by_id(db, user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to access this page", "danger")
    return redirect(url_for('login'))

@app.route('/')
def login():
    return render_template('login.html')

@app.route("/login", methods=["GET", "POST"])
def login_handler():
    if request.method == "POST":
        user = model.get_user_by_id(get_db(), request.form.get("username"))
        if user is not None and user.password == request.form.get("password"):
            login_user(user)
            session['user_id'] = user.id
            return redirect(url_for("search"))
        else:
            return "Login failed"
        
    elif request.method == "GET":
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_type = request.form.get("userType")

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
        
        model.create_user(get_db(), user)
        flash("Registration successful!", "success")

        return render_template("login.html")
            
    elif request.method == "GET":
        return render_template("register.html")
    
@app.context_processor
def inject_user_id():
    return dict(user_id=current_user.id if current_user.is_authenticated else None)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

@app.route('/waterbody/<int:waterbody_id>', methods=['GET'])
@login_required  
def waterbody(waterbody_id):
    
    connection = get_db()
    # Fetch waterbody details and related statistics
    (
    waterbody_data, 
    count_complaints, 
    count_reports, 
    media_indice_biodiversidade, 
    ph_stats, 
    denuncias_por_severidade
    ) = useful_queries.get_waterbodydata_by_id(connection, waterbody_id)
    

    user_type = useful_queries.get_user_type_by_id(current_user.id)
    connection.close()
    
    return render_template(
        "waterbody.html",
        waterbody=waterbody_data,
        count_complaints=count_complaints,
        count_reports=count_reports,
        media_indice_biodiversidade=media_indice_biodiversidade,
        ph_stats=ph_stats,
        denuncias_por_severidade=denuncias_por_severidade,
        user_type=user_type
    )

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    query = request.form.get("query", "")
    results = []
    if query:
        results = model.search_waterbody_by_name(get_db(), query)
    
    return render_template("search.html", query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)