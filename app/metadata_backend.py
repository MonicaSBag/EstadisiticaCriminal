import sqlite3
from flask import Flask, jsonify, render_template, request
from setup_database import crear_db, BaseModel

app = Flask(__name__, template_folder="../templates")

# INICIALIZAR BASE DE DATOS
crear_db()
BaseModel.crear_tabla()
BaseModel.cargar_archivo()

# CONEXION A LA BBDD
def obtener_conexion():
    return sqlite3.connect('data/estadistica_criminal.db')

# RENDER LA PAGINA PRINCIPAL
@app.route('/')
def index():
    return render_template("index.html")

# EXTRAE LA DATA DESDE LA BBDD PARA LOS FILTROS
@app.route('/filtros', methods=["GET"])
def filtros():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Selecciona todas las provincias 
    cursor.execute("SELECT DISTINCT provincia_nombre FROM estadisticas_delitos ORDER BY provincia_nombre")
    provincias = [fila[0] for fila in cursor.fetchall()]
    
    # Selecciona todos los años
    cursor.execute("SELECT DISTINCT anio FROM estadisticas_delitos ORDER BY anio")
    anio = [fila[0] for fila in cursor.fetchall()]
    
    conn.close()
    
    # Devuelve json con los datos para el listado de filtro
    return jsonify({
        "provincias": provincias,
        "anio": anio,
    })

# BUSCA LOS DATOS SEGUN EL FILTRO DEL USUARIO
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

# EXTRAE ESTADÍSTICAS AGRUPADAS
@app.route('/estadisticas', methods=["POST"])
def estadisticas():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    filtros = request.get_json() or {}
    provincia = filtros.get('provincia')
    anio = filtros.get('anio')    
    
    # Selecciona delitos y cuenta cantidad por tipo
    query = """
        SELECT codigo_delito_snic_nombre, COUNT(*) as cantidad
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
    
    query += " GROUP BY codigo_delito_snic_nombre ORDER BY cantidad DESC"
    
    cursor.execute(query, params)
    filas = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    datos = [dict(zip(columnas, fila)) for fila in filas]
    
    conn.close()
    # Devuelve json con los resultados
    return jsonify(datos)

if __name__ == '__main__':
    app.run(debug=True)