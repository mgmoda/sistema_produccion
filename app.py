from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Ruta principal
@app.route('/')
def home():
    return redirect(url_for('ver_referencias'))

# Ver todas las referencias
@app.route('/ver-referencias')
def ver_referencias():
    conn = sqlite3.connect('avances.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM referencias')
    referencias = cursor.fetchall()
    conn.close()
    return render_template('tabla.html', referencias=referencias)

# Ruta para actualizar los datos desde el modal
@app.route('/actualizar', methods=['POST'])
def actualizar():
    id = request.form['id']
    pedido_tela = request.form['pedido_tela']
    fecha_estampacion = request.form['fecha_estampacion']

    # Calcular días transcurridos
    if fecha_estampacion:
        fecha_envio = datetime.strptime(fecha_estampacion, '%Y-%m-%d')
        hoy = datetime.today()
        dias_estampacion = (hoy - fecha_envio).days
    else:
        dias_estampacion = None

    conn = sqlite3.connect('avances.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE referencias
        SET pedido_tela = ?, fecha_estampacion = ?, dias_estampacion = ?
        WHERE id = ?
    ''', (pedido_tela, fecha_estampacion, dias_estampacion, id))
    conn.commit()
    conn.close()

    return redirect(url_for('ver_referencias'))

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=False, host='0.0.0.0', port=port)