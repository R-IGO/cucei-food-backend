import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    comments = db.relationship("Comment", backref="user", cascade="all, delete-orphan")

    def set_password(self, pw):
        """
        Establece el hash de la contraseña para el usuario.

        Args:
            pw (str): Contraseña en texto plano.
        """
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        """
        Verifica si la contraseña proporcionada coincide con el hash almacenado.

        Args:
            pw (str): Contraseña en texto plano.

        Returns:
            bool: True si la contraseña es correcta, False en caso contrario.
        """
        return check_password_hash(self.password_hash, pw)


class Place(db.Model):
    __tablename__ = 'places'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    schedule = db.Column(JSONB, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(300), default='')
    rating = db.Column(db.Float, default=0.0)
    num_ratings = db.Column(db.Integer, default=0)

    menu_items = db.relationship("MenuItem", backref="place", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="place", cascade="all, delete-orphan")


class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    dish_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=0)
