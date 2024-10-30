from flask import *
from flask_login import *
import mysql.connector
import os
from dotenv import load_dotenv
import model

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
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
    
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

@login_manager.user_loader
def load_user(user_id):
    return model.get_user_by_id(get_db(), user_id)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/test')
@login_required
def test():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Usuario')
    users = cursor.fetchall()
    cursor.close()
    print(current_user)
    return "Done"

@app.route("/login", methods=["GET", "POST"])
def login_handler():
    if request.method == "POST":
        user = model.get_user_by_id(get_db(), request.form.get("username"))
        if user is not None and user.password == request.form.get("password"):
            # Use the login_user method to log in the user
            login_user(user)
            return redirect(url_for("test"))
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
        
        print(user)
        model.create_user(get_db(), user)
        return "ok"
            
    elif request.method == "GET":
        return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)