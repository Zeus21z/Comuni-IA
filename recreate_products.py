from app import app, db
from sqlalchemy import text

def recreate_products_table():
    with app.app_context():
        try:
            # Get all existing products data
            result = db.session.execute(text('''
                SELECT id, business_id, name, price, image_url 
                FROM products
            ''')).fetchall()
            
            # Store the data
            products_data = [{
                'id': row[0],
                'business_id': row[1],
                'name': row[2],
                'price': row[3],
                'image_url': row[4]
            } for row in result]
            
            # Drop the existing table
            db.session.execute(text('DROP TABLE IF EXISTS products'))
            
            # Create tables (this will create the products table with the new schema)
            db.create_all()
            
            # Reinsert the data with NULL description
            for product in products_data:
                db.session.execute(text('''
                    INSERT INTO products (id, business_id, name, price, image_url, description)
                    VALUES (:id, :business_id, :name, :price, :image_url, NULL)
                '''), product)
            
            db.session.commit()
            print("Successfully recreated products table with description column")
            
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    recreate_products_table()