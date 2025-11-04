import sqlite3
from flask import Flask, jsonify, render_template, request, flash, redirect, session
from setup_database import crear_db as crear_db_dataset, EstadisticasDelitos, Provincia, cargar_archivo, crear_tabla
from user_database import crear_user_tabla, User
from werkzeug.security import check_password_hash
from functools import wraps

app = Flask(__name__, template_folder="../templates")
# INICIALIZAR BASE DE DATOS AMBAS BASES DE DATOS
crear_db_dataset()
crear_tabla()
cargar_archivo()
crear_user_tabla()
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# RENDER LESTRUCTURA DE LAS PAGINAS
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user = User.get(User.username == username)
        except User.DoesNotExist:
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('login.html')
        
        if check_password_hash(user.password_hash, password):  # o check_password(user.password, password)
            session['user_id'] = user.id
            session['tipo_user'] = user.tipo_usuario_id
            session['provincia_nombre'] = user.provincia_nombre 
            
            if user.tipo_usuario_id == 2:
                flash(f'Sesión iniciada como {username}. Acceso a la carga de datos concedido.', 'success')
                return redirect("/dashboard-private")
            elif user.tipo_usuario_id == 1:
                flash(f'Sesión iniciada como {username}.', 'success')
                return redirect("/dashboard-private")  # RUTA A PAGINA DE SUPERUSUARIO

        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('login.html')

"""@app.route('/register', methods=['GET', 'POST'])
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
            if User.get(User.username == username):
                flash('El usuario ya existe. Por favor, inicie sesión.', 'warning')
                return redirect(url_for('login'))
        except:
            User.create(
                username = username,
                provincia_nombre = "",
                password_hash = generate_password_hash(password) 
            )    
            flash('Registro exitoso. ¡Ahora puede iniciar sesión!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')"""

@app.route('/filtros', methods=["GET"])
@login_required
def filtros():
    tipo_user = session.get('tipo_user')
    conn = obtener_conexion_dataset()
    cursor = conn.cursor()

    # Provincias: si es superusuario, muestra todas; si no, usa la que está en sesión
    if tipo_user == 1:
        cursor.execute("SELECT DISTINCT provincia_nombre FROM estadisticasdelitos ORDER BY provincia_nombre")
        provincias = [fila[0] for fila in cursor.fetchall()]
    else:
        provincia_nombre = session.get('provincia_nombre')
        provincias = [provincia_nombre] if provincia_nombre else []

    # Años disponibles
    cursor.execute("SELECT DISTINCT anio FROM estadisticasdelitos ORDER BY anio")
    anio = [fila[0] for fila in cursor.fetchall()]

    # Delitos disponibles
    cursor.execute("SELECT DISTINCT codigo_delito_snic_nombre FROM estadisticasdelitos ORDER BY codigo_delito_snic_nombre")
    delito = [fila[0] for fila in cursor.fetchall()]

    conn.close()

    return jsonify({
        "provincias": provincias,
        "anio": anio,
        "codigo_delito_snic_nombre": delito,
    })

@app.route('/filtros2', methods=["GET"])
def filtros2():
    conn = obtener_conexion_dataset()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT provincia_nombre FROM estadisticasdelitos ORDER BY provincia_nombre")
    provincias = [fila[0] for fila in cursor.fetchall()]


    # Años disponibles
    cursor.execute("SELECT DISTINCT anio FROM estadisticasdelitos ORDER BY anio")
    anio = [fila[0] for fila in cursor.fetchall()]

    # Delitos disponibles
    cursor.execute("SELECT DISTINCT codigo_delito_snic_nombre FROM estadisticasdelitos ORDER BY codigo_delito_snic_nombre")
    delito = [fila[0] for fila in cursor.fetchall()]

    conn.close()

    return jsonify({
        "provincias": provincias,
        "anio": anio,
        "codigo_delito_snic_nombre": delito,
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

    query = "SELECT * FROM estadisticasdelitos WHERE 1=1"
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
    return render_template("components/iFrame_filtros_prueba1.html")

@app.route('/dashboard-private')
@login_required
def dash_private():
    return render_template("components/iFrame_filtros_prueba2.html")

@app.route("/nuevo-registro", methods=["POST", "GET"])
@login_required
def nuevo_registro():
    if request.method == 'POST':
        provincia_nomb = request.form.get('provincia_modal')
        tipo_delito = request.form.get('codigo_delito_snic_nombre_modal')
        anio = request.form.get('anio_modal')
        cantidad_hechos = request.form.get('hechos')
        cantidad_victimas = request.form.get('victimas_total')
        cantidad_victimas_masc = request.form.get('victimas_masc')
        cantidad_victimas_fem = request.form.get('victimas_fem')
        cantidad_victimas_sd = request.form.get('victimas_sd')
    registro = Provincia.get(Provincia.provincia_nombre == provincia_nomb)
    registro2 = EstadisticasDelitos.get(EstadisticasDelitos.codigo_delito_snic_nombre == tipo_delito)
    EstadisticasDelitos.create(
        codigo_delito_snic_id = registro2.codigo_delito_snic_id,
        provincia_nombre = provincia_nomb,
        provincia_id = registro.provincia_id,
        anio = anio,
        codigo_delito_snic_nombre = tipo_delito,
        cantidad_hechos = cantidad_hechos,
        cantidad_victimas = cantidad_victimas,
        cantidad_victimas_masc = cantidad_victimas_masc,
        cantidad_victimas_fem = cantidad_victimas_fem,
        cantidad_victimas_sd = cantidad_victimas_sd
    )    
    return redirect("/dashboard-private")

@app.route("/eliminar-registro", methods=["POST", "GET"])
@login_required
def eliminar_registro():
    id_registro = request.form.get('registro_a_eliminar')
    try:
        registro = EstadisticasDelitos.get_by_id(id_registro)
        registro.delete_instance()
    except EstadisticasDelitos.DoesNotExist:
        print("No se encontró el registro con ese ID.")
    except Exception as e:
        print(f"Error al eliminar el registro: {str(e)}")

    return redirect("/dashboard-private")

@app.route('/consultar-registro', methods=['POST'])
def consultar_registro():
    id_registro = request.json.get('registro_id')
    try:
        registro = EstadisticasDelitos.get_by_id(id_registro)
        datos = {
            "ID": registro.id,
            "Provincia": registro.provincia_nombre,
            "Año": registro.anio,
            "Delito": registro.codigo_delito_snic_nombre,
            "Hechos": registro.cantidad_hechos,
            "Víctimas": registro.cantidad_victimas
        }
        return jsonify({"datos": [datos]})
    except EstadisticasDelitos.DoesNotExist:
        return jsonify({"datos": []})

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
        FROM estadisticasdelitos 
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