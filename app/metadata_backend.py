import sqlite3
from flask import Flask, jsonify, render_template, request
from setup_database import crear_db, crear_tabla, cargar_archivo
app = Flask(__name__, template_folder="../templates")

# CONEXION A LA BBDD
#def obtener_conexion():
#    return sqlite3.connect('data/estadistica_criminal.db')
crear_db()
crear_tabla()
cargar_archivo()

# RENDER LA PAGINA PRINCIPAL
@app.route('/')
def index():
    return render_template("index.html")

# EXTRAE LA DATA DESDE LA BBDD PARA LOS FILTROS
@app.route('/filtros', methods=["GET"])
def filtros():
    conn = obtener_conexion()
    cursor = conn.cursor()
    # selecciona todas las provincias 
    cursor.execute("SELECT DISTINCT provincia_nombre FROM estadisticas_delitos")
    provincias = [fila[0] for fila in cursor.fetchall()]
    # selecciona todos los delitos
    cursor.execute("SELECT DISTINCT anio FROM estadisticas_delitos")
    anio = [fila[0] for fila in cursor.fetchall()]
    conn.close()
    # devuelve json con los datos para el listado de filtro
    return jsonify({
        "provincias": provincias,
        "anio": anio,
    })
#  busca los datos segun el filtro del usuario
@app.route('/filtrar', methods=["POST"])
def filtrar():
    filtros = request.get_json()
    provincia = filtros.get('provincia')
    anio = filtros.get('anio')

    conn = obtener_conexion()
    cursor = conn.cursor()

    query = "SELECT * FROM estadisticas_delitos WHERE 1=1"
    params = []

    if provincia:
        query += " AND provincia_nombre = ?"
        params.append(provincia)
    if anio:
        query += " AND anio = ?"
        params.append(anio)

    cursor.execute(query, params)
    filas = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    datos = [dict(zip(columnas, fila)) for fila in filas]
    total = len(datos)

    conn.close()
    return jsonify({
        "total": total,
        "datos": datos
    })


# EXTRAE LA DATA DESDE LA BBDD
@app.route('/estadisticas', methods=["POST"])
def estadisticas():
    conn = obtener_conexion()
    cursor = conn.cursor()
    filtros = request.get_json()
    provincia = filtros.get('provincia')
    anio = filtros.get('anio')    
    # selecciona todas las provinicas, cuenta la cant por provincia
    query = """
    SELECT codigo_delito_snic_nombre, COUNT(*) 
    FROM estadisticas_delitos 
    WHERE 1=1
"""
    params = []
    if provincia:
        query += " AND provincia_nombre = ?"
        params.append(provincia)
    if anio:
        query += " AND anio = ?"
        params.append(anio)
    query += " GROUP BY codigo_delito_snic_nombre"
    #params.append(" GROUP BY codigo_delito_snic_nombre")
    cursor.execute(query, params)
    filas = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    datos = [dict(zip(columnas, fila)) for fila in filas]

#    cursor.execute("SELECT provincia_nombre, COUNT(*) FROM estadisticas_delitos GROUP BY provincia_nombre")
#    resultados = cursor.fetchall()
    conn.close()
    # devuelve json con los resultados
    return jsonify(datos) 

