from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB = 'produccion.db'

def ejecutar_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

@app.route('/nueva_orden', methods=['GET', 'POST'])
def nueva_orden():
    if request.method == 'POST':
        referencia_id = request.form['referencia_id']
        cantidad = request.form['cantidad']
        observaciones = request.form.get('observaciones', '')

        # Insertar orden de corte
        query = '''INSERT INTO ordenes_corte (referencia_id, cantidad, observaciones) 
                   VALUES (?, ?, ?)'''
        ejecutar_query(query, (referencia_id, cantidad, observaciones))

        # Obtener ID de la orden creada
        orden_id = ejecutar_query('SELECT last_insert_rowid()', fetch=True)[0][0]

        # Procesos base
        procesos = [('Pedido de Tela',), ('Corte',)]

        # Verificar si requiere estampación
        requiere_estampado = ejecutar_query('SELECT requiere_estampado FROM referencias WHERE id = ?', (referencia_id,), fetch=True)[0][0]
        if requiere_estampado:
            procesos.insert(1, ('Estampación',))

        for proceso in procesos:
            ejecutar_query('''INSERT INTO procesos_orden (orden_id, tipo_proceso) VALUES (?, ?)''', (orden_id, proceso[0]))

        return redirect(url_for('ordenes'))

    referencias = ejecutar_query('SELECT id, referencia, descripcion FROM referencias', fetch=True)
    return render_template('nueva_orden.html', referencias=referencias)

@app.route('/ordenes')
def ordenes():
    datos = ejecutar_query('''
        SELECT o.id, r.referencia, o.cantidad, o.fecha_creacion
        FROM ordenes_corte o
        JOIN referencias r ON o.referencia_id = r.id
        ORDER BY o.fecha_creacion DESC
    ''', fetch=True)
    return render_template('ordenes.html', ordenes=datos)

if __name__ == '__main__':
    app.run(debug=True)