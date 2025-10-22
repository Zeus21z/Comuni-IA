import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'comuni_ia.db')

def reset_history():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: No se encontró el archivo de base de datos en {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS alembic_version")
        conn.commit()
        conn.close()
        print("✅ Historial de migraciones reseteado en la base de datos (tabla 'alembic_version' eliminada).")
    except Exception as e:
        print(f"❌ Ocurrió un error al intentar resetear el historial: {e}")

if __name__ == '__main__':
    reset_history()