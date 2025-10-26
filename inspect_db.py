import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, inspect

# Obtener la ruta absoluta a la base de datos desde app.py
BASEDIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASEDIR, 'comuni_ia.db')
DB_URI = f"sqlite:///{DB_PATH}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def inspect_database_schema():
    """Se conecta a la base de datos y muestra información sobre las tablas y sus claves foráneas."""
    print(f"Inspeccionando la base de datos en: {DB_URI}")
    
    engine = create_engine(DB_URI)
    inspector = inspect(engine)
    
    schemas = inspector.get_schema_names()
    for schema in schemas:
        print(f"\n--- Esquema: {schema} ---")
        tables = inspector.get_table_names(schema=schema)
        if not tables:
            print("No se encontraron tablas en este esquema.")
            continue
            
        for table_name in tables:
            print(f"\nTabla: {table_name}")
            
            # Columnas
            print("  Columnas:")
            try:
                columns = inspector.get_columns(table_name, schema=schema)
                for column in columns:
                    print(f"    - {column['name']} ({column['type']})")
            except Exception as e:
                print(f"    Error al obtener columnas: {e}")

            # Claves Foráneas
            print("  Claves Foráneas:")
            try:
                fks = inspector.get_foreign_keys(table_name, schema=schema)
                if not fks:
                    print("    (Ninguna)")
                else:
                    for fk in fks:
                        print(f"    - Columnas locales: {fk['constrained_columns']}")
                        print(f"      -> Hacen referencia a la tabla: {fk['referred_table']}")
                        print(f"      -> Columnas referenciadas: {fk['referred_columns']}")
            except Exception as e:
                print(f"    Error al obtener claves foráneas: {e}")

if __name__ == '__main__':
    with app.app_context():
        inspect_database_schema()
