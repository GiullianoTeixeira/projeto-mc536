from flask import *
from flask_login import *
import useful_queries
from enum import Enum
from datetime import datetime
import colorama
from colorama import Fore

colorama.init(autoreset=True)

class UserRole(Enum):
    PF = 'PF'
    PJ_pv = 'PJ_pv'
    PJ_gov = 'PJ_gov'

class User(UserMixin):
    def __init__(self, id, password, type):
        self.id = id
        self.password = password
        self.type = type
    
    def __repr__(self):
        return f"User(id='{self.id}', password='{self.password}', type='{self.type}')"

class UserPF(User):
    def __init__(self, id, password, name, date_of_birth):
        super().__init__(id, password, 'pf')
        self.name = name
        self.date_of_birth = date_of_birth

    def __repr__(self):
        return f"UserPF(id='{self.id}', password='{self.password}', type='{self.type}', name='{self.name}', date_of_birth='{self.date_of_birth}')"

class UserPJ(User):
    def __init__(self, id: str, password: str, razao_social: str, representative: str, is_govt: bool):
        super().__init__(id, password, 'pj')
        self.razao_social = razao_social
        self.representative = representative
        self.is_govt = is_govt

    def __repr__(self):
        return f"UserPJ(id='{self.id}', password='{self.password}', type={self.type}, razao_social='{self.razao_social}', is_govt='{self.is_govt}')"

class WaterBody:
    def __init__(self, id: int, name: str, coords: str, image_url: str):
        self.id = id
        self.name = name
        self.coords = coords
        self.image_url = image_url
    
    def __repr__(self):
        return f"WaterBody(id='{self.id}', name='{self.name}', coords='{self.coords}', image_url='{self.image_url}')"

class Solution:
    def __init__(self, id: int, issuing_entity: str, referenced_waterbody: int, budget: float, description: str):
        self.id = id
        self.issuing_entity = issuing_entity
        self.referenced_waterbody = referenced_waterbody
        self.budget = budget
        self.description = description
    
    def __repr__(self):
        return f"Solution(id='{self.id}', issuing_entity='{self.issuing_entity}', referenced_waterbody='{self.referenced_waterbody}', budget='{self.budget}', description='{self.description}')"

class Simulation:
    def __init__(self, id: int, issuing_entity: str, referenced_waterbody: int, severity: str, description: str):
        self.id = id
        self.issuing_entity = issuing_entity
        self.referenced_waterbody = referenced_waterbody
        self.severity = severity
        self.description = description
    
    def __repr__(self):
        return f"Simulation(id='{self.id}', issuing_entity='{self.issuing_entity}', referenced_waterbody='{self.referenced_waterbody}', severity='{self.severity}', description='{self.description}')"

class Report:
    def __init__(self, id: int, issuing_entity: str, datetime: datetime, referenced_waterbody: int, text: str, pH: float = None, biodiversity_index: int = None):
        self.id = id
        self.issuing_entity = issuing_entity
        self.datetime = datetime
        self.referenced_waterbody = referenced_waterbody
        self.text = text
        self.pH = pH
        self.biodiversity_index = biodiversity_index
    
    def __repr__(self):
        return f"Report(id='{self.id}', issuing_entity='{self.issuing_entity}', datetime='{self.datetime}', referenced_waterbody='{self.referenced_waterbody}', text='{self.text}', pH='{self.pH}', biodiversity_index='{self.biodiversity_index}')"

class WaterBodySuperPage:
    def __init__(self, waterbody, count_complaints, count_reports, 
                 biodiversity_media_index, ph_stats, complaints_by_severity, user_type):
        self.waterbody = waterbody
        self.count_complaints = count_complaints
        self.count_reports = count_reports
        self.biodiversity_media_index = biodiversity_media_index
        self.ph_stats = ph_stats
        self.complaints_by_severity = complaints_by_severity
        self.user_type = user_type
    
    def __repr__(self):
        return (f"Water Body: {self.waterbody}"
                f"Complaints Count: {self.count_complaints}"
                f"Reports Count: {self.count_reports}"
                f"Average Biodiversity Index: {self.media_indice_biodiversidade}"
                f"pH Statistics: {self.ph_stats}"
                f"Complaints by Severity: {self.denuncias_por_severidade}"
                f"User Type: {self.user_type}")
    
class Complaint:
    def __init__(self, complainer, date_time, referred_body, category, severity, description):
        self.complainer = complainer
        self.date_time = date_time
        self.referred_body = referred_body
        self.category = category
        self.severity = severity
        self.description = description
        
    def __repr__(self):
        return (f"Complaint Details:\n"
                f"Complainer: {self.complainer}\n"
                f"Date and Time: {self.date_time}\n"
                f"Referred Body: {self.referred_body}\n"
                f"Category: {self.category}\n"
                f"Severity: {self.severity}\n"
                f"Description: {self.description}\n")

def get_user_by_id(db, id) -> User:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Usuario WHERE id = %s', (id,))
    user = cursor.fetchone()
    cursor.close()

    print(Fore.YELLOW + cursor.statement)
    if user:
        return User(user[0], user[1], user[2])
    return None

def get_typed_user_by_id(db, id) -> User:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Usuario WHERE id = %s', (id,))
    user = cursor.fetchone()
    cursor.close()

    print(Fore.YELLOW + cursor.statement)
    if user:
        if user[2] == 'pf':
            cursor = db.cursor()
            cursor.execute('SELECT * FROM PessoaFisica WHERE cpf = %s', (id,))
            specific_data = cursor.fetchone()
            cursor.close()
            return UserPF(user[0], user[1], specific_data[1], specific_data[2])
        elif user[2] == 'pj':
            cursor = db.cursor()
            cursor.execute('SELECT * FROM PessoaJuridica WHERE cnpj = %s', (id,))
            specific_data = cursor.fetchone()
            cursor.close()
            return UserPJ(user[0], user[1], specific_data[1], specific_data[2], specific_data[3])
    return None

def get_typed_user_by_nontyped_user(db, user: User) -> User:
    return get_typed_user_by_id(db, user.id)

def get_user_password(db, id) -> str:
    cursor = db.cursor()
    cursor.execute('SELECT password FROM Usuario WHERE id = %s', (id,))
    user = cursor.fetchone()
    cursor.close()

    print(Fore.YELLOW + cursor.statement)
    if user:
        return user[0]
    return None

def create_user(db, user):
    cursor = db.cursor()
    cursor.execute('INSERT INTO Usuario (id, senha, tipo) VALUES (%s, %s, %s)', (user.id, user.password, user.type))
    if user.type == 'PF':
        cursor.execute('INSERT INTO PessoaFisica (cpf, nome, data_nasc) VALUES (%s, %s, %s)', (user.id, user.name, user.date_of_birth))
    elif user.type == 'PJ':
        cursor.execute('INSERT INTO PessoaJuridica (cnpj, razaoSocial, representante, isOrgaoGovernamental) VALUES (%s, %s, %s, %s)', (user.id, user.razao_social, user.representative, user.is_govt))

    db.commit()
    print(Fore.YELLOW + cursor.statement)
    cursor.close()

def get_waterbody_by_id(db, id) -> WaterBody:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM CorpoAgua WHERE id = %s', (id,))
    waterbody = cursor.fetchone()
    cursor.close()

    print(Fore.YELLOW + cursor.statement)
    if waterbody:
        return WaterBody(*waterbody)
    return None

def search_waterbody_by_name(db, name) -> list[WaterBody]:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM CorpoAgua WHERE nome LIKE %s', (f'%{name}%',))
    results = cursor.fetchall()
    cursor.close()

    print(Fore.YELLOW + cursor.statement)
    return [WaterBody(*result) for result in results]

def get_solution_by_id(db, id) -> Solution:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Solucao WHERE id = %s', (id,))
    solution = cursor.fetchone()
    cursor.close()

    print(Fore.YELLOW + cursor.statement)
    if solution:
        return Solution(*solution)
    return None

def get_simulation_by_id(db, id) -> Simulation:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Simulacao WHERE id = %s', (id,))
    simulation = cursor.fetchone()
    cursor.close()

    print(Fore.YELLOW + cursor.statement)
    if simulation:
        return Simulation(*simulation)
    return None

def get_report_by_id(db, id) -> Report:
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Relatorio WHERE id = %s', (id,))
    report = cursor.fetchone()
    cursor.close()

    print(Fore.YELLOW + cursor.statement)
    if report:
        return Report(*report)
    return None
  
    print(cursor.statement)
    return [WaterBody(*result) for result in results]

def send_complaint_form(db, complaint):  
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO Denuncia
        (denunciante, datahora, corpoReferente, categoria, severidade, descricao) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (complaint.complainer, complaint.date_time, complaint.referred_body, complaint.category, complaint.severity, complaint.description))
    
    db.commit()
    cursor.close()

def create_waterbody_super_page(db, waterbody_id):
    (
        waterbody, count_complaints, count_reports, biodiversity_media_index, ph_stats, complaints_by_severity
    ) = useful_queries.get_waterbodydata_by_id(db, waterbody_id)
    
    user_type = useful_queries.get_user_type_by_id(current_user.id)
    
    waterbody_super_page = WaterBodySuperPage(waterbody, count_complaints, count_reports, biodiversity_media_index, ph_stats, complaints_by_severity, user_type)
    
    return waterbody_super_page

def get_complaint(db, id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Denuncia WHERE id = %s", (id,))
    complaint = cursor.fetchone()

    cursor.close()
    
    return complaint
