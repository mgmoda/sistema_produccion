from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Base de datos para producción (ordenes, procesos)
DB_PRODUCCION = 'produccion.db'
# Base de datos para avances y referencias
DB_AVANCES = 'avances.db'

# Función para ejecutar consultas en producción

def ejecutar_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_PRODUCCION)
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# Ruta raíz
@app.route('/')
def home():
    return redirect(url_for('menu'))

# Menú principal
@app.route('/menu')
def menu():
    return render_template('menu.html')

# Ver referencias (usando avances.db)
@app.route('/ver-referencias')
def ver_referencias():
    conn = sqlite3.connect(DB_AVANCES)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM referencias')
    referencias = cursor.fetchall()
    conn.close()
    return render_template('tabla.html', referencias=referencias)

# Actualizar campos de una referencia (desde modal)
@app.route('/actualizar', methods=['POST'])
def actualizar():
    id = request.form['id']
    pedido_tela = request.form['pedido_tela']
    fecha_estampacion = request.form['fecha_estampacion']

    dias_estampacion = None
    if fecha_estampacion:
        fecha_envio = datetime.strptime(fecha_estampacion, '%Y-%m-%d')
        hoy = datetime.today()
        dias_estampacion = (hoy - fecha_envio).days

    conn = sqlite3.connect(DB_AVANCES)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE referencias
        SET pedido_tela = ?, fecha_estampacion = ?, dias_estampacion = ?
        WHERE id = ?
    ''', (pedido_tela, fecha_estampacion, dias_estampacion, id))
    conn.commit()
    conn.close()

    return redirect(url_for('ver_referencias'))

# Crear nueva orden de corte
@app.route('/nueva_orden', methods=['GET', 'POST'])
def nueva_orden():
    if request.method == 'POST':
        referencia_id = request.form['referencia_id']
        cantidad = request.form['cantidad']
        observaciones = request.form.get('observaciones', '')

        ejecutar_query('''INSERT INTO ordenes_corte (referencia_id, cantidad, observaciones) 
                          VALUES (?, ?, ?)''', (referencia_id, cantidad, observaciones))

        orden_id = ejecutar_query('SELECT last_insert_rowid()', fetch=True)[0][0]

        procesos = [('Pedido de Tela',), ('Corte',)]

        requiere_estampado = ejecutar_query('''
            SELECT requiere_estampado FROM referencias WHERE id = ?
        ''', (referencia_id,), fetch=True)[0][0]

        if requiere_estampado:
            procesos.insert(1, ('Estampación',))

        for proceso in procesos:
            ejecutar_query('''INSERT INTO procesos_orden (orden_id, tipo_proceso) VALUES (?, ?)''', (orden_id, proceso[0]))

        return redirect(url_for('ordenes'))

    referencias = ejecutar_query('SELECT id, referencia, descripcion FROM referencias', fetch=True)
    return render_template('nueva_orden.html', referencias=referencias)

# Ver órdenes creadas
@app.route('/ordenes')
def ordenes():
    datos = ejecutar_query('''
        SELECT o.id, r.referencia, o.cantidad, o.fecha_creacion
        FROM ordenes_corte o
        JOIN referencias r ON o.referencia_id = r.id
        ORDER BY o.fecha_creacion DESC
    ''', fetch=True)
    return render_template('ordenes.html', ordenes=datos)

# Ejecutar servidor
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)