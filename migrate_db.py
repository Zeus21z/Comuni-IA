"""
Script para agregar campos nuevos a la base de datos existente
Ejecutar con: python migrate_db.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'comuni_ia.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(businesses)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Agregar columna 'category' si no existe
        if 'category' not in columns:
            cursor.execute("ALTER TABLE businesses ADD COLUMN category VARCHAR(100) DEFAULT 'Otros'")
            print("✅ Columna 'category' agregada")
        else:
            print("ℹ️  Columna 'category' ya existe")
        
        # Agregar columna 'phone' si no existe
        if 'phone' not in columns:
            cursor.execute("ALTER TABLE businesses ADD COLUMN phone VARCHAR(20)")
            print("✅ Columna 'phone' agregada")
        else:
            print("ℹ️  Columna 'phone' ya existe")
        
        # Agregar columna 'email' si no existe
        if 'email' not in columns:
            cursor.execute("ALTER TABLE businesses ADD COLUMN email VARCHAR(120)")
            print("✅ Columna 'email' agregada")
        else:
            print("ℹ️  Columna 'email' ya existe")
        
        # Agregar columna 'whatsapp' si no existe
        if 'whatsapp' not in columns:
            cursor.execute("ALTER TABLE businesses ADD COLUMN whatsapp VARCHAR(20)")
            print("✅ Columna 'whatsapp' agregada")
        else:
            print("ℹ️  Columna 'whatsapp' ya existe")
        
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
