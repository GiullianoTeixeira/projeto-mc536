from flask import Flask, jsonify, render_template, request
import mysql.connector
from mysql.connector import Error

app = app = Flask(__name__, template_folder='templates')

# Hosted Database configuration
db_config = {
    'user': 'sql10740190',
    'password': 'IZKjQhSf19',
    'host': 'sql10.freesqldatabase.com',
    'database': 'sql10740190'
}

def get_db_connection():
    """Establishes a new database connection."""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/denuncias/usuario/<string:cpf>', methods=['GET'])
def get_denuncias_por_usuario(cpf):
    """Fetch all complaints made by a specific individual."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            d.id AS 'ID da Denúncia',
            d.datahora AS 'Data e Hora',
            ca.nome AS 'Nome do Corpo de Água',
            d.categoria AS 'Categoria da Denúncia',
            d.severidade AS 'Severidade',
            d.descricao AS 'Descrição'
        FROM 
            Denuncia d
        JOIN 
            PessoaFisica pf ON d.denunciante = pf.cpf
        JOIN 
            CorpoAgua ca ON d.corpoReferente = ca.id
        WHERE 
            pf.cpf = %s;
    """, (cpf,))
    denuncias = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(denuncias)

@app.route('/denuncias/corpo/<int:corpo_id>', methods=['GET'])
def get_denuncias_por_corpo(corpo_id):
    """Fetch all complaints related to a specific water body."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            d.id AS 'ID da Denúncia',
            pf.nome AS 'Nome do Denunciante',
            d.datahora AS 'Data e Hora',
            d.categoria AS 'Categoria da Denúncia',
            d.severidade AS 'Severidade',
            d.descricao AS 'Descrição'
        FROM
            Denuncia d
        JOIN
            PessoaFisica pf ON d.denunciante = pf.cpf
        JOIN
            CorpoAgua ca ON d.corpoReferente = ca.id
        WHERE
            ca.id = %s;
    """, (corpo_id,))
    denuncias = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(denuncias)

@app.route('/relatorios/corpo/<int:corpo_id>', methods=['GET'])
def get_relatorios_por_corpo(corpo_id):
    """Fetch all reports for a specific water body."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            r.id AS 'ID do Relatório',
            pj.razaoSocial AS 'Entidade Emissora',
            r.datahora AS 'Data e Hora',
            r.texto AS 'Texto do Relatório',
            r.pH AS 'pH da Água',
            r.indiceBiodiversidade AS 'Índice de Biodiversidade'
        FROM
            Relatorio r
        JOIN
            PessoaJuridica pj ON r.entidadeEmissora = pj.cnpj
        JOIN
            CorpoAgua ca ON r.corpoReferente = ca.id
        WHERE
            ca.id = %s;
    """, (corpo_id,))
    relatorios = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(relatorios)

@app.route('/relatorios/indice_biodiversidade/<int:corpo_id>', methods=['GET'])
def get_media_indice_biodiversidade(corpo_id):
    """Fetch average biodiversity index for reports of a specific water body."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            ca.nome AS 'Nome do Corpo de Água',
            AVG(r.indiceBiodiversidade) AS 'Média do Índice de Biodiversidade'
        FROM
            Relatorio r
        JOIN
            CorpoAgua ca ON r.corpoReferente = ca.id
        WHERE
            ca.id = %s 
        GROUP BY
            ca.nome;
    """, (corpo_id,))
    media = cursor.fetchone()

    cursor.close()
    connection.close()
    return jsonify(media)

@app.route('/relatorios/ph/<int:corpo_id>', methods=['GET'])
def get_ph_statistics(corpo_id):
    """Fetch min, avg, and max pH levels for a specific water body."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            ca.nome AS 'Nome do Corpo de Água',
            MIN(r.pH) AS 'pH Mínimo',
            AVG(r.pH) AS 'pH Médio',
            MAX(r.pH) AS 'pH Máximo'
        FROM
            Relatorio r
        JOIN
            CorpoAgua ca ON r.corpoReferente = ca.id
        WHERE
            ca.id = %s 
        GROUP BY
            ca.nome;
    """, (corpo_id,))
    ph_stats = cursor.fetchone()

    cursor.close()
    connection.close()
    return jsonify(ph_stats)

@app.route('/denuncias/severidade/<int:corpo_id>', methods=['GET'])
def get_denuncias_por_severidade(corpo_id):
    """Fetch count of complaints by severity for a specific water body."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            ca.nome AS 'Nome do Corpo de Água',
            d.severidade AS 'Severidade',
            COUNT(d.id) AS 'Número de Denúncias'
        FROM
            Denuncia d
        JOIN
            CorpoAgua ca ON d.corpoReferente = ca.id
        WHERE
            ca.id = %s  
        GROUP BY
            d.severidade, ca.nome;
    """, (corpo_id,))
    severidade_counts = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(severidade_counts)

@app.route('/solucoes/entidade/<string:razao_social>', methods=['GET'])
def get_solucoes_por_entidade(razao_social):
    """Fetch all proposed solutions by a specific issuing entity."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            pj.razaoSocial AS 'Entidade Emissora',
            s.id AS 'ID da Solução',
            s.orcamento AS 'Orçamento',
            ca.nome AS 'Nome do Corpo de Água',
            s.descricao AS 'Descrição da Solução'
        FROM
            Solucao s
        JOIN
            PessoaJuridica pj ON s.entidadeEmissora = pj.cnpj
        JOIN
            CorpoAgua ca ON s.corpoReferente = ca.id
        WHERE
            pj.razaoSocial = %s; 
    """, (razao_social,))
    solucoes = cursor.fetchall()

    cursor.close()
    connection.close()
    return jsonify(solucoes)

if __name__ == '__main__':
    app.run(debug=True)