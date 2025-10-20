"""
Script de migración completa - Fases C, D, E + Mejoras Admin
Ejecutar con: python migrate_complete.py
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash  # Import para hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'comuni_ia.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("🔄 Iniciando migración completa...\n")
        
        # 1. Verificar y agregar columna created_at a reviews
        cursor.execute("PRAGMA table_info(reviews)")
        review_columns = [col[1] for col in cursor.fetchall()]
        
        if 'created_at' not in review_columns:
            cursor.execute("ALTER TABLE reviews ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            print("✅ Columna 'created_at' agregada a reviews")
        else:
            print("ℹ️  Columna 'created_at' ya existe en reviews")
        
        # 2. Crear tabla users si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                business_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses (id)
            )
        """)
        print("✅ Tabla 'users' creada/verificada")
        
        # 3. NUEVO: Agregar columna role a users si no existe
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in cursor.fetchall()]
        
        if 'role' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
            print("✅ Columna 'role' agregada a users")
        else:
            print("ℹ️  Columna 'role' ya existe en users")
        
        # 4. NUEVO: Crear usuario admin inicial si no existe
        cursor.execute("SELECT * FROM users WHERE email = 'admin@comunia.com'")
        if not cursor.fetchone():
            admin_pass_hash = generate_password_hash('admin123')  # Cambia esta contraseña después
            cursor.execute("""
                INSERT INTO users (email, password_hash, role)
                VALUES ('admin@comunia.com', ?, 'admin')
            """, (admin_pass_hash,))
            print("✅ Usuario admin creado (email: admin@comunia.com, pass: admin123 - ¡Cámbiala!)")
        else:
            print("ℹ️  Usuario admin ya existe")
        
        conn.commit()
        print("\n🎉 Migración completada exitosamente!")
        print("\n📋 Resumen:")
        print("   - Tabla users: Lista para autenticación con roles")
        print("   - Reviews: Ahora con timestamps")
        print("   - Admin inicial: Creado si no existía")
        print("   - Todas las fases (A, B, C, D, E + Admin) están activas")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()