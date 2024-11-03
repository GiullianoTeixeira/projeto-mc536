from flask import *
from flask_login import *


import model
from functools import wraps
from flask import abort

app = Flask(__name__, template_folder='templates')

# Configure MySQL connection

# Custom decorator to check if the user has the required role

if __name__ == '__main__':
    app.run(debug=True)