import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from sqlalchemy import text
from dotenv import load_dotenv
import google.generativeai as genai
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_uploads import UploadSet, configure_uploads, IMAGES

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
BASEDIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASEDIR, 'comuni_ia.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'comunia-secret-key-2025')
app.config['UPLOADED_IMAGES_DEST'] = os.path.join(BASEDIR, 'static', 'uploads')
app.config['UPLOADED_IMAGES_ALLOW'] = IMAGES  # Solo imágenes (jpg, png, etc.)
csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# CONFIGURACIÓN DE SUBIDAS
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

# Helper table for the many-to-many relationship between users and favorite businesses
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('business_id', db.Integer, db.ForeignKey('businesses.id'), primary_key=True)
)

# Helper table for the many-to-many relationship for business views
business_views = db.Table('business_views',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('business_id', db.Integer, db.ForeignKey('businesses.id'), primary_key=True)
)

# MODELOS (ACTUALIZADO: logo y image_url ahora guardan rutas relativas)
class Business(db.Model):
    __tablename__ = 'businesses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    logo = db.Column(db.String(500), nullable=True)  # Ruta relativa a static/uploads
    location = db.Column(db.String(160), nullable=False, default="Santa Cruz, Bolivia")
    category = db.Column(db.String(100), nullable=False, default="Servicios")
    phone = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    email = db.Column(db.String(120), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    reviews = db.relationship('Review', backref='business', lazy=True, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='business', lazy=True, cascade="all, delete-orphan")
    favorited_by = db.relationship('User', secondary=favorites, lazy='subquery', backref=db.backref('favorite_businesses', lazy=True))
    viewed_by = db.relationship('User', secondary=business_views, lazy='subquery', backref=db.backref('viewed_businesses', lazy=True))

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'author': self.author,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%d/%m/%Y') if self.created_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)  # Descripción detallada del producto
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)  # Ruta relativa a static/uploads

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=True)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=db.func.now())
    # La relación a 'favorite_businesses' se define a través del backref en Business.favorited_by
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.create_all()
    # En bases existentes la tabla 'businesses' puede no tener columnas new (latitude/longitude).
    # Comprobamos y añadimos columnas faltantes con ALTER TABLE (SQLite soporta ADD COLUMN simple).
    try:
        tbl_info = db.session.execute(text("PRAGMA table_info(businesses) ")).fetchall()
        existing_cols = [row[1] for row in tbl_info]
        if 'latitude' not in existing_cols:
            db.session.execute(text("ALTER TABLE businesses ADD COLUMN latitude REAL"))
        if 'longitude' not in existing_cols:
            db.session.execute(text("ALTER TABLE businesses ADD COLUMN longitude REAL"))
        db.session.commit()
    except Exception as e:
        # No detener el arranque si falla esta corrección automática; informar en consola.
        print('Advertencia: no se pudo asegurar columnas latitude/longitude en businesses:', e)

# DECORADORES
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        business_id = kwargs.get('id') or kwargs.get('business_id')
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not business_id or user.business_id != business_id:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# GEMINI (SIN CAMBIOS)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_MODEL = genai.GenerativeModel("gemini-2.5-flash")
else:
    GEMINI_MODEL = None

# RUTAS DE AUTENTICACIÓN (ACTUALIZADO: /join con subida de logo)
@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            return render_template('login.html', error="Email y contraseña son requeridos")
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.business_id:
                return redirect(url_for('profile', id=user.business_id))
            else:
                return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Email o contraseña incorrectos")
    
    return render_template('login.html')

@app.route('/logout', strict_slashes=False)
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/join', methods=['GET', 'POST'], strict_slashes=False)
def join():
    categories = ["Gastronomía", "Moda y Ropa", "Servicios Profesionales", 
                  "Belleza y Cuidado Personal", "Hogar y Decoración", 
                  "Tecnología", "Salud y Bienestar", "Educación", "Otros"]
    
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Datos de user
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Datos de business
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', 'Santa Cruz, Bolivia').strip() or "Santa Cruz, Bolivia"
        category = request.form.get('category', 'Otros').strip()
        phone = request.form.get('phone', '').strip()
        business_email = request.form.get('business_email', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        # Validaciones user
        if not email or not password or not confirm_password:
            return render_template('join.html', error="Campos de cuenta son requeridos", form=request.form, categories=categories)

        if password != confirm_password:
            return render_template('join.html', error="Contraseñas no coinciden", form=request.form, categories=categories)

        if len(password) < 6:
            return render_template('join.html', error="Contraseña debe tener al menos 6 caracteres", form=request.form, categories=categories)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('join.html', error="Email ya registrado", form=request.form, categories=categories)

        # Validaciones business
        if not name or not description:
            return render_template('join.html', error="Nombre y descripción del negocio son obligatorios", form=request.form, categories=categories)

        try:
            # 1. Manejo de imagen (logo) dentro del try
            logo = request.files.get('logo') if 'logo' in request.files else None
            logo_path = None
            if logo and logo.filename:
                logo_path = images.save(logo)

            # 2. Crear usuario y negocio en una transacción
            user = User(email=email, role='user')
            user.set_password(password)
            db.session.add(user)

            business = Business(name=name, description=description, logo=logo_path,
                              location=location, category=category, phone=phone,
                              email=business_email, whatsapp=whatsapp,
                              latitude=float(latitude) if latitude else None,
                              longitude=float(longitude) if longitude else None)
            db.session.add(business)

            # Es importante hacer flush() para que SQLAlchemy asigne los IDs
            # antes de vincularlos.
            db.session.flush()

            # 3. Vincular usuario con negocio
            user.business_id = business.id

            # 4. Confirmar la transacción completa
            db.session.commit()

            # Iniciar sesión
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role

            return redirect(url_for('profile', id=business.id))
        except Exception as e:
            db.session.rollback()
            return render_template('join.html', error=f"Error al registrar: {str(e)}",
                                 form=request.form, categories=categories)

    return render_template('join.html', categories=categories)

@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})

@app.route('/register_client', methods=['GET', 'POST'], strict_slashes=False)
def register_client():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not email or not password or not confirm_password:
            return render_template('register_client.html', error="Todos los campos son requeridos.")

        if password != confirm_password:
            return render_template('register_client.html', error="Las contraseñas no coinciden.")

        if len(password) < 6:
            return render_template('register_client.html', error="La contraseña debe tener al menos 6 caracteres.")

        if User.query.filter_by(email=email).first():
            return render_template('register_client.html', error="Este email ya está registrado.")

        user = User(email=email, role='client') # Nuevo rol 'client'
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Iniciar sesión y redirigir a la home
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_role'] = user.role
        return redirect(url_for('home'))

    return render_template('register_client.html')


@app.route('/', strict_slashes=False)
def home():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    
    query = Business.query
    
    if search_query:
        query = query.filter(
            db.or_(
                Business.name.ilike(f'%{search_query}%'),
                Business.description.ilike(f'%{search_query}%')
            )
        )
    
    if category_filter and category_filter != 'Todas las categorías':
        query = query.filter(Business.category == category_filter)
    
    businesses = query.order_by(Business.id.desc()).all()
    
    categories = ["Gastronomía", "Moda y Ropa", "Servicios Profesionales", 
                  "Belleza y Cuidado Personal", "Hogar y Decoración", 
                  "Tecnología", "Salud y Bienestar", "Educación", "Otros"]
    
    return render_template('index.html', businesses=businesses, 
                         categories=categories, 
                         search_query=search_query,
                         category_filter=category_filter)

@app.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    return redirect(url_for('join'))

@app.route('/profile/<int:id>', strict_slashes=False)
def profile(id):
    business = Business.query.get_or_404(id)
    products = Product.query.filter_by(business_id=id).all()
    reviews_query = Review.query.filter_by(business_id=id).order_by(Review.created_at.desc()).all()
    
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(business_id=id).scalar() or 0
    
    is_owner = False
    is_favorited = False
    # --- INICIO LÓGICA DE CONTEO DE VISITAS ---
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            if user.business_id == id:
                is_owner = True
            else:
                # Contar la visita solo si el usuario no es el dueño
                # y si no ha visitado antes este perfil.
                if business not in user.viewed_businesses:
                    user.viewed_businesses.append(business)
                    db.session.commit()

            # Comprobar si este negocio está en la lista de favoritos del usuario
            if business in user.favorite_businesses:
                is_favorited = True
    view_count = len(business.viewed_by)
    # --- FIN LÓGICA DE CONTEO DE VISITAS ---
    return render_template('profile.html', business=business, products=products,
                         reviews=[r.to_dict() for r in reviews_query],
                         avg_rating=round(avg_rating, 1), view_count=view_count,
                         is_owner=is_owner,
                         is_favorited=is_favorited)

@app.route('/api/business/<int:business_id>/favorite', methods=['POST'], strict_slashes=False)
@login_required
def toggle_favorite(business_id):
    user = User.query.get(session['user_id'])
    business = Business.query.get_or_404(business_id)
    if business in user.favorite_businesses:
        user.favorite_businesses.remove(business)
        db.session.commit()
        return jsonify({"success": True, "favorited": False})
    else:
        user.favorite_businesses.append(business)
        db.session.commit()
        return jsonify({"success": True, "favorited": True})

@app.route('/profile/<int:id>/update_logo', methods=['POST'], strict_slashes=False)
@owner_required
def update_logo(id):
    business = Business.query.get_or_404(id)
    logo = request.files.get('logo')

    if not logo or not logo.filename:
        return redirect(url_for('profile', id=id))

    try:
        # Borrar logo antiguo si existe
        if business.logo:
            old_logo_path = images.path(business.logo)
            if os.path.exists(old_logo_path):
                os.remove(old_logo_path)
        
        business.logo = images.save(logo)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(url_for('profile', id=id))

@app.route('/profile/<int:id>/edit', methods=['POST'], strict_slashes=False)
@owner_required
def edit_business(id):
    business = Business.query.get_or_404(id)
    
    # Obtener datos del formulario
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()
    phone = request.form.get('phone', '').strip()
    business_email = request.form.get('business_email', '').strip()
    whatsapp = request.form.get('whatsapp', '').strip()
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    if not name or not description or not category:
        # Aquí podrías usar `flash` para un mejor feedback, pero por ahora redirigimos.
        return redirect(url_for('profile', id=id))

    business.name = name
    business.description = description
    business.category = category
    business.phone = phone
    business.email = business_email
    business.whatsapp = whatsapp
    business.latitude = float(latitude) if latitude else None
    business.longitude = float(longitude) if longitude else None
    db.session.commit()
    return redirect(url_for('profile', id=id))

@app.route('/api/ai/suggestions/<int:id>', methods=['GET'], strict_slashes=False)
def ai_suggestions(id):
    business = Business.query.get_or_404(id)
    if not GEMINI_MODEL:
        return jsonify({"error": "Gemini no configurado. Define GEMINI_API_KEY en .env"}), 500

    prompt = (
        "Eres un asistente de marketing para emprendimientos locales de Santa Cruz, Bolivia. "
        "Genera 5 sugerencias prácticas y accionables (títulos y bullets) para mejorar la visibilidad y ventas "
        f"del negocio:\n\nNombre: {business.name}\nDescripción: {business.description}\nUbicación: {business.location}\n\n"
        "Formato:\n- Título breve\n- 2 a 3 bullets con acciones concretas (menciona redes locales, hashtags, alianzas, ferias/mercados cruceños)."
    )
    try:
        resp = GEMINI_MODEL.generate_content(prompt)
        text = resp.text.strip() if hasattr(resp, "text") else "No hay respuesta."
        return jsonify({"business_id": business.id, "suggestions": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'], strict_slashes=False)
def chat():
    if not GEMINI_MODEL:
        return jsonify({"error": "Gemini no configurado. Define GEMINI_API_KEY en .env"}), 500

    data = request.get_json(silent=True) or {}
    user_msg = (data.get('message') or "").strip()
    if not user_msg:
        return jsonify({"error": "Falta 'message'"}), 400

    # --- INICIO DE LA MEJORA DEL CHATBOT ---
    import re
    import unicodedata

    # 1. Limpiar el mensaje del usuario
    cleaned_msg = user_msg.lower()
    cleaned_msg = re.sub(r'[^\w\s]', '', cleaned_msg)
    cleaned_msg = ''.join(c for c in unicodedata.normalize('NFD', cleaned_msg) if unicodedata.category(c) != 'Mn')

    # 2. Determinar la intención del usuario
    # Palabras clave que indican una búsqueda de negocio.
    search_keywords = ['busco', 'recomienda', 'necesito', 'donde hay', 'quiero', 'encuentra', 'negocio', 'tienda', 'servicio', 'comida', 'ropa']
    is_search_intent = any(keyword in cleaned_msg for keyword in search_keywords)
    is_short_message = len(cleaned_msg.split()) <= 2

    relevant_businesses = []
    business_context_str = "No se ha realizado una búsqueda de negocios."

    # 3. Si la intención es buscar (o no es un mensaje corto), buscar en la BD
    if is_search_intent or not is_short_message:
        search_terms = cleaned_msg.split()
        filters = [
            db.or_(
                Business.name.ilike(f'%{term}%'),
                Business.description.ilike(f'%{term}%'),
                Business.category.ilike(f'%{term}%')
            ) for term in search_terms if len(term) > 2
        ]
        
        if filters:
            found_businesses = Business.query.filter(db.or_(*filters)).limit(5).all()
            for b in found_businesses:
                relevant_businesses.append(f"- Nombre: {b.name}, Categoría: {b.category}, Descripción: {b.description[:150]}...")
        
        business_context_str = "\n".join(relevant_businesses) if relevant_businesses else "No se encontraron negocios relevantes en el directorio para esta búsqueda."

    # 4. Construir el prompt final para la IA
    if is_search_intent or not is_short_message:
        # Prompt enfocado en búsqueda
        final_prompt = (
            "Eres un asistente virtual para 'Comuni IA', un directorio de negocios locales en Santa Cruz, Bolivia. "
            "Tu objetivo es ayudar a los usuarios a encontrar el negocio que necesitan. "
            "Basado en la pregunta del usuario y la lista de negocios que te proporciono, recomienda la mejor opción y explica por qué. "
            "Si ningún negocio parece adecuado, informa al usuario que no encontraste una coincidencia y anímale a explorar el directorio manualmente.\n\n"
            f"LISTA DE NEGOCIOS ENCONTRADOS:\n{business_context_str}\n\n"
            f"PREGUNTA DEL USUARIO:\n'{user_msg}'\n\n"
            "Asistente:"
        )
    else:
        # Prompt para conversación general
        final_prompt = (
            "Eres un asistente virtual amigable y servicial para 'Comuni IA', un directorio de negocios locales. "
            "Estás teniendo una conversación general. Responde de forma breve y natural. Si te preguntan qué puedes hacer, explica que puedes ayudar a encontrar negocios o dar consejos de marketing.\n\n"
            f"Usuario: {user_msg}\nAsistente:"
        )
    # --- FIN DE LA MEJORA DEL CHATBOT ---

    try:
        # Usamos el nuevo prompt dinámico
        resp = GEMINI_MODEL.generate_content(final_prompt)
        text = resp.text.strip() if hasattr(resp, "text") else "No tengo una respuesta en este momento."
        return jsonify({"reply": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RUTAS DE PRODUCTOS (ACTUALIZADO: subida de imagen)
@app.route('/api/products/<int:business_id>', methods=['POST'], strict_slashes=False)
@owner_required
def add_product(business_id):
    business = Business.query.get_or_404(business_id)
    image = request.files.get('image') if 'image' in request.files else None
    
    name = request.form.get('name', '').strip()
    price = float(request.form.get('price', 0))
    image_path = None
    
    if image and image.filename:
        try:
            image_path = images.save(image)
        except Exception as e:
            return jsonify({"error": f"Error al subir imagen: {str(e)}"}), 500
    
    if not name or price <= 0:
        return jsonify({"error": "Nombre y precio válido son requeridos"}), 400
    
    product = Product(business_id=business_id, name=name, price=price, image_url=image_path)
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "product": {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url
        }
    })

@app.route('/api/products/<int:product_id>', methods=['DELETE', 'PUT'], strict_slashes=False)
def manage_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.business_id == product.business_id:
            if request.method == 'DELETE':
                db.session.delete(product)
                db.session.commit()
                return jsonify({"success": True})
            elif request.method == 'PUT':
                name = request.form.get('name', '').strip()
                price = float(request.form.get('price', 0))
                description = request.form.get('description', '').strip()
                
                if not name or price <= 0:
                    return jsonify({"error": "Nombre y precio válido son requeridos"}), 400
                
                image = request.files.get('image') if 'image' in request.files else None
                if image and image.filename:
                    try:
                        # Si hay una imagen anterior, la borramos
                        if product.image_url:
                            old_image_path = images.path(product.image_url)
                            if os.path.exists(old_image_path):
                                os.remove(old_image_path)
                        product.image_url = images.save(image)
                    except Exception as e:
                        return jsonify({"error": f"Error al subir imagen: {str(e)}"}), 500
                
                product.name = name
                product.price = price
                product.description = description
                db.session.commit()
                return jsonify({"success": True})
    
    abort(403) # abort() es manejado por el errorhandler y devuelve JSON

# RUTAS DE RESEÑAS (SIN CAMBIOS)
@app.route('/api/reviews/<int:business_id>', methods=['POST'], strict_slashes=False)
@login_required # Proteger la ruta, solo usuarios logueados pueden comentar
def add_review(business_id):
    business = Business.query.get_or_404(business_id)
    data = request.get_json(silent=True) or {}
    
    # El autor es el usuario logueado, no se toma del formulario.
    author = session.get('user_email', 'Anónimo')
    comment = data.get('comment', '').strip()
    
    try:
        rating = int(data.get('rating', 0))
    except (ValueError, TypeError):
        rating = 0

    if not comment or rating < 1 or rating > 5:
        return jsonify({"error": "El comentario y una calificación de 1 a 5 son requeridos."}), 400
    
    review = Review(business_id=business_id, author=author, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    
    return jsonify({"success": True, "review": review.to_dict()})

@app.route('/api/reviews/<int:business_id>', methods=['GET'], strict_slashes=False)
def get_reviews(business_id):
    reviews = Review.query.filter_by(business_id=business_id).order_by(Review.created_at.desc()).all()
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(business_id=business_id).scalar() or 0
    
    return jsonify({
        "reviews": [r.to_dict() for r in reviews],
        "avg_rating": round(avg_rating, 1),
        "total": len(reviews)
    })

# RUTAS ADMIN (SIN CAMBIOS)
@app.route('/admin/dashboard', strict_slashes=False)
@admin_required
def admin_dashboard():
    businesses = Business.query.all()
    return render_template('admin_dashboard.html', businesses=businesses)

@app.route('/admin/delete_business/<int:id>', methods=['POST'], strict_slashes=False)
@admin_required
def delete_business(id):
    business = Business.query.get_or_404(id)
    user = User.query.filter_by(business_id=id).first()
    
    try:
        if user:
            db.session.delete(user)
        db.session.delete(business)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html', error_404=True), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify(error=str(e)), 500

@app.errorhandler(403)
def forbidden(e):
    return jsonify(error="No tienes permiso para realizar esta acción"), 403

if __name__ == '__main__':
    app.run(debug=True)