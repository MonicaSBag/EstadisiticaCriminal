import sqlite3
from flask import Flask, jsonify, render_template

app = Flask(__name__, template_folder="../templates")

def obtener_conexion():
    return sqlite3.connect('data/estadistica_criminal.db')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/filtros', methods=["GET"])
def filtros():
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT provincia_nombre FROM estadisticas_delitos")
    provincias = [fila[0] for fila in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT codigo_delito_snic_nombre FROM estadisticas_delitos")
    tipos_delito = [fila[0] for fila in cursor.fetchall()]


    conn.close()

    return jsonify({
        "provincias": provincias,
        "tipos_delito": tipos_delito,
    })

