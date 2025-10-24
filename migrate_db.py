"""
Script para agregar campos nuevos a la base de datos existente
Ejecutar con: python migrate_db.py
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash # ¡IMPORTANTE! Añadir esta línea

DB_PATH = os.path.join(os.path.dirname(__file__), 'comuni_ia.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("--- Migrando tabla 'businesses' ---")
        cursor.execute("PRAGMA table_info(businesses)")
        business_columns = [col[1] for col in cursor.fetchall()]

        # Columnas a agregar en 'businesses'
        cols_to_add_businesses = {
            'category': "VARCHAR(100) DEFAULT 'Otros'",
            'phone': "VARCHAR(20)",
            'email': "VARCHAR(120)",
            'whatsapp': "VARCHAR(20)",
            'nit': "VARCHAR(20)",
            'latitude': "REAL",
            'longitude': "REAL"
        }

        for col, col_type in cols_to_add_businesses.items():
            if col not in business_columns:
                cursor.execute(f"ALTER TABLE businesses ADD COLUMN {col} {col_type}")
                print(f"✅ Columna '{col}' agregada a 'businesses'")
            else:
                print(f"ℹ️  Columna '{col}' ya existe en 'businesses'")

        # --- Migrar tabla 'products' ---
        print("\n--- Migrando tabla 'products' ---")
        try:
            cursor.execute("PRAGMA table_info(products)")
            product_columns = [col[1] for col in cursor.fetchall()]

            if 'description' not in product_columns:
                cursor.execute("ALTER TABLE products ADD COLUMN description TEXT")
                print("✅ Columna 'description' agregada a 'products'")
            else:
                print("ℹ️  Columna 'description' ya existe en 'products'")
        except sqlite3.OperationalError as e:
            if "no such table: products" in str(e):
                print("⚠️  Tabla 'products' no encontrada. Se creará al iniciar la app.")
            else:
                raise e

        # --- Crear usuario admin si no existe ---
        print("\n--- Verificando usuario administrador ---")
        ADMIN_EMAIL = 'godIA@comunia.com'
        ADMIN_PASSWORD = 'god123'
        ADMIN_ROLE = 'admin'

        cursor.execute("SELECT * FROM users WHERE email = ?", (ADMIN_EMAIL,))
        if not cursor.fetchone():
            admin_pass_hash = generate_password_hash(ADMIN_PASSWORD)
            cursor.execute("""
                INSERT INTO users (email, password_hash, role)
                VALUES (?, ?, ?)
            """, (ADMIN_EMAIL, admin_pass_hash, ADMIN_ROLE))
            print(f"✅ Usuario admin creado (email: {ADMIN_EMAIL}, pass: {ADMIN_PASSWORD} - ¡Cámbiala!)")
        else:
            print(f"ℹ️  El usuario administrador '{ADMIN_EMAIL}' ya existe.")

        conn.commit()
        print("\n🎉 Migración completada exitosamente!")

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("🔄 Iniciando migración de base de datos...\n")
    migrate()
