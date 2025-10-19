"""
Script de migración completa - Fases C, D, E
Ejecutar con: python migrate_complete.py
"""
import sqlite3
import os

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
        
        conn.commit()
        print("\n🎉 Migración completada exitosamente!")
        print("\n📋 Resumen:")
        print("   - Tabla users: Lista para autenticación")
        print("   - Reviews: Ahora con timestamps")
        print("   - Todas las fases (A, B, C, D, E) están activas")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
