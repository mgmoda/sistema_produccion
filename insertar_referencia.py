import sqlite3

conexion = sqlite3.connect('produccion.db')
cursor = conexion.cursor()

# Insertar una referencia de prueba
cursor.execute("""
    INSERT INTO referencias (referencia, descripcion, requiere_estampado)
    VALUES (?, ?, ?)
""", ("REF123", "Vestido boho estampado", 1))  # 1 = requiere estampado

conexion.commit()
conexion.close()

print("✅ Referencia insertada correctamente.")