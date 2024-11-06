from flask import *
from flask_login import *
from . import db
from . import model

bp = Blueprint('search', __name__)

@bp.route("/search", methods=["GET", "POST"])
@login_required
def search():
    query = request.form.get("query", "")
    results = []
    if query:
        results = model.search_waterbody_by_name(db.get_db(), query)
    
    return render_template("search.html", query=query, results=results)