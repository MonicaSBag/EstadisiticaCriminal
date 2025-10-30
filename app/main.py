import sqlite3
from flask import Flask, jsonify, render_template, request, flash, redirect, url_for
from setup_database import crear_db as crear_db_dataset, BaseModel as BaseModelDataset
from user_database import crear_user_db, BaseModel as BaseModelUser
from werkzeug.security import generate_password_hash

app = Flask(__name__, template_folder="../templates")

# INICIALIZAR BASE DE DATOS AMBAS BASES DE DATOS
crear_db_dataset()
BaseModelDataset.crear_tabla()
BaseModelDataset.cargar_archivo()
crear_user_db()
BaseModelUser.crear_user_tabla()
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_larga_y_segura' # Requerido para flashear mensajes y sesiones

# CONEXION A LA BBDD
def obtener_conexion_dataset():
    try:
        return sqlite3.connect('data/estadistica_criminal.db')
    except:
        print("No se pudo conectar con la base de datos")

def obtener_conexion_user():
    try:
        return sqlite3.connect('data/users.db')
    except:
        print("No se pudo conectar con la base de datos")


# RENDER LA PAGINA PRINCIPAL
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = obtener_conexion_user()
    #cursor = conn.cursor()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = BaseModelUser.get(BaseModelUser.username == username)
        if user and user.check_password(password):
            flash(f'Sesión iniciada como {username}. Acceso a la carga de datos concedido.', 'success')
            return redirect("segundo iframe de filtros el que permite crud")
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = obtener_conexion_user()
    #cursor = conn.cursor()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Ambos campos son requeridos.', 'danger')
            return redirect(url_for('register'))
        try:
            if BaseModelUser.get(BaseModelUser.username == username):
                flash('El usuario ya existe. Por favor, inicie sesión.', 'warning')
                return redirect(url_for('login'))
        except:
            BaseModelUser.create(
                username = username,
                provincia_nombre = "",
                password_hash = generate_password_hash(password) 
            )    
            flash('Registro exitoso. ¡Ahora puede iniciar sesión!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


# EXTRAE LA DATA DESDE LA BBDD PARA LOS FILTROS
@app.route('/filtros', methods=["GET"])
def filtros():
    conn = obtener_conexion_dataset()
    cursor = conn.cursor()
    
    # Selecciona todas las provincias 
    cursor.execute("SELECT DISTINCT provincia_nombre FROM estadisticas_delitos ORDER BY provincia_nombre")
    provincias = [fila[0] for fila in cursor.fetchall()]
    
    # Selecciona todos los años
    cursor.execute("SELECT DISTINCT anio FROM estadisticas_delitos ORDER BY anio")
    anio = [fila[0] for fila in cursor.fetchall()]
    
    # Selecciona todos los años
    cursor.execute("SELECT DISTINCT codigo_delito_snic_nombre FROM estadisticas_delitos ORDER BY codigo_delito_snic_nombre")
    delito = [fila[0] for fila in cursor.fetchall()]

    conn.close()
    
    # Devuelve json con los datos para el listado de filtro
    return jsonify({
        "provincias": provincias,
        "anio": anio,
        "codigo_delito_snic_nombre" : delito,
    })

# BUSCA LOS DATOS SEGUN EL FILTRO DEL USUARIO
@app.route('/filtrar', methods=["POST"])
def filtrar():
    filtros = request.get_json()
    provincia = filtros.get('provincia')
    anio = filtros.get('anio')
    delito = filtros.get('codigo_delito_snic_nombre')

    conn = obtener_conexion_dataset()
    cursor = conn.cursor()

    query = "SELECT * FROM estadisticas_delitos WHERE 1=1"
    params = []

    if provincia:
        query += " AND provincia_nombre = ?"
        params.append(provincia)
    if anio:
        query += " AND anio = ?"
        params.append(anio)
    if delito:
        query += " AND codigo_delito_snic_nombre = ?"
        params.append(delito)

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
@app.route('/dashboard-public')
def dash_public():
    return render_template("iFrame_filtros_prueba1.html")
# EXTRAE ESTADÍSTICAS AGRUPADAS
@app.route('/estadisticas', methods=["POST"])
def estadisticas():
    conn = obtener_conexion_dataset()
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