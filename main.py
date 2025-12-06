import os
import json
import secrets
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sqlalchemy.orm import Session
from app.db.models import db, Place, MenuItem, Comment, User
from app.utils import update_place_rating
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Api, Resource, fields

# --- CONFIGURACIÓN DE CARPETAS ---
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)

# --- CONFIGURACIÓN DE CORS (Híbrida: Tu configuración permisiva) ---
CORS(app, resources={r"/*": {"origins": "*"}})

# --- CONFIGURACIÓN DE FLASK-RESTX (La parte de tu compañera) ---
# Esto genera la documentación automática en /docs
api = Api(app, 
          title="Cucei Foods API", 
          version="1.0", 
          description="Documentación de la API Backend", 
          doc='/docs')

# --- CONFIGURACIÓN DE BASE DE DATOS ---
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

local_db_uri = f'postgresql://postgres:{os.environ.get("DB_PASSWORD", "contraseña_local_aqui")}@localhost:5432/cuceifoods'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or local_db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ERROR_404_HELP'] = False # Para evitar conflictos de rutas con React si fuera necesario

# Secret key
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

db.init_app(app)

# -------------------
# Helpers
# -------------------

def get_session():
    return Session(db.engine)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------
# NAMESPACES & MODELS (Para la documentación)
# -------------------

api_ns = api.namespace('api', path='/api', description='Endpoints principales')

# Modelos de datos para Swagger
menu_item_model = api_ns.model('MenuItem', {
    'category': fields.String(required=False, description='Categoría del plato'),
    'dish_name': fields.String(required=True, description='Nombre del platillo'),
    'price': fields.Float(required=True, description='Precio')
})

place_model = api_ns.model('Place', {
    'id': fields.String(readOnly=True, description='ID del lugar'),
    'name': fields.String(required=True, description='Nombre del lugar'),
    'schedule': fields.Raw(required=False, description='Horario (objeto JSON)'),
    'category': fields.String(required=False, description='Categoría'),
    'image_url': fields.String(required=False, description='URL de la imagen'),
    'menu': fields.List(fields.Nested(menu_item_model), description='Lista de elementos del menú'),
    'rating': fields.Float(description='Calificación promedio'),
    'num_ratings': fields.Integer(description='Número de calificaciones'),
    'latest_comment': fields.String(description='Último comentario')
})

comment_model = api_ns.model('Comment', {
    'id': fields.String(readOnly=True, description='ID del comentario'),
    'place_id': fields.String(required=True, description='ID del lugar'),
    'user_id': fields.String(required=False, description='ID del usuario'),
    'user_name': fields.String(required=False, description='Nombre del usuario'),
    'text': fields.String(required=True, description='Texto del comentario'),
    'rating': fields.Integer(required=False, description='Calificación')
})

id_model = api_ns.model('CreatedId', {
    'id': fields.String(description='ID creado')
})

message_model = api_ns.model('Message', {
    'message': fields.String(description='Mensaje informativo')
})

register_model = api_ns.model('Register', {
    'name': fields.String(required=True, description='Nombre del usuario'),
    'email': fields.String(required=True, description='Correo electrónico'),
    'password': fields.String(required=True, description='Contraseña')
})

login_model = api_ns.model('Login', {
    'email': fields.String(required=True, description='Correo electrónico'),
    'password': fields.String(required=True, description='Contraseña')
})

login_response_model = api_ns.model('LoginResponse', {
    'message': fields.String(description='Mensaje de respuesta'),
    'user_id': fields.String(description='ID del usuario'),
    'user_name': fields.String(description='Nombre del usuario')
})

counts_model = api_ns.model('PlaceCounts', {
    'all': fields.Integer,
    'Desayunos y Comidas': fields.Integer,
    'Bebidas y Cafetería': fields.Integer,
    'Snacks': fields.Integer
})

# -------------------
# RUTA DE IMÁGENES 
# -------------------
# función "get_uploaded_file"

@api.route("/uploads/<filename>")
class UploadResource(Resource):
    def get(self, filename):
        """
        Sirve un archivo subido desde el directorio de uploads.
        """
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# -------------------
# AUTH ENDPOINTS
# -------------------

@api_ns.route('/register')
class Register(Resource):
    @api_ns.expect(register_model, validate=False)
    @api_ns.marshal_with(message_model, code=201)
    def post(self):
        """Registra un nuevo usuario en el sistema."""
        session_db = get_session()
        try:
            # Intentamos obtener JSON primero, si falla usamos form
            data = request.json if request.is_json else request.form
            
            name = data.get("name")
            email = data.get("email")
            password = data.get("password")

            if not email or not email.endswith("@alumnos.udg.mx"):
                api_ns.abort(400, "El correo debe ser @alumnos.udg.mx")

            if session_db.query(User).filter(User.email == email).first():
                api_ns.abort(409, "Este correo ya está registrado")

            user = User(name=name, email=email)
            user.password_hash = generate_password_hash(password)

            session_db.add(user)
            session_db.commit()

            return {"message": "Usuario registrado"}, 201
        finally:
            session_db.close()

@api_ns.route('/login')
class Login(Resource):
    @api_ns.expect(login_model, validate=False)
    def post(self):
        """Inicia sesión para un usuario existente."""
        session_db = get_session()
        try:
            data = request.json if request.is_json else request.form
            email = data.get("email")
            password = data.get("password")

            user = session_db.query(User).filter(User.email == email).first()

            if not user or not check_password_hash(user.password_hash, password):
                api_ns.abort(401, "Credenciales inválidas")

            return {
                "message": "Logged in",
                "user_id": user.id,
                "user_name": user.name
            }, 200
        finally:
            session_db.close()

@api_ns.route('/logout')
class Logout(Resource):
    @api_ns.marshal_with(message_model)
    def post(self):
        """Finaliza la sesión del usuario."""
        return {"message": "Logged out"}, 200

# -------------------
# PLACES ENDPOINTS
# -------------------

@api_ns.route('/places')
class Places(Resource):
    @api_ns.marshal_list_with(place_model)
    def get(self):
        """Obtiene una lista de lugares registrados."""
        session_db = get_session()
        try:
            category = request.args.get("category")
            query = session_db.query(Place)
            if category and category.lower() != "all":
                query = query.filter(Place.category == category)
            
            places = query.all()
            
            # Mapeo manual para asegurar que coincida con el modelo
            result = []
            for p in places:
                result.append({
                    "id": p.id,
                    "name": p.name,
                    "schedule": p.schedule,
                    "category": p.category,
                    "image_url": p.image_url,
                    "menu": p.menu_items, # SQLAlchemy relationship
                    "rating": p.rating,
                    "num_ratings": p.num_ratings,
                    "latest_comment": p.comments[-1].text if p.comments else ""
                })
            return result
        finally:
            session_db.close()

    @api_ns.expect(place_model, validate=False)
    @api_ns.marshal_with(id_model, code=201)
    def post(self):
        """Crea un nuevo lugar en el sistema."""
        session_db = get_session()
        try:
            # Nota: Al usar FormData con archivos, request.form es necesario
            name = request.form.get("name")
            category = request.form.get("category")
            
            schedule_raw = request.form.get("schedule", "{}")
            try:
                schedule = json.loads(schedule_raw)
            except:
                schedule = {}

            image_file = request.files.get("image")
            image_url = ""
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                image_url = f"/uploads/{filename}"

            new_place = Place(
                name=name,
                schedule=schedule,
                category=category,
                image_url=image_url
            )

            session_db.add(new_place)
            session_db.commit()

            # Menu items
            menu_json = request.form.get("menu", "[]")
            try:
                menu_items = json.loads(menu_json)
            except:
                menu_items = []

            for m in menu_items:
                menu_item = MenuItem(
                    place_id=new_place.id,
                    category=m.get("category"),
                    dish_name=m.get("dish_name"),
                    price=m.get("price")
                )
                session_db.add(menu_item)

            session_db.commit()
            return {"id": new_place.id}, 201
        finally:
            session_db.close()

@api_ns.route('/places/<string:place_id>')
class PlaceResource(Resource):
    @api_ns.marshal_with(place_model)
    def get(self, place_id):
        """Obtiene información detallada de un lugar."""
        session_db = get_session()
        try:
            p = session_db.get(Place, place_id)
            if not p:
                api_ns.abort(404, "Place not found")
            return {
                "id": p.id,
                "name": p.name,
                "schedule": p.schedule,
                "category": p.category,
                "image_url": p.image_url,
                "menu": p.menu_items,
                "rating": p.rating,
                "num_ratings": p.num_ratings
            }
        finally:
            session_db.close()

    @api_ns.expect(place_model, validate=False)
    @api_ns.marshal_with(message_model)
    def put(self, place_id):
        """Actualiza un lugar."""
        session_db = get_session()
        try:
            p = session_db.get(Place, place_id)
            if not p:
                api_ns.abort(404, "Place not found")

            data = request.json
            p.name = data.get("name", p.name)
            p.category = data.get("category", p.category)
            p.image_url = data.get("image_url", p.image_url)

            if "schedule" in data:
                s = data["schedule"]
                if isinstance(s, str):
                    try:
                        s = json.loads(s)
                    except:
                        s = {}
                p.schedule = s

            # Actualizar menu
            session_db.query(MenuItem).filter(MenuItem.place_id == p.id).delete(synchronize_session=False)
            for m in data.get("menu", []):
                menu_item = MenuItem(
                    place_id=p.id,
                    category=m.get("category"),
                    dish_name=m.get("dish_name"),
                    price=m.get("price")
                )
                session_db.add(menu_item)

            session_db.commit()
            return {"message": "Updated"}
        finally:
            session_db.close()

    @api_ns.marshal_with(message_model)
    def delete(self, place_id):
        """Elimina un lugar."""
        session_db = get_session()
        try:
            p = session_db.get(Place, place_id)
            if not p:
                api_ns.abort(404, "Place not found")
            session_db.delete(p)
            session_db.commit()
            return {"message": "Deleted"}
        finally:
            session_db.close()

@api_ns.route('/places/counts')
class PlaceCounts(Resource):
    @api_ns.marshal_with(counts_model)
    def get(self):
        """Obtiene el conteo de lugares."""
        session_db = get_session()
        try:
            counts = {
                "all": session_db.query(Place).count(),
                "Desayunos y Comidas": session_db.query(Place).filter(Place.category == "Desayunos y Comidas").count(),
                "Bebidas y Cafetería": session_db.query(Place).filter(Place.category == "Bebidas y Cafetería").count(),
                "Snacks": session_db.query(Place).filter(Place.category == "Snacks").count()
            }
            return counts
        finally:
            session_db.close()

# -------------------
# COMMENTS
# -------------------

@api_ns.route('/places/<string:place_id>/comments')
class Comments(Resource):
    @api_ns.marshal_list_with(comment_model)
    def get(self, place_id):
        """Obtiene los comentarios de un lugar."""
        session_db = get_session()
        try:
            place = session_db.get(Place, place_id)
            if not place:
                api_ns.abort(404, "Place not found")
            
            # Convertir objetos SQLAlchemy a diccionarios si es necesario
            # Pero marshal_list_with suele manejar objetos bien si los campos coinciden
            return [
                {
                    "id": c.id,
                    "place_id": c.place_id,
                    "user_id": c.user_id,
                    "user_name": c.user.name,
                    "text": c.text,
                    "rating": c.rating
                } for c in place.comments
            ]
        finally:
            session_db.close()

    @api_ns.expect(comment_model, validate=False)
    @api_ns.marshal_with(id_model, code=201)
    def post(self, place_id):
        """Agrega un comentario."""
        session_db = get_session()
        try:
            place = session_db.get(Place, place_id)
            if not place:
                api_ns.abort(404, "Local no encontrado")

            # Soporte para form-data (frontend actual) o JSON
            data = request.json if request.is_json else request.form

            new_comment = Comment(
                place_id=place_id,
                user_id=data.get("user_id"),
                text=data.get("text"),
                rating=int(data.get("rating", 0))
            )

            session_db.add(new_comment)
            session_db.commit()

            update_place_rating(session_db, place)
            session_db.commit()

            return {"id": new_comment.id}, 201
        finally:
            session_db.close()

@api_ns.route('/comments/<string:comment_id>')
class CommentResource(Resource):
    @api_ns.expect(comment_model, validate=False)
    @api_ns.marshal_with(message_model)
    def put(self, comment_id):
        """Actualiza un comentario."""
        session_db = get_session()
        try:
            c = session_db.get(Comment, comment_id)
            if not c:
                api_ns.abort(404, "Comentario no encontrado")

            data = request.json
            c.text = data.get("text", c.text)
            c.rating = data.get("rating", c.rating)

            session_db.commit()
            update_place_rating(session_db, c.place)
            session_db.commit()

            return {"message": "Comentario editado correctamente"}
        finally:
            session_db.close()

    @api_ns.marshal_with(message_model)
    def delete(self, comment_id):
        """Elimina un comentario."""
        session_db = get_session()
        try:
            c = session_db.get(Comment, comment_id)
            if not c:
                api_ns.abort(404, "Comment not found")
            
            place = c.place
            session_db.delete(c)
            session_db.commit()

            update_place_rating(session_db, place)
            session_db.commit()

            return {"message": "Comentario eliminado correctamente"}
        finally:
            session_db.close()

# -------------------
# RUN SERVER
# -------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)