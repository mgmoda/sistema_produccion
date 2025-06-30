import sqlite3

# Conectar o crear la base de datos
conn = sqlite3.connect('produccion.db')
cursor = conn.cursor()

# Crear tabla de referencias
cursor.execute('''
CREATE TABLE IF NOT EXISTS referencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referencia TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    requiere_estampado BOOLEAN DEFAULT 0
)
''')

# Crear tabla de órdenes de corte
cursor.execute('''
CREATE TABLE IF NOT EXISTS ordenes_corte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referencia_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_creacion DATE DEFAULT CURRENT_DATE,
    observaciones TEXT,
    FOREIGN KEY (referencia_id) REFERENCES referencias(id)
)
''')

# Crear tabla de procesos asociados a la orden
cursor.execute('''
CREATE TABLE IF NOT EXISTS procesos_orden (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_id INTEGER NOT NULL,
    tipo_proceso TEXT NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    estado TEXT DEFAULT 'Pendiente',
    observaciones TEXT,
    FOREIGN KEY (orden_id) REFERENCES ordenes_corte(id)
)
''')

conn.commit()
conn.close()

print("✅ Tablas creadas correctamente.")