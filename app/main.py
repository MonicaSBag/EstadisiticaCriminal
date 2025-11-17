import sqlite3
from flask import Flask, jsonify, render_template, request, flash, redirect, session, url_for
from setup_database import crear_db as crear_db_dataset, EstadisticasDelitos, Provincia, cargar_archivo, crear_tabla
from user_database import crear_user_tabla, User, TipoUsuario, verificar_o_agregar_campo
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__, template_folder="../templates")
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_larga_y_segura'

# INICIALIZAR BASES DE DATOS
crear_db_dataset()
crear_tabla()
cargar_archivo()
crear_user_tabla()

# CONEXIÓN A LA BBDD
def obtener_conexion_dataset():
    return sqlite3.connect('data/estadistica_criminal.db')

def obtener_conexion_user():
    return sqlite3.connect('data/users.db')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# RUTAS
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 1️⃣ Verificar usuario
        try:
            user = User.get(User.username == username)
        except User.DoesNotExist:
            flash("❌ El usuario no existe.", "danger")
            return redirect(url_for('login'))

        # 2️⃣ Verificar contraseña
        if not check_password_hash(user.password_hash, password):
            flash("❌ Contraseña incorrecta.", "danger")
            return redirect(url_for('login'))

        # 3️⃣ Logueo correcto
        session['user_id'] = user.id
        session['tipo_user'] = user.tipo_usuario_id
        session['provincia_nombre'] = user.provincia_nombre

        # 4️⃣ Obligado a cambiar pass
        if user.debe_cambiar_password:
            return redirect(url_for('cambiar_password_primera_vez'))

        # 5️⃣ Redirección por rol
        if user.tipo_usuario_id == 2:
            return redirect("/dashboard-private")
        elif user.tipo_usuario_id == 1:
            return redirect("/portal_admin")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route("/login_admin", methods=["POST"])
def login_admin():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    try:
        user = User.get(User.username == username)
    except User.DoesNotExist:
        return jsonify({"success": False, "msg": "Usuario no encontrado ❌"})

    if check_password_hash(user.password_hash, password) and user.tipo_usuario_id == 1:
        session["user_id"] = user.id
        session["tipo_user"] = user.tipo_usuario_id
        return jsonify({"success": True, "msg": "Login correcto ✅"})
    else:
        return jsonify({"success": False, "msg": "Acceso denegado ❌ Solo el superAdmin puede ingresar."})

@app.route('/filtros', methods=["GET"])
@login_required
def filtros():
    tipo_user = session.get('tipo_user')
    conn = obtener_conexion_dataset()
    cursor = conn.cursor()

    if tipo_user == 1:
        cursor.execute("SELECT DISTINCT provincia_nombre FROM estadisticasdelitos ORDER BY provincia_nombre")
        provincias = [fila[0] for fila in cursor.fetchall()]
    else:
        provincia_nombre = session.get('provincia_nombre')
        provincias = [provincia_nombre] if provincia_nombre else []

    cursor.execute("SELECT DISTINCT anio FROM estadisticasdelitos ORDER BY anio")
    anio = [fila[0] for fila in cursor.fetchall()]

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

    cursor.execute("SELECT DISTINCT anio FROM estadisticasdelitos ORDER BY anio")
    anio = [fila[0] for fila in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT codigo_delito_snic_nombre FROM estadisticasdelitos ORDER BY codigo_delito_snic_nombre")
    delito = [fila[0] for fila in cursor.fetchall()]

    conn.close()

    return jsonify({
        "provincias": provincias,
        "anio": anio,
        "codigo_delito_snic_nombre": delito,
    })

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
    conn.close()
    
    return jsonify({
        "total": len(datos),
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
        try:
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
                codigo_delito_snic_id=registro2.codigo_delito_snic_id,
                provincia_nombre=provincia_nomb,
                provincia_id=registro.provincia_id,
                anio=anio,
                codigo_delito_snic_nombre=tipo_delito,
                cantidad_hechos=cantidad_hechos,
                cantidad_victimas=cantidad_victimas,
                cantidad_victimas_masc=cantidad_victimas_masc,
                cantidad_victimas_fem=cantidad_victimas_fem,
                cantidad_victimas_sd=cantidad_victimas_sd
            )
            flash("Registro agregado correctamente.", "success")
        except Exception as e:
            flash(f"Error al agregar el registro: {str(e)}", "danger")
        
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

@app.route('/estadisticas', methods=["POST"])
def estadisticas():
    conn = obtener_conexion_dataset()
    cursor = conn.cursor()
    
    filtros = request.get_json() or {}
    provincia = filtros.get('provincia')
    anio = filtros.get('anio')    
    
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
    
    return jsonify(datos)

@app.route("/portal_admin")
def portal_admin():
    if session.get("tipo_user") == 1:
        return render_template("PortalAdmin.html")
    else:
        flash("Acceso denegado ❌ Solo el superAdmin puede ingresar.")
        return redirect("/")

# ABM DE USUARIOS
@app.route("/usuarios")
@login_required
def usuarios():
    if session.get("tipo_user") != 1:
        flash("Acceso denegado ❌ Solo el superAdmin puede ingresar.")
        return redirect("/")

    usuarios = User.select(User, TipoUsuario).join(TipoUsuario)
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/usuarios/agregar", methods=["POST"])
@login_required
def agregar_usuario():
    if session.get("tipo_user") != 1:
        return jsonify({"success": False, "msg": "Acceso denegado ❌"})
    
    data = request.get_json()
    username = data.get("username")
    provincia = data.get("provincia_nombre")
    password = data.get("password")
    tipo = data.get("tipo_usuario")

    try:
        tipo_obj = TipoUsuario.get(TipoUsuario.tipo_usuario == tipo)
        User.create(
            username=username,
            provincia_nombre=provincia,
            password_hash=generate_password_hash(password),
            debe_cambiar_password=True,
            tipo_usuario=tipo_obj,
        )
        return jsonify({"success": True, "msg": "Usuario agregado ✅"})
    except Exception as e:
        return jsonify({"success": False, "msg": f"Error: {str(e)}"})

@app.route("/usuarios/editar/<int:id>", methods=["POST"])
@login_required
def editar_usuario(id):
    if session.get("tipo_user") != 1:
        return jsonify({"success": False, "msg": "Acceso denegado ❌"})
    
    data = request.get_json()
    username = data.get("username")
    provincia = data.get("provincia_nombre")
    tipo = data.get("tipo_usuario")

    try:
        user = User.get_by_id(id)
        tipo_obj = TipoUsuario.get(TipoUsuario.tipo_usuario == tipo)
        user.username = username
        user.provincia_nombre = provincia
        user.tipo_usuario = tipo_obj
        user.save()
        return jsonify({"success": True, "msg": "Usuario actualizado ✅"})
    except Exception as e:
        return jsonify({"success": False, "msg": f"Error: {str(e)}"})

@app.route("/usuarios/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_usuario(id):
    if session.get("tipo_user") != 1:
        return jsonify({"success": False, "msg": "Acceso denegado ❌"})
    
    try:
        user = User.get_by_id(id)
        user.delete_instance()
        return jsonify({"success": True, "msg": "Usuario eliminado ✅"})
    except Exception as e:
        return jsonify({"success": False, "msg": f"Error: {str(e)}"})

@app.route("/usuarios/set_password/<int:id>", methods=["POST"])
@login_required
def set_password(id):
    if session.get("tipo_user") != 1:
        return jsonify({"success": False, "msg": "Acceso denegado ❌"})

    data = request.get_json() or {}
    nueva_password = data.get("password")

    if not nueva_password:
        return jsonify({"success": False, "msg": "Debe ingresar una nueva contraseña."})

    try:
        user = User.get_by_id(id)
        user.password_hash = generate_password_hash(nueva_password)
        user.debe_cambiar_password = True
        user.save()

        return jsonify({
            "success": True,
            "msg": f"Contraseña actualizada correctamente para {user.username} ✅ (deberá cambiarla al iniciar sesión)"
        })
    except User.DoesNotExist:
        return jsonify({"success": False, "msg": "Usuario no encontrado ❌"})
    except Exception as e:
        return jsonify({"success": False, "msg": f"Error al cambiar la contraseña: {str(e)}"})

@app.route('/cambiar_password_primera_vez', methods=['GET', 'POST'])
@login_required
def cambiar_password_primera_vez():
    user_id = session.get('user_id')
    if not user_id:
        flash("Debe iniciar sesión primero.", "warning")
        return redirect(url_for('login'))

    user = User.get_by_id(user_id)

    if request.method == 'POST':
        nueva = request.form.get('nueva_password')
        confirmar = request.form.get('confirmar_password')

        if not nueva or not confirmar:
            flash("Debe completar ambos campos.", "warning")
            return redirect(url_for('cambiar_password_primera_vez'))

        if nueva != confirmar:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for('cambiar_password_primera_vez'))

        user.password_hash = generate_password_hash(nueva)
        user.debe_cambiar_password = False
        user.save()

        flash("Contraseña actualizada correctamente ✅", "success")

        if user.tipo_usuario_id == 1:
            return redirect("/portal_admin")
        else:
            return redirect("/dashboard-private")

    return render_template('cambiar_password_primera_vez.html', user=user)

# ABM AVANZADO
def calcular_tasas(cantidad_hechos, cantidad_victimas, cantidad_victimas_masc, cantidad_victimas_fem):
    """Calcula las tasas basadas en las cantidades ingresadas"""
    return {
        'tasa_hechos': cantidad_hechos if cantidad_hechos > 0 else 0,
        'tasa_victimas': cantidad_victimas if cantidad_victimas > 0 else 0,
        'tasa_victimas_masc': cantidad_victimas_masc if cantidad_victimas_masc > 0 else 0,
        'tasa_victimas_fem': cantidad_victimas_fem if cantidad_victimas_fem > 0 else 0
    }

@app.route('/abm/consultar', methods=["POST"])
@login_required
def abm_consultar():
    filtros = request.get_json()
    provincia = filtros.get('provincia')
    anio = filtros.get('anio')
    delito = filtros.get('delito')
    
    tipo_user = session.get('tipo_user')
    
    if tipo_user != 1:
        provincia_sesion = session.get('provincia_nombre')
        if provincia and provincia != provincia_sesion:
            return jsonify({"success": False, "msg": "Acceso denegado a esa provincia", "datos": []})
        provincia = provincia_sesion
    
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
    conn.close()
    
    return jsonify({
        "success": True,
        "total": len(datos),
        "datos": datos
    })

@app.route('/abm/agregar', methods=["POST"])
@login_required
def abm_agregar():
    tipo_user = session.get('tipo_user')
    provincia_sesion = session.get('provincia_nombre')
    
    data = request.get_json()
    
    campos_requeridos = ['provincia', 'anio', 'delito', 'cantidad_hechos', 
                         'cantidad_victimas', 'cantidad_victimas_masc', 
                         'cantidad_victimas_fem', 'cantidad_victimas_sd']
    
    for campo in campos_requeridos:
        if campo not in data or data[campo] == '' or data[campo] is None:
            return jsonify({"success": False, "msg": f"Campo requerido: {campo}"})
    
    try:
        cantidad_hechos = int(data['cantidad_hechos'])
        cantidad_victimas = int(data['cantidad_victimas'])
        cantidad_victimas_masc = int(data['cantidad_victimas_masc'])
        cantidad_victimas_fem = int(data['cantidad_victimas_fem'])
        cantidad_victimas_sd = int(data['cantidad_victimas_sd'])
    except ValueError:
        return jsonify({"success": False, "msg": "Todos los campos numéricos deben ser números"})
    
    if tipo_user != 1 and data['provincia'] != provincia_sesion:
        return jsonify({"success": False, "msg": "Acceso denegado a esa provincia"})
    
    try:
        registro_provincia = Provincia.get(Provincia.provincia_nombre == data['provincia'])
        registro_delito = EstadisticasDelitos.get(EstadisticasDelitos.codigo_delito_snic_nombre == data['delito'])
        
        tasas = calcular_tasas(cantidad_hechos, cantidad_victimas, cantidad_victimas_masc, cantidad_victimas_fem)
        
        EstadisticasDelitos.create(
            codigo_delito_snic_id=registro_delito.codigo_delito_snic_id,
            provincia_nombre=data['provincia'],
            provincia_id=registro_provincia.provincia_id,
            anio=data['anio'],
            codigo_delito_snic_nombre=data['delito'],
            cantidad_hechos=cantidad_hechos,
            cantidad_victimas=cantidad_victimas,
            cantidad_victimas_masc=cantidad_victimas_masc,
            cantidad_victimas_fem=cantidad_victimas_fem,
            cantidad_victimas_sd=cantidad_victimas_sd,
            tasa_hechos=tasas['tasa_hechos'],
            tasa_victimas=tasas['tasa_victimas'],
            tasa_victimas_masc=tasas['tasa_victimas_masc'],
            tasa_victimas_fem=tasas['tasa_victimas_fem']
        )
        
        return jsonify({"success": True, "msg": "Registro agregado correctamente ✅"})
    except Exception as e:
        return jsonify({"success": False, "msg": f"Error: {str(e)}"})

@app.route('/abm/eliminar/<int:id>', methods=["DELETE"])
@login_required
def abm_eliminar(id):
    tipo_user = session.get('tipo_user')
    provincia_sesion = session.get('provincia_nombre')

    try:
        registro = EstadisticasDelitos.get_by_id(id)

        if tipo_user != 1 and registro.provincia_nombre != provincia_sesion:
            return jsonify({"success": False, "msg": "Acceso denegado a ese registro"})

        registro.delete_instance()
        return jsonify({"success": True, "msg": "Registro eliminado exitosamente ✅"})
    except EstadisticasDelitos.DoesNotExist:
        return jsonify({"success": False, "msg": "Registro no encontrado ❌"})
    except Exception as e:
        return jsonify({"success": False, "msg": f"Error al eliminar: {str(e)}"})

if __name__ == "__main__":
    crear_user_tabla()
    verificar_o_agregar_campo()
    app.run(debug=True)