from flask import Flask, jsonify, request, render_template
import pandas as pd
import os

app = Flask(__name__)

EXCEL_FILE = "snic-provincias.xlsx"

def load_data():
    return pd.read_excel(EXCEL_FILE)

@app.route('/')
def home():
    return render_template('index.html')

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
    if filtros.get('provincia'):
        df = df[df['Provincia'] == filtros['provincia']]
    if filtros.get('tipo_delito'):
        df = df[df['Tipo Delito'] == filtros['tipo_delito']]
    if filtros.get('genero'):
        df = df[df['Género'] == filtros['genero']]

    total = len(df)
    return jsonify({'total': total, 'datos': df.to_dict(orient='records')})

if __name__ == '__main__':
    app.run(debug=True)
