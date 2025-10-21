"""
Script para poblar la base de datos con 2 negocios por categoría
Incluye productos específicos para cada tipo de negocio
"""
import sys
sys.path.insert(0, 'D:\\Comunianew')

from app import app, db, User, Business, Product
from werkzeug.security import generate_password_hash

# Datos de negocios organizados por categoría
negocios_data = [
    # GASTRONOMÍA
    {
        "user": {"email": "pizzaitalia@email.com", "password": "pizza123"},
        "business": {
            "name": "Pizza Italia",
            "description": "Auténticas pizzas italianas hechas en horno de leña. Masa artesanal y ingredientes importados directamente de Italia.",
            "category": "Gastronomía",
            "phone": "77012345",
            "whatsapp": "59177012345",
            "email": "pizzaitalia@email.com"
        },
        "products": [
            {"name": "Pizza Margarita", "price": 45.00},
            {"name": "Pizza Pepperoni", "price": 52.00},
            {"name": "Pizza Hawaiana", "price": 48.00},
            {"name": "Pizza Cuatro Quesos", "price": 55.00},
            {"name": "Lasaña Bolognesa", "price": 38.00}
        ]
    },
    {
        "user": {"email": "cafearoma@email.com", "password": "cafe123"},
        "business": {
            "name": "Café Aroma",
            "description": "Cafetería especializada en café de altura boliviano. Repostería artesanal y ambiente acogedor para trabajar o reunirse.",
            "category": "Gastronomía",
            "phone": "77012346",
            "whatsapp": "59177012346",
            "email": "cafearoma@email.com"
        },
        "products": [
            {"name": "Café Americano", "price": 12.00},
            {"name": "Cappuccino", "price": 15.00},
            {"name": "Café Latte", "price": 16.00},
            {"name": "Torta de Chocolate", "price": 20.00},
            {"name": "Sándwich Club", "price": 25.00}
        ]
    },
    
    # MODA Y ROPA
    {
        "user": {"email": "modaurbana@email.com", "password": "moda123"},
        "business": {
            "name": "Moda Urbana",
            "description": "Ropa de moda para jóvenes y adultos. Últimas tendencias en street wear y casual elegante. Envíos a toda Bolivia.",
            "category": "Moda y Ropa",
            "phone": "77012347",
            "whatsapp": "59177012347",
            "email": "modaurbana@email.com"
        },
        "products": [
            {"name": "Jean Skinny Hombre", "price": 180.00},
            {"name": "Polera Oversize", "price": 85.00},
            {"name": "Vestido Casual", "price": 150.00},
            {"name": "Chaqueta Denim", "price": 220.00},
            {"name": "Zapatillas Deportivas", "price": 250.00}
        ]
    },
    {
        "user": {"email": "boutiquechic@email.com", "password": "chic123"},
        "business": {
            "name": "Boutique Chic",
            "description": "Ropa femenina elegante y exclusiva. Vestidos para eventos, casual chic y accesorios de diseñador. Atención personalizada.",
            "category": "Moda y Ropa",
            "phone": "77012348",
            "whatsapp": "59177012348",
            "email": "boutiquechic@email.com"
        },
        "products": [
            {"name": "Vestido de Fiesta", "price": 350.00},
            {"name": "Blusa de Seda", "price": 180.00},
            {"name": "Pantalón Elegante", "price": 200.00},
            {"name": "Bolso de Cuero", "price": 280.00},
            {"name": "Zapatos de Tacón", "price": 320.00}
        ]
    },
    
    # SERVICIOS PROFESIONALES
    {
        "user": {"email": "contadores@email.com", "password": "conta123"},
        "business": {
            "name": "Contadores Asociados",
            "description": "Servicios contables y tributarios para empresas y particulares. Declaración de impuestos, auditorías y asesoría financiera.",
            "category": "Servicios Profesionales",
            "phone": "77012349",
            "whatsapp": "59177012349",
            "email": "contadores@email.com"
        },
        "products": [
            {"name": "Declaración de Impuestos", "price": 200.00},
            {"name": "Asesoría Contable Mensual", "price": 500.00},
            {"name": "Auditoría Financiera", "price": 1500.00},
            {"name": "Constitución de Empresa", "price": 800.00}
        ]
    },
    {
        "user": {"email": "abogadossc@email.com", "password": "legal123"},
        "business": {
            "name": "Abogados Santa Cruz",
            "description": "Estudio jurídico especializado en derecho civil, penal y laboral. 15 años de experiencia defendiendo sus derechos.",
            "category": "Servicios Profesionales",
            "phone": "77012350",
            "whatsapp": "59177012350",
            "email": "abogadossc@email.com"
        },
        "products": [
            {"name": "Consulta Legal", "price": 150.00},
            {"name": "Divorcio Express", "price": 1200.00},
            {"name": "Defensa Penal", "price": 2500.00},
            {"name": "Contrato Laboral", "price": 300.00}
        ]
    },
    
    # BELLEZA Y CUIDADO PERSONAL
    {
        "user": {"email": "salonbella@email.com", "password": "bella123"},
        "business": {
            "name": "Salón Bella",
            "description": "Salón de belleza integral. Cortes, tintes, manicure, pedicure y tratamientos faciales. Productos profesionales de primera calidad.",
            "category": "Belleza y Cuidado Personal",
            "phone": "77012351",
            "whatsapp": "59177012351",
            "email": "salonbella@email.com"
        },
        "products": [
            {"name": "Corte de Cabello Dama", "price": 50.00},
            {"name": "Tinte Completo", "price": 150.00},
            {"name": "Manicure + Pedicure", "price": 80.00},
            {"name": "Tratamiento Facial", "price": 120.00},
            {"name": "Alisado Brasileño", "price": 400.00}
        ]
    },
    {
        "user": {"email": "barberking@email.com", "password": "barber123"},
        "business": {
            "name": "Barbería King",
            "description": "Barbería moderna para caballeros. Cortes clásicos y modernos, barba, cejas. Ambiente masculino y cerveza gratis.",
            "category": "Belleza y Cuidado Personal",
            "phone": "77012352",
            "whatsapp": "59177012352",
            "email": "barberking@email.com"
        },
        "products": [
            {"name": "Corte Clásico", "price": 40.00},
            {"name": "Corte + Barba", "price": 60.00},
            {"name": "Arreglo de Cejas", "price": 20.00},
            {"name": "Tinte de Barba", "price": 50.00},
            {"name": "Corte Diseño", "price": 70.00}
        ]
    },
    
    # HOGAR Y DECORACIÓN
    {
        "user": {"email": "decorahome@email.com", "password": "decor123"},
        "business": {
            "name": "Decora Home",
            "description": "Muebles y decoración para tu hogar. Desde sofás hasta cuadros decorativos. Asesoría gratuita en diseño de interiores.",
            "category": "Hogar y Decoración",
            "phone": "77012353",
            "whatsapp": "59177012353",
            "email": "decorahome@email.com"
        },
        "products": [
            {"name": "Sofá 3 Cuerpos", "price": 2500.00},
            {"name": "Mesa de Centro", "price": 800.00},
            {"name": "Lámpara Moderna", "price": 350.00},
            {"name": "Cuadro Decorativo", "price": 180.00},
            {"name": "Alfombra Grande", "price": 650.00}
        ]
    },
    {
        "user": {"email": "plantasverdes@email.com", "password": "plantas123"},
        "business": {
            "name": "Plantas Verdes",
            "description": "Vivero y plantas de interior. Cactus, suculentas, plantas ornamentales y macetas artesanales. Asesoría en cuidado de plantas.",
            "category": "Hogar y Decoración",
            "phone": "77012354",
            "whatsapp": "59177012354",
            "email": "plantasverdes@email.com"
        },
        "products": [
            {"name": "Cactus Pequeño", "price": 25.00},
            {"name": "Suculenta en Maceta", "price": 35.00},
            {"name": "Planta Monstera", "price": 120.00},
            {"name": "Maceta Cerámica", "price": 45.00},
            {"name": "Kit de Jardinería", "price": 80.00}
        ]
    },
    
    # TECNOLOGÍA
    {
        "user": {"email": "techstore@email.com", "password": "tech123"},
        "business": {
            "name": "Tech Store",
            "description": "Tienda de tecnología y electrónica. Computadoras, celulares, accesorios y servicio técnico especializado. Garantía en todos nuestros productos.",
            "category": "Tecnología",
            "phone": "77012355",
            "whatsapp": "59177012355",
            "email": "techstore@email.com"
        },
        "products": [
            {"name": "Laptop HP Core i5", "price": 4500.00},
            {"name": "Mouse Gamer RGB", "price": 180.00},
            {"name": "Teclado Mecánico", "price": 350.00},
            {"name": "Auriculares Bluetooth", "price": 220.00},
            {"name": "Webcam Full HD", "price": 280.00}
        ]
    },
    {
        "user": {"email": "reparatech@email.com", "password": "repara123"},
        "business": {
            "name": "Repara Tech",
            "description": "Servicio técnico de computadoras y celulares. Reparación, mantenimiento y actualización. Diagnóstico gratuito.",
            "category": "Tecnología",
            "phone": "77012356",
            "whatsapp": "59177012356",
            "email": "reparatech@email.com"
        },
        "products": [
            {"name": "Reparación Pantalla Celular", "price": 280.00},
            {"name": "Formateo PC", "price": 80.00},
            {"name": "Mantenimiento Laptop", "price": 150.00},
            {"name": "Instalación Windows", "price": 100.00},
            {"name": "Cambio Batería Celular", "price": 120.00}
        ]
    },
    
    # SALUD Y BIENESTAR
    {
        "user": {"email": "gympower@email.com", "password": "gym123"},
        "business": {
            "name": "Gym Power",
            "description": "Gimnasio completo con equipamiento de última generación. Clases grupales, entrenadores personales y nutricionista. Abierto 24/7.",
            "category": "Salud y Bienestar",
            "phone": "77012357",
            "whatsapp": "59177012357",
            "email": "gympower@email.com"
        },
        "products": [
            {"name": "Membresía Mensual", "price": 200.00},
            {"name": "Membresía Trimestral", "price": 540.00},
            {"name": "Membresía Anual", "price": 1800.00},
            {"name": "Entrenamiento Personal (sesión)", "price": 80.00},
            {"name": "Plan Nutricional", "price": 150.00}
        ]
    },
    {
        "user": {"email": "yogazen@email.com", "password": "yoga123"},
        "business": {
            "name": "Yoga Zen",
            "description": "Centro de yoga y meditación. Clases para todos los niveles, terapias holísticas y masajes relajantes. Encuentra tu paz interior.",
            "category": "Salud y Bienestar",
            "phone": "77012358",
            "whatsapp": "59177012358",
            "email": "yogazen@email.com"
        },
        "products": [
            {"name": "Clase de Yoga (Individual)", "price": 50.00},
            {"name": "Pack 10 Clases", "price": 400.00},
            {"name": "Masaje Relajante", "price": 120.00},
            {"name": "Terapia Reiki", "price": 150.00},
            {"name": "Mat de Yoga Premium", "price": 180.00}
        ]
    },
    
    # EDUCACIÓN
    {
        "user": {"email": "inglesfast@email.com", "password": "ingles123"},
        "business": {
            "name": "Inglés Fast",
            "description": "Academia de inglés con método intensivo. Aprende en 6 meses con profesores nativos. Preparación para exámenes internacionales.",
            "category": "Educación",
            "phone": "77012359",
            "whatsapp": "59177012359",
            "email": "inglesfast@email.com"
        },
        "products": [
            {"name": "Curso Básico (3 meses)", "price": 600.00},
            {"name": "Curso Intermedio (3 meses)", "price": 650.00},
            {"name": "Curso Avanzado (3 meses)", "price": 700.00},
            {"name": "Clases Particulares (hora)", "price": 80.00},
            {"name": "Material Didáctico", "price": 120.00}
        ]
    },
    {
        "user": {"email": "clasesmate@email.com", "password": "mate123"},
        "business": {
            "name": "Clases Particulares Matemáticas",
            "description": "Profesor universitario ofrece clases particulares de matemáticas para colegio y universidad. Álgebra, cálculo, física.",
            "category": "Educación",
            "phone": "77012360",
            "whatsapp": "59177012360",
            "email": "clasesmate@email.com"
        },
        "products": [
            {"name": "Clase Individual (2 horas)", "price": 100.00},
            {"name": "Pack 10 Clases", "price": 850.00},
            {"name": "Preparación Examen", "price": 150.00},
            {"name": "Resolución de Tareas", "price": 50.00}
        ]
    },
    
    # OTROS
    {
        "user": {"email": "fotostudio@email.com", "password": "foto123"},
        "business": {
            "name": "Foto Studio",
            "description": "Estudio fotográfico profesional. Sesiones de fotos, eventos, bodas, quinceaños. Edición profesional incluida.",
            "category": "Otros",
            "phone": "77012361",
            "whatsapp": "59177012361",
            "email": "fotostudio@email.com"
        },
        "products": [
            {"name": "Sesión Fotográfica Personal", "price": 350.00},
            {"name": "Cobertura de Boda", "price": 2500.00},
            {"name": "Sesión Quinceañera", "price": 800.00},
            {"name": "Fotos de Producto", "price": 200.00},
            {"name": "Video Promocional", "price": 1200.00}
        ]
    },
    {
        "user": {"email": "eventosmagicos@email.com", "password": "eventos123"},
        "business": {
            "name": "Eventos Mágicos",
            "description": "Organización de eventos sociales y corporativos. Cumpleaños, bodas, eventos empresariales. Todo incluido.",
            "category": "Otros",
            "phone": "77012362",
            "whatsapp": "59177012362",
            "email": "eventosmagicos@email.com"
        },
        "products": [
            {"name": "Cumpleaños Infantil", "price": 1500.00},
            {"name": "Evento Corporativo", "price": 3500.00},
            {"name": "Boda Completa", "price": 8000.00},
            {"name": "Baby Shower", "price": 1200.00},
            {"name": "Quinceañera", "price": 4500.00}
        ]
    }
]

def poblar_base_datos():
    with app.app_context():
        print("🚀 Iniciando población de base de datos...\n")
        
        credenciales = []
        
        for idx, data in enumerate(negocios_data, 1):
            try:
                print(f"[{idx}/18] Creando: {data['business']['name']}...")
                
                # Crear usuario
                user = User(
                    email=data['user']['email'],
                    role='user'
                )
                user.set_password(data['user']['password'])
                db.session.add(user)
                db.session.flush()
                
                # Crear negocio
                business = Business(
                    name=data['business']['name'],
                    description=data['business']['description'],
                    category=data['business']['category'],
                    phone=data['business'].get('phone'),
                    email=data['business'].get('email'),
                    whatsapp=data['business'].get('whatsapp'),
                    location="Santa Cruz, Bolivia"
                )
                db.session.add(business)
                db.session.flush()
                
                # Vincular usuario con negocio
                user.business_id = business.id
                
                # Crear productos
                for prod_data in data['products']:
                    product = Product(
                        business_id=business.id,
                        name=prod_data['name'],
                        price=prod_data['price']
                    )
                    db.session.add(product)
                
                db.session.commit()
                
                # Guardar credenciales
                credenciales.append({
                    'negocio': data['business']['name'],
                    'categoria': data['business']['category'],
                    'email': data['user']['email'],
                    'password': data['user']['password'],
                    'productos': len(data['products'])
                })
                
                print(f"   ✅ {data['business']['name']} - {len(data['products'])} productos")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                db.session.rollback()
                continue
        
        print(f"\n✅ ¡Población completada!")
        print(f"📊 Total negocios creados: {len(credenciales)}")
        print(f"📦 Total productos: {sum(c['productos'] for c in credenciales)}")
        
        return credenciales

if __name__ == '__main__':
    credenciales = poblar_base_datos()
    
    # Guardar credenciales en archivo TXT
    with open('D:\\Comunianew\\CREDENCIALES_NEGOCIOS.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("CREDENCIALES DE ACCESO - COMUNI IA\n")
        f.write("=" * 80 + "\n\n")
        f.write("Total de Negocios: 18 (2 por categoría)\n")
        f.write("Fecha de Creación: " + str(__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')) + "\n")
        f.write("\n" + "=" * 80 + "\n\n")
        
        categoria_actual = ""
        for cred in credenciales:
            if cred['categoria'] != categoria_actual:
                categoria_actual = cred['categoria']
                f.write(f"\n{'─' * 80}\n")
                f.write(f"CATEGORÍA: {categoria_actual.upper()}\n")
                f.write(f"{'─' * 80}\n\n")
            
            f.write(f"Negocio: {cred['negocio']}\n")
            f.write(f"Email: {cred['email']}\n")
            f.write(f"Contraseña: {cred['password']}\n")
            f.write(f"Productos: {cred['productos']}\n")
            f.write(f"URL: http://localhost:5000/login\n")
            f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("NOTAS:\n")
        f.write("- Todas las contraseñas son simples para propósitos de testing\n")
        f.write("- Los productos NO tienen imágenes (puedes agregarlas después)\n")
        f.write("- Cada negocio tiene entre 4-5 productos específicos\n")
        f.write("- Para cambiar contraseñas, hazlo desde el panel de admin\n")
        f.write("=" * 80 + "\n")
    
    print(f"\n📄 Archivo de credenciales creado: CREDENCIALES_NEGOCIOS.txt")
    print("\n🎉 ¡Proceso completado exitosamente!")
