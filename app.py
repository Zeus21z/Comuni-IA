import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import google.generativeai as genai
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
BASEDIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASEDIR, 'comuni_ia.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'comunia-secret-key-2025')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# MODELOS (IGUALES - PERFECTOS)
class Business(db.Model):
    __tablename__ = 'businesses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    logo = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(160), nullable=False, default="Santa Cruz, Bolivia")
    category = db.Column(db.String(100), nullable=False, default="Servicios")
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    reviews = db.relationship('Review', backref='business', lazy=True, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='business', lazy=True, cascade="all, delete-orphan")

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
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.create_all()

# DECORADOR PARA RUTAS PROTEGIDAS
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(id, *args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.business_id != id:
            abort(403)
        return f(id, *args, **kwargs)
    return decorated_function

# GEMINI (MEJORADO)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_MODEL = genai.GenerativeModel("gemini-2.5-flash")
else:
    GEMINI_MODEL = None

# RUTAS DE AUTENTICACIÓN
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
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
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

@app.route('/signup', methods=['GET', 'POST'], strict_slashes=False)
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not email or not password:
            return render_template('signup.html', error="Todos los campos son requeridos")
        
        if password != confirm_password:
            return render_template('signup.html', error="Las contraseñas no coinciden")
        
        if len(password) < 6:
            return render_template('signup.html', error="La contraseña debe tener al menos 6 caracteres")
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('signup.html', error="Este email ya está registrado")
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        return redirect(url_for('register'))
    
    return render_template('signup.html')

# RUTAS (IGUALES - FUNCIONALES)
@app.route('/', strict_slashes=False)
def home():
    # Obtener parámetros de búsqueda
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    
    # Query base
    query = Business.query
    
    # Aplicar filtros
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
    
    # Lista de categorías para el filtro
    categories = ["Gastronomía", "Moda y Ropa", "Servicios Profesionales", 
                  "Belleza y Cuidado Personal", "Hogar y Decoración", 
                  "Tecnología", "Salud y Bienestar", "Educación", "Otros"]
    
    return render_template('index.html', businesses=businesses, 
                         categories=categories, 
                         search_query=search_query,
                         category_filter=category_filter)

@app.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    categories = ["Gastronomía", "Moda y Ropa", "Servicios Profesionales", 
                  "Belleza y Cuidado Personal", "Hogar y Decoración", 
                  "Tecnología", "Salud y Bienestar", "Educación", "Otros"]
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        logo = request.form.get('logo', '').strip()
        location = request.form.get('location', 'Santa Cruz, Bolivia').strip() or "Santa Cruz, Bolivia"
        category = request.form.get('category', 'Otros').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()

        if not name or not description:
            return render_template('register.html', error="Nombre y descripción son obligatorios.", 
                                 form=request.form, categories=categories)

        business = Business(name=name, description=description, logo=logo, 
                          location=location, category=category, phone=phone,
                          email=email, whatsapp=whatsapp)
        db.session.add(business)
        db.session.commit()
        
        # Vincular con usuario si está logueado
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and not user.business_id:
                user.business_id = business.id
                db.session.commit()
        
        return redirect(url_for('profile', id=business.id))

    return render_template('register.html', categories=categories)

@app.route('/profile/<int:id>', strict_slashes=False)
def profile(id):
    business = Business.query.get_or_404(id)
    products = Product.query.filter_by(business_id=id).all()
    reviews = Review.query.filter_by(business_id=id).order_by(Review.created_at.desc()).all()
    
    # Calcular promedio de rating
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(business_id=id).scalar() or 0
    
    # Verificar si el usuario actual es el dueño
    is_owner = False
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.business_id == id:
            is_owner = True
    
    return render_template('profile.html', business=business, products=products, 
                         reviews=reviews, avg_rating=round(avg_rating, 1),
                         is_owner=is_owner)

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

    system_context = (
        "Eres el chatbot de Comuni IA. Responde con mensajes útiles y breves sobre marketing, visibilidad, "
        "buenas prácticas de perfil, uso de etiquetas locales (#SantaCruzBolivia, #EmprendimientoCruceño), "
        "participación en ferias locales (ex. Feria Barrio, Cambódromo), y cómo usar la plataforma Comuni IA. "
        "Evita temas fuera de este alcance."
    )

    try:
        resp = GEMINI_MODEL.generate_content(f"{system_context}\n\nUsuario: {user_msg}\nAsistente:")
        text = resp.text.strip() if hasattr(resp, "text") else "No tengo una respuesta en este momento."
        return jsonify({"reply": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RUTAS DE PRODUCTOS
@app.route('/api/products/<int:business_id>', methods=['POST'], strict_slashes=False)
@owner_required
def add_product(business_id):
    business = Business.query.get_or_404(business_id)
    data = request.get_json(silent=True) or {}
    
    name = data.get('name', '').strip()
    price = data.get('price', 0)
    image_url = data.get('image_url', '').strip()
    
    if not name or price <= 0:
        return jsonify({"error": "Nombre y precio válido son requeridos"}), 400
    
    product = Product(business_id=business_id, name=name, price=price, image_url=image_url)
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

@app.route('/api/products/<int:product_id>', methods=['DELETE'], strict_slashes=False)
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Verificar que el usuario sea dueño
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.business_id == product.business_id:
            db.session.delete(product)
            db.session.commit()
            return jsonify({"success": True})
    
    return jsonify({"error": "No autorizado"}), 403

# RUTAS DE RESEÑAS
@app.route('/api/reviews/<int:business_id>', methods=['POST'], strict_slashes=False)
def add_review(business_id):
    business = Business.query.get_or_404(business_id)
    data = request.get_json(silent=True) or {}
    
    author = data.get('author', '').strip()
    rating = data.get('rating', 0)
    comment = data.get('comment', '').strip()
    
    if not author or not comment or rating < 1 or rating > 5:
        return jsonify({"error": "Todos los campos son requeridos y rating debe ser 1-5"}), 400
    
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

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html', error_404=True), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True)