from flask_login import UserMixin
import mysql.connector

class User(UserMixin):
    def __init__(self, id, password, type):
        self.id = id
        self.password = password
        self.type = type
    
    def __str__(self):
        return f"User(id='{self.id}', password='{self.password}', type='{self.type}')"

class UserPF(User):
    def __init__(self, id, password, name, date_of_birth):
        super().__init__(id, password, 'PF')
        self.name = name
        self.date_of_birth = date_of_birth

    def __str__(self):
        return f"UserPF(id='{self.id}', password='{self.password}', name='{self.name}', date_of_birth='{self.date_of_birth}')"

class UserPJ(User):
    def __init__(self, id: str, password: str, razao_social: str, representative: str, is_govt: bool):
        super().__init__(id, password, 'PJ')
        self.razao_social = razao_social
        self.representative = representative
        self.is_govt = is_govt

    def __str__(self):
        return f"UserPJ(id='{self.id}', password='{self.password}', razao_social='{self.razao_social}', is_govt='{self.is_govt}')"

def get_user_by_id(db, id):
    print("Getting user by id: ", id)

    cursor = db.cursor()
    cursor.execute('SELECT * FROM Usuario WHERE id = %s', (id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return User(user[0], user[1], user[2])
    return None

def get_user_password(db, id):
    cursor = db.cursor()
    cursor.execute('SELECT password FROM Usuario WHERE id = %s', (id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return user[0]
    return None

# def creste_user(db, id, password, type, nome=None, data_nascimento=None, razao_social=None, representative=None, is_govt=None):
#     cursor = db.cursor()
#     cursor.execute('INSERT INTO Usuario (id, password, type) VALUES (%s, %s, %s)', (id, password, type))
#     if type == 'PF':
#         cursor.execute('INSERT INTO PessoaFisica (cpf, nome, data_nasc) VALUES (%s, %s, %s)', (id, nome, data_nascimento))
#     elif type == 'PJ':
#         cursor.execute('INSERT INTO PessoaJuridica (cnpj, razaoSocial, representante, isOrgaoGovernamental) VALUES (%s, %s, %s)', (id, razao_social, representative, is_govt))

#     db.commit()
#     cursor.close()

def create_user(db, user):
    cursor = db.cursor()
    cursor.execute('INSERT INTO Usuario (id, senha, tipo    ) VALUES (%s, %s, %s)', (user.id, user.password, user.type))
    if user.type == 'PF':
        cursor.execute('INSERT INTO PessoaFisica (cpf, nome, data_nasc) VALUES (%s, %s, %s)', (user.id, user.name, user.date_of_birth))
    elif user.type == 'PJ':
        cursor.execute('INSERT INTO PessoaJuridica (cnpj, razaoSocial, representante, isOrgaoGovernamental) VALUES (%s, %s, %s, %s)', (user.id, user.razao_social, user.representative, user.is_govt))

    db.commit()
    cursor.close()