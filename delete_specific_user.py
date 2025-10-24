"""
Script para eliminar un usuario específico de la base de datos por su email.
Útil para limpiar usuarios de prueba o incorrectos.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'comuni_ia.db')

def delete_user_by_email(email_to_delete):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE email = ?", (email_to_delete,))
        if cursor.rowcount > 0:
            print(f"✅ Usuario '{email_to_delete}' eliminado exitosamente de la base de datos.")
            conn.commit()
        else:
            print(f"ℹ️  No se encontró ningún usuario con el email '{email_to_delete}'.")
    except Exception as e:
        print(f"❌ Error al intentar eliminar el usuario '{email_to_delete}': {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("🔄 Iniciando eliminación de usuario...\n")
    # Define el email del usuario que quieres eliminar
    delete_user_by_email('admin@comunia.com')
