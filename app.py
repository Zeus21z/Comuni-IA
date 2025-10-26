import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, session, flash
from flask_sqlalchemy import SQLAlchemy
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
app.config['UPLOADED_IMAGES_ALLOW'] = IMAGES

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
    nit = db.Column(db.String(20), nullable=True)  # NUEVO CAMPO
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    email = db.Column(db.String(120), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    reviews = db.relationship('Review', backref='business', lazy=True, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='business', lazy=True, cascade="all, delete-orphan")
    favorited_by = db.relationship('User', secondary=favorites, lazy='subquery', backref=db.backref('favorite_businesses', lazy=True))
    viewed_by = db.relationship('User', secondary=business_views, lazy='subquery', backref=db.backref('viewed_businesses', lazy=True))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

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
    ci = db.Column(db.String(20), nullable=True)  # NUEVO CAMPO
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=db.func.now())
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # La relación a 'favorite_businesses' se define a través del backref en Business.favorited_by
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.create_all()
    # En bases existentes la tabla 'businesses' puede no tener columnas new (latitude/longitude).
    # Comprobamos y añadimos columnas faltantes con ALTER TABLE.
    try:
        # Para la tabla 'businesses'
        business_cols_info = db.session.execute(text("PRAGMA table_info(businesses)")).fetchall()
        business_cols = [row[1] for row in business_cols_info]
        if 'latitude' not in business_cols:
            db.session.execute(text("ALTER TABLE businesses ADD COLUMN latitude REAL"))
        if 'longitude' not in business_cols:
            db.session.execute(text("ALTER TABLE businesses ADD COLUMN longitude REAL"))
        if 'nit' not in business_cols:
            db.session.execute(text("ALTER TABLE businesses ADD COLUMN nit VARCHAR(20)"))

        # Para la tabla 'users'
        user_cols_info = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
        user_cols = [row[1] for row in user_cols_info]
        if 'ci' not in user_cols:
            db.session.execute(text("ALTER TABLE users ADD COLUMN ci VARCHAR(20)"))

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
            session['business_id'] = user.business_id # Añadir esta línea para guardar el business_id en la sesión
            flash(f'✅ ¡Bienvenido de vuelta, {user.email}!', 'success')
            
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
    flash('👋 Has cerrado sesión. ¡Vuelve pronto!', 'info')
    return redirect(url_for('home'))

@app.route('/join', methods=['GET', 'POST'], strict_slashes=False)
def join():
    categories = ["Gastronomía", "Moda y Ropa", "Servicios Profesionales", 
                  "Belleza y Cuidado Personal", "Hogar y Decoración", 
                  "Tecnología", "Salud y Bienestar", "Educación", "Otros"]
    
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.business_id:
            flash('⚠️ Ya tienes un negocio registrado. No puedes registrar otro.', 'warning')
        else:
            flash('⚠️ Para registrar un negocio, primero debes cerrar tu sesión de cliente actual.', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Datos de user
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        ci = request.form.get('ci', '').strip() # NUEVO CAMPO
        
        # Datos de business
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', 'Santa Cruz, Bolivia').strip() or "Santa Cruz, Bolivia"
        category = request.form.get('category', 'Otros').strip()
        phone = request.form.get('phone', '').strip()
        business_email = request.form.get('business_email', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        latitude = request.form.get('latitude')
        nit = request.form.get('nit', '').strip() # NUEVO CAMPO
        longitude = request.form.get('longitude')

        # Validaciones user
        if not email or not password or not confirm_password:
            return render_template('join.html', error="Campos de cuenta son requeridos", categories=categories, form_data=request.form)

        if password != confirm_password:
            return render_template('join.html', error="Contraseñas no coinciden", categories=categories, form_data=request.form)

        if len(password) < 6:
            return render_template('join.html', error="Contraseña debe tener al menos 6 caracteres", categories=categories, form_data=request.form)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('join.html', error="Email ya registrado", categories=categories, form_data=request.form)

        # Validaciones business
        if not name or not description:
            return render_template('join.html', error="Nombre y descripción del negocio son obligatorios", categories=categories, form_data=request.form)

        try:
            # 1. Manejo de imagen (logo) dentro del try
            logo = request.files.get('logo') if 'logo' in request.files else None
            logo_path = None
            if logo and logo.filename:
                logo_path = images.save(logo)

            # 2. Crear usuario y negocio en una transacción
            user = User(email=email, role='user', ci=ci) # Añadido 'ci'
            user.set_password(password)
            db.session.add(user)

            business = Business(name=name, description=description, logo=logo_path,
                              location=location, category=category, phone=phone,
                              email=business_email, whatsapp=whatsapp, nit=nit, # Añadido 'nit'
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
            flash('🎉 ¡Tu negocio ha sido registrado! Bienvenido a Comuni IA.', 'success')

            return redirect(url_for('profile', id=business.id))
        except Exception as e:
            db.session.rollback()
            return render_template('join.html', error=f"Error al registrar: {str(e)}", categories=categories, form_data=request.form)

    return render_template('join.html', categories=categories, form_data={})

@app.route('/register_client', methods=['GET', 'POST'], strict_slashes=False)
def register_client():
    if 'user_id' in session:
        flash('⚠️ Ya has iniciado sesión. No puedes registrar una nueva cuenta de cliente.', 'warning')
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
        flash('✅ ¡Registro exitoso! Bienvenido a Comuni IA.', 'success')
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
    
    # MEJORA: Mostrar solo negocios activos en la página principal
    query = query.filter(Business.is_active == True)

    businesses = query.order_by(Business.id.desc()).all()
    
    categories = ["Gastronomía", "Moda y Ropa", "Servicios Profesionales", 
                  "Belleza y Cuidado Personal", "Hogar y Decoración", 
                  "Tecnología", "Salud y Bienestar", "Educación", "Otros"]
    
    return render_template('index.html', businesses=businesses, 
                         categories=categories, 
                         search_query=search_query,
                         category_filter=category_filter)

@app.route('/profile/<int:id>', strict_slashes=False)
def profile(id):
    business = Business.query.get_or_404(id)
    products = Product.query.filter_by(business_id=id).all()
    reviews_query = Review.query.filter_by(business_id=id).order_by(Review.created_at.desc()).all()
    
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(business_id=id).scalar() or 0
    
    is_owner = False
    is_favorited = False
    
    # Lógica de conteo de visitas y estado de favorito/dueño
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            if user.business_id == id:
                is_owner = True
            
            if business in user.favorite_businesses:
                is_favorited = True
            
            # Contar la visita solo si el usuario no es el dueño y no ha visitado antes
            if not is_owner and business not in user.viewed_businesses:
                user.viewed_businesses.append(business)
                db.session.commit()

    view_count = len(business.viewed_by)
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

def format_gemini_response(text):
    """Convierte Markdown simple (negritas) a HTML."""
    import re
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    return text

@app.route('/api/chat', methods=['POST'], strict_slashes=False)
def chat():
    if not GEMINI_MODEL:
        return jsonify({"error": "Gemini no configurado. Define GEMINI_API_KEY en .env"}), 500

    data = request.get_json(silent=True) or {}
    user_msg = (data.get('message') or "").strip()
    if not user_msg:
        return jsonify({"error": "Falta 'message'"}), 400

    # --- LIMPIEZA Y PREPARACIÓN DEL MENSAJE ---
    import re
    import unicodedata

    cleaned_msg = user_msg.lower()
    cleaned_msg = re.sub(r'[^\w\s]', '', cleaned_msg)
    cleaned_msg = ''.join(
        c for c in unicodedata.normalize('NFD', cleaned_msg)
        if unicodedata.category(c) != 'Mn'
    )

    # --- DETECCIÓN DE INTENCIÓN ---
    search_keywords = [
        'busco', 'recomienda', 'necesito', 'donde hay', 'quiero', 'encuentra',
        'negocio', 'tienda', 'servicio', 'comida', 'ropa', 'restaurante',
        'menu', 'carta', 'producto'
    ]
    is_search_intent = any(keyword in cleaned_msg for keyword in search_keywords)
    is_menu_intent = 'menu' in cleaned_msg or 'carta' in cleaned_msg
    is_short_message = len(cleaned_msg.split()) <= 2

    # --- VARIABLES PARA RESULTADOS ---
    businesses_found = []
    response_context = ""

    # --- BÚSQUEDA EN BASE DE DATOS ---
    search_terms = [t for t in cleaned_msg.split() if len(t) > 2]

    if is_search_intent and not is_menu_intent:
        # Buscar coincidencias en negocios
        filters = [
            db.or_(
                Business.name.ilike(f'%{term}%'),
                Business.description.ilike(f'%{term}%'),
                Business.category.ilike(f'%{term}%')
            ) for term in search_terms
        ]
        if filters:
            businesses_found = Business.query.filter(db.or_(*filters)).limit(5).all()

        # Buscar coincidencias también en productos
        product_filters = [
            db.or_(
                Product.name.ilike(f"%{term}%"),
                Product.description.ilike(f"%{term}%")
            ) for term in search_terms
        ]
        if product_filters:
            product_results = Product.query.filter(db.or_(*product_filters)).limit(5).all()
            for p in product_results:
                if p.business not in businesses_found:
                    businesses_found.append(p.business)

        # Armar el contexto de respuesta
        if not businesses_found:
            response_context = "No se encontraron negocios que coincidan con tu búsqueda."
        else:
            response_context = "Encontré estos lugares relacionados:\n\n"
            for b in businesses_found:
                response_context += f"🏪 <strong>{b.name}</strong> — {b.category}\n"
                if b.description:
                    response_context += f"{b.description[:120]}...\n"
                response_context += f"📍 <a href='/profile/{b.id}'>Ver perfil</a>\n"

                productos = Product.query.filter_by(business_id=b.id).limit(3).all()
                if productos:
                    response_context += "🍽️ Menú destacado:\n"
                    for p in productos:
                        response_context += f"• {p.name} — {p.price:.2f} Bs\n"
                    response_context += "\n"
                else:
                    response_context += "\n"

    elif is_menu_intent:
        # --- SI PIDE UN MENÚ DIRECTO ---
        name_match = re.search(r'menu (de|del)? ([\w\s]+)', cleaned_msg)
        if name_match:
            business_name = name_match.group(2).strip()
            business = Business.query.filter(Business.name.ilike(f"%{business_name}%")).first()
            if business:
                productos = Product.query.filter_by(business_id=business.id).all()
                if productos:
                    response_context = f"🍽️ Menú de {business.name}:\n"
                    for p in productos:
                        response_context += f"• {p.name} — {p.price:.2f} Bs\n"
                    response_context += f"\n📍 <a href='/profile/{business.id}'>Ver más del negocio</a>"
                else:
                    response_context = f"{business.name} no tiene productos registrados todavía."
            else:
                response_context = f"No encontré un negocio llamado '{business_name}'."
        else:
            response_context = "Por favor, dime el nombre del negocio del que quieres ver el menú."

    else:
        # --- CONVERSACIÓN GENERAL ---
        final_prompt = (
            "Eres un asistente virtual amigable y servicial para 'Comuni IA', "
            "un directorio de negocios locales en Santa Cruz, Bolivia. "
            "Responde de forma breve y natural. "
            "Si te preguntan qué puedes hacer, explica que puedes ayudar a encontrar negocios, productos o menús.\n\n"
            f"Usuario: {user_msg}\nAsistente:"
        )
        try:
            resp = GEMINI_MODEL.generate_content(final_prompt)
            text = resp.text.strip() if hasattr(resp, "text") else "No tengo una respuesta ahora."
            return jsonify({"reply": format_gemini_response(text)})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # --- PROMPT FINAL PARA GEMINI ---
    final_prompt = (
        "Eres el asistente de 'Comuni IA', un directorio de negocios locales en Santa Cruz, Bolivia. "
        "Responde de forma amable y útil según la búsqueda del usuario. "
        "Muestra los negocios o menús encontrados de manera clara.\n\n"
        f"Consulta del usuario: {user_msg}\n\n"
        f"Contexto encontrado:\n{response_context}\n\n"
        "Redacta una respuesta amigable para el usuario."
    )

    try:
        resp = GEMINI_MODEL.generate_content(final_prompt)
        text = resp.text.strip() if hasattr(resp, "text") else response_context
        return jsonify({"reply": format_gemini_response(text)})
    except Exception:
        return jsonify({"reply": format_gemini_response(response_context)})

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
        return jsonify({"error": "El comentario y una calificación de 1 a 5 son requeridos."} ), 400
    
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

# RUTAS ADMIN
@app.route('/admin/dashboard', strict_slashes=False)
@admin_required
def admin_dashboard():
    # Estadísticas para el dashboard
    stats = {
        'total_users': User.query.count(),
        'total_businesses': Business.query.count(),
        'total_products': Product.query.count(),
        'total_reviews': Review.query.count()
    }
    
    # Lista de todos los negocios con el email del dueño
    businesses_with_owners = db.session.query(Business, User.email).outerjoin(User, Business.id == User.business_id).order_by(Business.id.desc()).all()
    
    # Lista de todos los usuarios
    all_users = User.query.order_by(User.created_at.desc()).all()

    return render_template('admin_dashboard.html', 
                           stats=stats, 
                           businesses_with_owners=businesses_with_owners,
                           all_users=all_users)

@app.route('/admin/toggle_business_status/<int:id>', methods=['POST'], strict_slashes=False)
@admin_required
def toggle_business_status(id):
    """
    Activa o desactiva un negocio (Soft Delete).
    Si se desactiva un negocio, el usuario dueño se desvincula.
    """
    business = Business.query.get_or_404(id)
    new_status = not business.is_active
    action = "reactivado" if new_status else "desactivado"

    try:
        business.is_active = new_status

        # Si se desactiva, desvincular al dueño para que pueda registrar otro negocio si lo desea.
        if not new_status:
            user = User.query.filter_by(business_id=id).first()
            if user:
                user.business_id = None

        db.session.commit()
        return jsonify({"success": True, "message": f"Negocio '{business.name}' {action}."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/admin/toggle_user_status/<int:user_id>', methods=['POST'], strict_slashes=False)
@admin_required
def toggle_user_status(user_id):
    """
    Activa o desactiva un usuario (Soft Delete).
    Si se desactiva un usuario, su negocio asociado también se desactiva.
    """
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        return jsonify({"error": "No se puede desactivar a un administrador."}), 403

    new_status = not user.is_active
    action = "reactivado" if new_status else "desactivado"

    try:
        user.is_active = new_status

        # Si se desactiva un usuario, también se desactiva su negocio.
        if not new_status and user.business_id:
            business = Business.query.get(user.business_id)
            if business:
                business.is_active = False

        db.session.commit()
        return jsonify({"success": True, "message": f"Usuario '{user.email}' {action}."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ============================================
# NUEVAS RUTAS DE ELIMINACIÓN PERMANENTE
# ============================================

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'], strict_slashes=False)
@admin_required
def delete_user(user_id):
    """
    Elimina permanentemente un usuario y todos sus datos relacionados.
    Esto incluye: el usuario, sus negocios, productos de sus negocios, 
    y reseñas de sus negocios.
    """
    user = User.query.get_or_404(user_id)
    
    # No permitir eliminar a otros administradores
    if user.role == 'admin':
        return jsonify({'success': False, 'error': 'No se puede eliminar a un administrador'}), 403
    
    try:
        # 1. Si el usuario tiene un negocio asociado
        if user.business_id:
            business = Business.query.get(user.business_id)
            if business:
                # Eliminar productos del negocio
                Product.query.filter_by(business_id=business.id).delete()
                
                # Eliminar reseñas del negocio
                Review.query.filter_by(business_id=business.id).delete()
                
                # Limpiar relaciones many-to-many
                business.favorited_by.clear()  # Eliminar de favoritos
                business.viewed_by.clear()      # Eliminar vistas
                
                # Eliminar logo si existe
                if business.logo:
                    try:
                        logo_path = images.path(business.logo)
                        if os.path.exists(logo_path):
                            os.remove(logo_path)
                    except Exception as e:
                        print(f"Advertencia: No se pudo eliminar el logo: {e}")
                
                # Eliminar el negocio
                db.session.delete(business)
        
        # 2. Eliminar reseñas hechas por el usuario (usando el email como autor)
        Review.query.filter_by(author=user.email).delete()
        
        # 3. Limpiar relaciones many-to-many del usuario
        user.favorite_businesses.clear()
        user.viewed_businesses.clear()
        
        # 4. Eliminar el usuario
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Usuario "{user.email}" eliminado correctamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Error al eliminar usuario: {str(e)}'}), 500


@app.route('/admin/delete_business/<int:id>', methods=['POST'], strict_slashes=False)
@admin_required
def delete_business(id):
    """
    Elimina permanentemente un negocio y todos sus datos relacionados.
    Esto incluye: productos, reseñas y relaciones con usuarios.
    """
    business = Business.query.get_or_404(id)
    
    try:
        # 1. Eliminar productos del negocio
        Product.query.filter_by(business_id=id).delete()
        
        # 2. Eliminar reseñas del negocio
        Review.query.filter_by(business_id=id).delete()
        
        # 3. Desvincular al dueño del negocio (si existe)
        owner = User.query.filter_by(business_id=id).first()
        if owner:
            owner.business_id = None
        
        # 4. Limpiar relaciones many-to-many
        business.favorited_by.clear()  # Eliminar de favoritos de usuarios
        business.viewed_by.clear()      # Eliminar registro de vistas
        
        # 5. Eliminar archivos de imagen si existen
        if business.logo:
            try:
                logo_path = images.path(business.logo)
                if os.path.exists(logo_path):
                    os.remove(logo_path)
            except Exception as e:
                print(f"Advertencia: No se pudo eliminar el logo: {e}")
        
        # 6. Eliminar el negocio
        db.session.delete(business)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Negocio "{business.name}" eliminado correctamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Error al eliminar negocio: {str(e)}'}), 500

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    # Si la petición es AJAX, devolver JSON. Si no, renderizar plantilla.
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(error="Recurso no encontrado"), 404
    return render_template('index.html', error_404=True), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify(error=str(e)), 500

@app.errorhandler(403)
def forbidden(e):
    return jsonify(error="No tienes permiso para realizar esta acción"), 403

if __name__ == '__main__':
    app.run(debug=True)