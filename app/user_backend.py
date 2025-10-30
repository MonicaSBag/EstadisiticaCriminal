from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import os

app = Flask(__name__)

# --- RUTAS DE NAVEGACIÓN Y AUTENTICACIÓN ---
@app.route('/consultar')
def consultar():
    # Redirige a la página de consulta de datos (index.html)
    return render_template('index.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            
            flash(f'Sesión iniciada como {username}. Acceso a la carga de datos concedido.', 'success')
            return redirect(url_for('cargar_datos'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Ambos campos son requeridos.', 'danger')
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe. Por favor, inicie sesión.', 'warning')
            return redirect(url_for('login'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso. ¡Ahora puede iniciar sesión!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/cargar_datos')
def cargar_datos():
    # debería tener un decorador de login_required en producción,
    # pero aquí solo mostramos el contenido.
    return render_template('cargar_datos.html') 

# --- RUTAS DE CONSULTA DE DATOS (Se mantienen) ---

@app.route('/provincias', methods=['GET'])
def listar():
    df = load_data()
    return jsonify(df.to_dict(orient='records'))

@app.route('/filtros', methods=['GET'])
def filtros():
    df = load_data()
    
    filtros = {
        'provincias': sorted(df['Provincia'].dropna().unique().tolist()) if 'Provincia' in df.columns else [],
        'tipos_delito': sorted(df['Tipo Delito'].dropna().unique().tolist()) if 'Tipo Delito' in df.columns else [],
        'generos': sorted(df['Género'].dropna().unique().tolist()) if 'Género' in df.columns else []
    }
    return jsonify(filtros)

@app.route('/filtrar', methods=['POST'])
def filtrar():
    df = load_data()
    filtros = request.get_json()
    
    # Lógica de filtrado
    if filtros.get('provincia'):
        df = df[df['Provincia'] == filtros['provincia']]
    # (El resto de la lógica de filtrado permanece igual)
    
    total_registros = len(df)
    
    # Adaptar las columnas a las reales del BBDD/CSV
    try:
        # Ejemplo de columnas a devolver
        datos_filtrados = df[['provincia_nombre', 'anio', 'codigo_delito_snic_nombre', 'cantidad_hechos']].head(10).to_dict(orient='records')
    except KeyError:
        
        datos_filtrados = df.head(5).to_dict(orient='records')

    return jsonify({'total': total_registros, 'datos': datos_filtrados})


if __name__ == '__main__':
    app.run(debug=True)