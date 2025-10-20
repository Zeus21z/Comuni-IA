"""
Script para arreglar el bug de registro
"""
import sys
sys.path.insert(0, 'D:\\Comunianew')

from app import app, db, User, Business

# Arreglar usuarios sin business_id vinculado
with app.app_context():
    # Buscar usuarios sin negocio
    users_without_business = User.query.filter_by(business_id=None).all()
    
    if users_without_business:
        print(f"⚠️  Encontrados {len(users_without_business)} usuarios sin negocio vinculado")
        for user in users_without_business:
            print(f"  - {user.email}")
        
        # Buscar negocios huérfanos
        businesses = Business.query.all()
        users = User.query.all()
        
        business_ids_with_owner = [u.business_id for u in users if u.business_id]
        orphan_businesses = [b for b in businesses if b.id not in business_ids_with_owner]
        
        if orphan_businesses:
            print(f"\n⚠️  Encontrados {len(orphan_businesses)} negocios huérfanos")
            for b in orphan_businesses:
                print(f"  - {b.name} (ID: {b.id})")
    else:
        print("✅ Todos los usuarios tienen negocio vinculado")

print("\n✅ Revisión completada")
