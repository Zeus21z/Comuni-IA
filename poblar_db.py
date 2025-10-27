"""
Script para poblar la base de datos con 2 negocios por categoría
Incluye productos específicos para cada tipo de negocio
"""
import os
import sys
import random

# --- MEJORA: Añadir la ruta del proyecto al path de Python ---
# Esto asegura que el script siempre pueda encontrar el módulo 'app'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
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
            {"name": "Pizza Margarita", "price": 45.00, "description": "La clásica pizza Margarita con salsa de tomate fresca, mozzarella y albahaca. ¡Simple y deliciosa!"},
            {"name": "Pizza Pepperoni", "price": 52.00, "description": "Una favorita de todos, cargada con pepperoni de alta calidad y queso mozzarella derretido."},
            {"name": "Pizza Hawaiana", "price": 48.00, "description": "La controversial pero amada combinación de jamón jugoso y piña dulce sobre una base de mozzarella."},
            {"name": "Pizza Cuatro Quesos", "price": 55.00, "description": "Para los amantes del queso: una mezcla irresistible de mozzarella, provolone, parmesano y gorgonzola."},
            {"name": "Lasaña Bolognesa", "price": 38.00, "description": "Capas de pasta fresca, rica salsa boloñesa y bechamel, horneada a la perfección con queso parmesano."}
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
            {"name": "Café Americano", "price": 12.00, "description": "Un shot de nuestro mejor espresso de altura, diluido con agua caliente para un sabor suave y robusto."},
            {"name": "Cappuccino", "price": 15.00, "description": "El equilibrio perfecto entre espresso, leche vaporizada y una cremosa capa de espuma. Ideal para empezar el día."},
            {"name": "Café Latte", "price": 16.00, "description": "Espresso suave mezclado con una generosa cantidad de leche vaporizada, coronado con un toque de espuma."},
            {"name": "Torta de Chocolate", "price": 20.00, "description": "Una rebanada húmeda y decadente de nuestra famosa torta de chocolate, el acompañante perfecto para tu café."},
            {"name": "Sándwich Club", "price": 25.00, "description": "Un clásico sándwich de tres pisos con pavo, tocino, lechuga, tomate y mayonesa. ¡Satisfacción garantizada!"}
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
            {"name": "Jean Skinny Hombre", "price": 180.00, "description": "Jeans ajustados y modernos para hombre, fabricados con denim elástico para máximo confort y estilo."},
            {"name": "Polera Oversize", "price": 85.00, "description": "Luce un estilo relajado y a la moda con nuestra polera oversize de algodón suave."},
            {"name": "Vestido Casual", "price": 150.00, "description": "Un vestido versátil y cómodo, perfecto para cualquier ocasión, desde un paseo por la ciudad hasta una salida con amigos."},
            {"name": "Chaqueta Denim", "price": 220.00, "description": "La chaqueta de jean que no puede faltar en tu armario. Un clásico atemporal que combina con todo."},
            {"name": "Zapatillas Deportivas", "price": 250.00, "description": "Zapatillas cómodas y con estilo, ideales tanto para hacer deporte como para tu look diario."}
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
            {"name": "Vestido de Fiesta", "price": 350.00, "description": "Deslumbra en tu próximo evento con este elegante vestido de fiesta, diseñado para realzar tu figura."},
            {"name": "Blusa de Seda", "price": 180.00, "description": "Una blusa de seda suave y lujosa, perfecta para un look de oficina sofisticado o una cena elegante."},
            {"name": "Pantalón Elegante", "price": 200.00, "description": "Pantalón de corte sastre que combina comodidad y elegancia, ideal para eventos formales o de trabajo."},
            {"name": "Bolso de Cuero", "price": 280.00, "description": "Un bolso de cuero genuino, espacioso y con un diseño atemporal. El accesorio perfecto para cualquier atuendo."},
            {"name": "Zapatos de Tacón", "price": 320.00, "description": "Eleva tu estilo con estos clásicos zapatos de tacón, diseñados para ofrecer elegancia y comodidad."}
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
            {"name": "Declaración de Impuestos", "price": 200.00, "description": "Servicio completo de declaración de impuestos para personas y empresas. Evita multas y optimiza tu carga tributaria."},
            {"name": "Asesoría Contable Mensual", "price": 500.00, "description": "Mantén tus finanzas en orden con nuestro servicio de asesoría mensual. Incluye registro de transacciones y reportes financieros."},
            {"name": "Auditoría Financiera", "price": 1500.00, "description": "Análisis exhaustivo de tus estados financieros para garantizar la precisión y el cumplimiento normativo."},
            {"name": "Constitución de Empresa", "price": 800.00, "description": "Te guiamos en todo el proceso para constituir legalmente tu nueva empresa de forma rápida y segura."}
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
            {"name": "Consulta Legal", "price": 150.00, "description": "Asesoría legal inicial para evaluar tu caso y orientarte sobre los pasos a seguir en cualquier área del derecho."},
            {"name": "Divorcio Express", "price": 1200.00, "description": "Proceso de divorcio de mutuo acuerdo, gestionado de forma rápida y eficiente por nuestros especialistas."},
            {"name": "Defensa Penal", "price": 2500.00, "description": "Representación legal experta en casos penales, defendiendo tus derechos en todas las etapas del proceso."},
            {"name": "Contrato Laboral", "price": 300.00, "description": "Redacción y revisión de contratos laborales para empleadores y empleados, asegurando el cumplimiento de la normativa vigente."}
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
            {"name": "Corte de Cabello Dama", "price": 50.00, "description": "Renueva tu look con un corte moderno y estilizado por nuestros expertos. Incluye lavado y secado."},
            {"name": "Tinte Completo", "price": 150.00, "description": "Coloración completa con productos de alta gama que cuidan tu cabello y garantizan un color vibrante y duradero."},
            {"name": "Manicure + Pedicure", "price": 80.00, "description": "El cuidado completo para tus manos y pies. Incluye limado, cutículas, exfoliación y esmaltado."},
            {"name": "Tratamiento Facial", "price": 120.00, "description": "Limpieza profunda e hidratación para revitalizar tu piel, dejándola suave y radiante."},
            {"name": "Alisado Brasileño", "price": 400.00, "description": "Consigue un cabello liso, brillante y sin frizz por meses con nuestro tratamiento de keratina brasileña."}
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
            {"name": "Corte Clásico", "price": 40.00, "description": "El tradicional corte de caballero con máquina y tijera, finalizado con un perfilado preciso."},
            {"name": "Corte + Barba", "price": 60.00, "description": "Servicio completo de corte de cabello y arreglo de barba con toalla caliente y perfilado a navaja."},
            {"name": "Arreglo de Cejas", "price": 20.00, "description": "Define y limpia tus cejas para enmarcar tu mirada con un estilo natural y masculino."},
            {"name": "Tinte de Barba", "price": 50.00, "description": "Cubre las canas y dale a tu barba un color uniforme y natural con nuestros tintes especiales."},
            {"name": "Corte Diseño", "price": 70.00, "description": "Atrévete con un corte moderno. Realizamos diseños y tribales con la máxima precisión."}
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
            {"name": "Sofá 3 Cuerpos", "price": 2500.00, "description": "Un sofá espacioso y confortable, tapizado en tela de alta resistencia. Perfecto para tu sala de estar."},
            {"name": "Mesa de Centro", "price": 800.00, "description": "Mesa de centro de diseño minimalista, fabricada en madera maciza con acabados de primera."},
            {"name": "Lámpara Moderna", "price": 350.00, "description": "Ilumina tus espacios con estilo. Lámpara de pie con diseño contemporáneo y luz cálida."},
            {"name": "Cuadro Decorativo", "price": 180.00, "description": "Arte abstracto en lienzo para darle un toque de color y personalidad a tus paredes."},
            {"name": "Alfombra Grande", "price": 650.00, "description": "Alfombra de área (2x3m) de pelo suave, ideal para dar calidez y confort a cualquier habitación."}
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
            {"name": "Cactus Pequeño", "price": 25.00, "description": "Ideal para escritorios y espacios pequeños. Un cactus de fácil cuidado que añade un toque verde a tu vida."},
            {"name": "Suculenta en Maceta", "price": 35.00, "description": "Hermosa suculenta en maceta de terracota. Requiere poca agua y es perfecta para principiantes."},
            {"name": "Planta Monstera", "price": 120.00, "description": "La popular Monstera Deliciosa o 'Costilla de Adán'. Una planta de interior espectacular que purifica el aire."},
            {"name": "Maceta Cerámica", "price": 45.00, "description": "Maceta de cerámica esmaltada con diseño moderno y agujero de drenaje. Varios colores disponibles."},
            {"name": "Kit de Jardinería", "price": 80.00, "description": "Kit básico para el cuidado de tus plantas. Incluye pala, rastrillo y tijeras de podar pequeñas."}
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
            {"name": "Laptop HP Core i5", "price": 4500.00, "description": "Potente laptop con procesador Core i5, 8GB de RAM y 256GB SSD. Ideal para trabajo y estudio."},
            {"name": "Mouse Gamer RGB", "price": 180.00, "description": "Mouse ergonómico para gaming con iluminación RGB personalizable y alta precisión de DPI."},
            {"name": "Teclado Mecánico", "price": 350.00, "description": "Teclado mecánico con switches de alta durabilidad, retroiluminación y layout en español."},
            {"name": "Auriculares Bluetooth", "price": 220.00, "description": "Auriculares inalámbricos con cancelación de ruido y hasta 20 horas de autonomía. Sonido de alta fidelidad."},
            {"name": "Webcam Full HD", "price": 280.00, "description": "Cámara web 1080p con micrófono incorporado, perfecta para videollamadas y streaming."}
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
            {"name": "Reparación Pantalla Celular", "price": 280.00, "description": "Reemplazo de pantalla rota para las principales marcas de celulares. Consulta por tu modelo."},
            {"name": "Formateo PC", "price": 80.00, "description": "Servicio de formateo e instalación de sistema operativo Windows o Linux. Incluye respaldo de datos."},
            {"name": "Mantenimiento Laptop", "price": 150.00, "description": "Limpieza interna de componentes, cambio de pasta térmica y optimización de software para mejorar el rendimiento."},
            {"name": "Instalación Windows", "price": 100.00, "description": "Instalación limpia del sistema operativo Windows 10 u 11 con drivers y programas básicos."},
            {"name": "Cambio Batería Celular", "price": 120.00, "description": "Reemplazo de batería para celulares con problemas de autonomía. Baterías de alta calidad."}
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
            {"name": "Membresía Mensual", "price": 200.00, "description": "Acceso ilimitado a todas las áreas del gimnasio y clases grupales durante un mes."},
            {"name": "Membresía Trimestral", "price": 540.00, "description": "Ahorra con nuestro plan trimestral. Acceso completo a instalaciones y clases por 3 meses."},
            {"name": "Membresía Anual", "price": 1800.00, "description": "El mejor precio para tu compromiso a largo plazo. Un año de acceso ilimitado."},
            {"name": "Entrenamiento Personal (sesión)", "price": 80.00, "description": "Una hora de entrenamiento uno a uno con un instructor certificado para maximizar tus resultados."},
            {"name": "Plan Nutricional", "price": 150.00, "description": "Plan de alimentación personalizado creado por nuestro nutricionista para alcanzar tus objetivos de salud."}
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
            {"name": "Clase de Yoga (Individual)", "price": 50.00, "description": "Participa en una de nuestras clases grupales de Hatha, Vinyasa o Ashtanga. Apto para todos los niveles."},
            {"name": "Pack 10 Clases", "price": 400.00, "description": "Ahorra comprando un paquete de 10 clases para usar cuando quieras en un plazo de 3 meses."},
            {"name": "Masaje Relajante", "price": 120.00, "description": "Sesión de 60 minutos de masaje descontracturante para liberar tensiones y renovar tu energía."},
            {"name": "Terapia Reiki", "price": 150.00, "description": "Equilibra tus centros energéticos y encuentra la calma interior con una sesión de Reiki."},
            {"name": "Mat de Yoga Premium", "price": 180.00, "description": "Mat de yoga antideslizante y ecológico para una práctica segura y cómoda en casa o en el estudio."}
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
            {"name": "Curso Básico (3 meses)", "price": 600.00, "description": "Módulo trimestral para principiantes. Aprende los fundamentos del inglés para comunicarte en situaciones cotidianas."},
            {"name": "Curso Intermedio (3 meses)", "price": 650.00, "description": "Perfecciona tu gramática y fluidez. Módulo trimestral para consolidar tus conocimientos."},
            {"name": "Curso Avanzado (3 meses)", "price": 700.00, "description": "Domina el inglés con nuestro curso avanzado. Enfocado en conversación y vocabulario profesional."},
            {"name": "Clases Particulares (hora)", "price": 80.00, "description": "Clases personalizadas uno a uno para enfocarte en tus necesidades específicas. Flexibilidad de horarios."},
            {"name": "Material Didáctico", "price": 120.00, "description": "Libro de texto y workbook oficial de nuestro método de enseñanza. Válido para un nivel completo."}
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
            {"name": "Clase Individual (2 horas)", "price": 100.00, "description": "Sesión de apoyo de 2 horas para resolver dudas y reforzar temas de matemáticas, física o cálculo."},
            {"name": "Pack 10 Clases", "price": 850.00, "description": "Paquete de 10 clases de 2 horas cada una. Ideal para un seguimiento continuo durante el semestre."},
            {"name": "Preparación Examen", "price": 150.00, "description": "Sesión intensiva de 3 horas enfocada en la preparación para un examen específico."},
            {"name": "Resolución de Tareas", "price": 50.00, "description": "Servicio de ayuda para resolver prácticos y tareas complejas. Precio por hora."}
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
            {"name": "Sesión Fotográfica Personal", "price": 350.00, "description": "Sesión de 1 hora en estudio o exteriores. Incluye 15 fotos editadas en alta resolución."},
            {"name": "Cobertura de Boda", "price": 2500.00, "description": "Cobertura completa de tu boda, desde la preparación hasta la fiesta. Incluye álbum y video resumen."},
            {"name": "Sesión Quinceañera", "price": 800.00, "description": "Paquete completo para quinceañeras con sesión pre-evento, cobertura de la fiesta y photobook."},
            {"name": "Fotos de Producto", "price": 200.00, "description": "Fotografía profesional de tus productos para catálogos, e-commerce y redes sociales. Precio por pack de 10 productos."},
            {"name": "Video Promocional", "price": 1200.00, "description": "Producción de un video de hasta 1 minuto para promocionar tu negocio en redes sociales."}
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
            {"name": "Cumpleaños Infantil", "price": 1500.00, "description": "Organización completa de fiesta infantil para 30 niños. Incluye decoración, torta, animación y sorpresas."},
            {"name": "Evento Corporativo", "price": 3500.00, "description": "Planificación y ejecución de eventos para empresas: lanzamientos, aniversarios y conferencias."},
            {"name": "Boda Completa", "price": 8000.00, "description": "Servicio integral de wedding planner para que tu día especial sea perfecto y sin estrés."},
            {"name": "Baby Shower", "price": 1200.00, "description": "Organizamos un tierno y divertido baby shower. Incluye decoración temática, juegos y catering."},
            {"name": "Quinceañera", "price": 4500.00, "description": "Planificación de fiesta de 15 años de ensueño. Nos encargamos de cada detalle, desde el local hasta el catering."}
        ]
    }
]

def poblar_base_datos():
    with app.app_context():
        print("🚀 Iniciando población de base de datos...\n")

        # --- INICIO DE LA MEJORA: LIMPIAR LA BASE DE DATOS ---
        print("🧹 Limpiando tablas existentes para un inicio limpio...")
        try:
            # El orden es importante para respetar las Foreign Keys
            db.session.execute(db.text('DELETE FROM favorites'))
            db.session.execute(db.text('DELETE FROM products'))
            db.session.execute(db.text('DELETE FROM reviews'))
            db.session.execute(db.text('DELETE FROM users'))
            db.session.execute(db.text('DELETE FROM businesses'))
            db.session.commit()
            print("   ✅ Tablas limpiadas correctamente.")
        except Exception as e:
            print(f"   ⚠️  Advertencia: No se pudieron limpiar las tablas. Puede que sea la primera ejecución. Error: {e}")
            db.session.rollback()
        # --- FIN DE LA MEJORA ---
        
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
                        price=prod_data['price'],
                        description=prod_data.get('description'), # NUEVO: Añadir descripción
                        stock=random.randint(5, 50) # NUEVO: Stock aleatorio
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
    
    output_path = os.path.join(os.path.dirname(__file__), 'CREDENCIALES_NEGOCIOS.txt')
    # Guardar credenciales en archivo TXT
    with open(output_path, 'w', encoding='utf-8') as f:
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
    
    print(f"\n📄 Archivo de credenciales creado: {output_path}")
    print("\n🎉 ¡Proceso completado exitosamente!")
