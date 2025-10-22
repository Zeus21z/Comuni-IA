from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text('ALTER TABLE products ADD COLUMN description TEXT'))
        db.session.commit()
        print("Successfully added description column")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()