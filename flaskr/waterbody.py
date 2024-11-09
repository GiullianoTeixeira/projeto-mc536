from flask import *
from flask_login import *
from . import model, db
from functools import wraps
from . import groq_integragtion
from datetime import datetime

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
    sp_info = model.create_waterbody_super_page(db.get_db(), waterbody_id)
    return render_template("waterbody.html", sp_info=sp_info)

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

@bp.route("/report/<int:report_id>", methods=["GET"])
@login_required
def report(report_id):
    report = model.get_report_by_id(db.get_db(), report_id)

    issuing_entity = model.get_typed_user_by_id(db.get_db(), report.issuing_entity)
    report.issuing_entity = f"{issuing_entity.razao_social} ({issuing_entity.id})"

    referenced_waterbody = model.get_waterbody_by_id(db.get_db(), report.referenced_waterbody)
    report.referenced_waterbody = f"{referenced_waterbody.name} ({referenced_waterbody.id})"

    return render_template("report.html", report=report)

@bp.route('/<string:waterbody_id>/complaint_form', methods=['GET', 'POST'])
@login_required
def complaint_form(waterbody_id):
    waterbody = model.get_waterbody_by_id(db.get_db(), waterbody_id)
    
    if request.method == 'POST':    
        complainer = str(current_user.id) 
        date_time = request.form['datahora']
        category = request.form['categoria']
        severity = request.form['severidade']
        description = request.form['descricao']
        complaint = model.Complaint(waterbody, complainer, date_time, category, severity, description)
        
        model.send_complaint_form(db.get_db(), complaint)
        return jsonify({'success': True})
    return render_template('complaint_form.html', user=str(current_user.id), waterbody=waterbody)

@bp.route('/complaint/<int:id>', methods=['GET'])
def complaint(id):
    complaint = model.get_complaint(db.get_db(), id)
    
    return render_template('complaint.html', complaint=complaint)

@bp.route('/create_report', methods=['GET'])
def create_report():
    waterbody_id = request.args.get('waterbody_id')
    waterbody = model.get_waterbody_by_id(db.get_db(), waterbody_id)

    attempts = 5
    while attempts > 0:
        try:
            result = groq_integragtion.get_report(waterbody.name)
            report = model.Report(-1, current_user.id, datetime.now(), waterbody.id, result['text'], result['pH'], result['indiceBiodiversidade'])
            model.create_report(db.get_db(), report)
            break
        except Exception as e:
            attempts -= 1
            if attempts == 0:
                return jsonify({'success': False, 'error': str(e)})

    return waterbody_super_page(waterbody_id)

@bp.route('/create_simulation', methods=['GET'])
def create_simulation():
    waterbody_id = request.args.get('waterbody_id')
    event = request.args.get('event')

    if not waterbody_id or not event:
        return jsonify({'success': False, 'error': 'Waterbody ID and event type are required.'})

    # Fetch the waterbody details
    waterbody = model.get_waterbody_by_id(db.get_db(), waterbody_id)

    attempts = 5
    while attempts > 0:
        try:
            # Use the user-provided event type
            result = groq_integragtion.get_simulation(waterbody.name, event)
            report = model.Simulation(-1, current_user.id, waterbody.id, result['severity'], result['text'])
            model.create_simulation(db.get_db(), report)
            break
        except Exception as e:
            attempts -= 1
            if attempts == 0:
                return jsonify({'success': False, 'error': str(e)})

    return waterbody_super_page(waterbody_id)