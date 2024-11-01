import app


def get_waterbodydata_by_id(db, waterbody_id):
    """Fetch waterbody details by ID."""
    
    if not db:
        return "error: Failed to connect to database", 500

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CorpoAgua WHERE id = %s", (waterbody_id,))
    waterbody_data = cursor.fetchone()
    
    if not waterbody_data:
        return "error: Waterbody not found", 404
    
    count_complaints = get_count_of_complaints_by_waterbody(waterbody_id)
    count_reports = get_count_of_reports_by_waterbody(waterbody_id)
    media_indice_biodiversidade = get_media_indice_biodiversidade(waterbody_id)
    ph_stats = get_ph_statistics(waterbody_id)
    denuncias_por_severidade = get_denuncias_por_severidade(waterbody_id)

    cursor.close()
    return waterbody_data, count_complaints, count_reports, media_indice_biodiversidade, ph_stats, denuncias_por_severidade

def get_count_of_complaints_by_waterbody(corpo_id):
    """Fetch the count of complaints related to a specific water body."""
    connection = app.get_db()
    if not connection:
        return 0  # Return 0 if connection fails

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT COUNT(d.id) AS total_denuncias
        FROM Denuncia d
        JOIN CorpoAgua ca ON d.corpoReferente = ca.id
        WHERE ca.id = %s;
    """, (corpo_id,))
    
    # Fetch the result
    result = cursor.fetchone()

    cursor.close()
    connection.close()
    
    # Return the count, defaulting to 0 if there are no complaints
    return result['total_denuncias'] if result else 0


def get_count_of_reports_by_waterbody(corpo_id):
    """Fetch count of reports for a specific water body."""
    connection = app.get_db()
    if not connection:
        return 0  # Return 0 if connection fails

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            COUNT(r.id) AS 'Número de Relatórios'
        FROM
            Relatorio r
        JOIN
            CorpoAgua ca ON r.corpoReferente = ca.id
        WHERE
            ca.id = %s;
    """, (corpo_id,))
    
    count_result = cursor.fetchone()  # Fetch the result which will be a single row

    cursor.close()
    connection.close()
    
    return count_result['Número de Relatórios'] if count_result else 0  # Return the count


def get_media_indice_biodiversidade(corpo_id):
    """Fetch average biodiversity index for reports of a specific water body."""
    connection = app.get_db()
    if not connection:
        return None  # Return None if connection fails

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
    return media  # Return the average biodiversity index


def get_ph_statistics(corpo_id):
    """Fetch min, avg, and max pH levels for a specific water body."""
    connection = app.get_db()
    if not connection:
        return None  # Return None if connection fails

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
    return ph_stats  # Return pH statistics


def get_denuncias_por_severidade(corpo_id):
    """Fetch count of complaints by severity for a specific water body."""
    connection = app.get_db()
    if not connection:
        return []  # Return an empty list if connection fails

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
    return severidade_counts  # Return counts by severity
