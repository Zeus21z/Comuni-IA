"""
Script para corregir y sincronizar el esquema de la base de datos.

Este script realiza dos tareas importantes:
1.  Elimina la columna conflictiva 'owner_id' de la tabla 'businesses' si existe,
    reconstruyendo la tabla de forma segura para SQLite.
2.  Añade las columnas 'is_active' a las tablas 'businesses' y 'users' si no existen,
    para alinear la base de datos con los modelos de la aplicación.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'comuni_ia.db')

def fix_and_sync_schema():
    print("🔄 Iniciando la corrección del esquema de la tabla 'businesses'...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # --- TAREA 1: Eliminar la columna 'owner_id' si existe ---
        cursor.execute("PRAGMA table_info(businesses)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'owner_id' in columns:
            print("  - Detectada columna 'owner_id' conflictiva. Procediendo a la corrección.")
            
            # Renombrar la tabla vieja
            cursor.execute("ALTER TABLE businesses RENAME TO businesses_old")
            print("  - Tabla 'businesses' renombrada a 'businesses_old'.")

            # Crear la nueva tabla con el esquema correcto (sin owner_id)
            correct_columns = [col for col in columns if col != 'owner_id']
            correct_columns_str = ", ".join(f'"{c}"' for c in correct_columns) # Usar comillas para nombres de columna
            
            cursor.execute(f"CREATE TABLE businesses AS SELECT {correct_columns_str} FROM businesses_old")
            print("  - Nueva tabla 'businesses' creada con las columnas correctas.")

            # Eliminar la tabla antigua
            cursor.execute("DROP TABLE businesses_old")
            print("  - Tabla temporal 'businesses_old' eliminada.")
        else:
            print("✅ La columna 'owner_id' no existe en 'businesses'. No se requiere limpieza.")

        # --- TAREA 2: Añadir columnas 'is_active' si no existen ---
        print("\n🔄 Sincronizando columnas 'is_active'...")

        # Para la tabla 'businesses'
        cursor.execute("PRAGMA table_info(businesses)")
        business_cols = [row[1] for row in cursor.fetchall()]
        if 'is_active' not in business_cols:
            cursor.execute("ALTER TABLE businesses ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1")
            print("  ✅ Columna 'is_active' agregada a 'businesses'.")
        else:
            print("  ℹ️  La columna 'is_active' ya existe en 'businesses'.")

        # Para la tabla 'users'
        cursor.execute("PRAGMA table_info(users)")
        user_cols = [row[1] for row in cursor.fetchall()]
        if 'is_active' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1")
            print("  ✅ Columna 'is_active' agregada a 'users'.")
        else:
            print("  ℹ️  La columna 'is_active' ya existe en 'users'.")

        conn.commit()
        print("\n🎉 ¡Esquema corregido y sincronizado exitosamente!")

    except Exception as e:
        print(f"\n❌ Error durante la corrección: {e}")
        print("  - Revirtiendo cambios...")
        conn.rollback()
    finally:
        print("  - Cerrando conexión con la base de datos.")
        conn.close()

if __name__ == '__main__':
    fix_and_sync_schema()