from flask import *
from flask_login import *
from . import model, db
from functools import wraps

def role_required(role: model.UserRole):
    def has_role(user: model.User, role: model.UserRole) -> bool:
        if role == model.UserRole.PF:
            return user.type == "pf"
        elif role == model.UserRole.PJ_pv:
            return user.type == "pj" and not user.is_govt
        elif role == model.UserRole.PJ_gov:
            return user.type == "pj" and user.is_govt
        else:
            return False

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not has_role(model.get_typed_user_by_nontyped_user(db.get_db(), current_user), role):
                abort(403)  # Forbidden access
            return f(*args, **kwargs)
        return decorated_function
    return decorator

bp = Blueprint('waterbody', __name__)

@bp.route('/waterbody/<int:waterbody_id>', methods=['GET'])
@login_required  
def waterbody_super_page(waterbody_id):
    
    waterbody = model.create_waterbody_super_page(db.get_db(), waterbody_id)
    print(waterbody.waterbody)
    print(waterbody.complaints[0]['id'])
    return render_template("waterbody.html", waterbody=waterbody)

@bp.route("/solution/<int:solution_id>", methods=["GET"])
@login_required
def solution(solution_id):
    solution = model.get_solution_by_id(db.get_db(), solution_id)

    issuing_entity = model.get_typed_user_by_id(db.get_db(), solution.issuing_entity)
    solution.issuing_entity = f"{issuing_entity.razao_social} ({issuing_entity.id})"

    referenced_waterbody = model.get_waterbody_by_id(db.get_db(), solution.referenced_waterbody)
    solution.referenced_waterbody = f"{referenced_waterbody.name} ({referenced_waterbody.id})"

    return render_template("solution.html", solution=solution)

@bp.route("/simulation/<int:simulation_id>", methods=["GET"])
@login_required
@role_required(model.UserRole.PJ_pv)
def simulation(simulation_id):
    simulation = model.get_simulation_by_id(db.get_db(), simulation_id)

    issuing_entity = model.get_typed_user_by_id(db.get_db(), simulation.issuing_entity)
    simulation.issuing_entity = f"{issuing_entity.razao_social} ({issuing_entity.id})"

    referenced_waterbody = model.get_waterbody_by_id(db.get_db(), simulation.referenced_waterbody)
    simulation.referenced_waterbody = f"{referenced_waterbody.name} ({referenced_waterbody.id})"

    return render_template("simulation.html", simulation=simulation)

@bp.route("/waterbody/<int:waterbody_id>/report/<int:report_id>", methods=["GET"])
@login_required
def report(waterbody_id, report_id):
    report = model.get_report_by_id(db.get_db(), report_id)

    issuing_entity = model.get_typed_user_by_id(db.get_db(), report.issuing_entity)
    report.issuing_entity = f"{issuing_entity.razao_social} ({issuing_entity.id})"

    referenced_waterbody = model.get_waterbody_by_id(db.get_db(), waterbody_id)
    report.referenced_waterbody = f"{referenced_waterbody.name} ({referenced_waterbody.id})"

    return render_template("report.html", report=report)

@bp.route('/complaint_form', methods=['GET', 'POST'])
def complaint_form():
    if request.method == 'POST':
       
        complainer = str(current_user.id) 
        date_time = request.form['datahora']
        referred_body = request.form['corpoReferente']
        category = request.form['categoria']
        severity = request.form['severidade']
        description = request.form['descricao']
        complaint = model.Complaint(complainer, date_time, referred_body, category, severity, description)
        
        model.send_complaint_form(db.get_db(), complaint)

        return redirect(url_for('complaint_form'))

    return render_template('complaint_form.html')

@bp.route('/waterbody/<int:waterbody_id>/complaint/<int:id>', methods=['GET'])
def complaint(waterbody_id, id):
    
    complaint = model.get_complaint(db.get_db(), id)
    
    return render_template('complaint.html', complaint=complaint)