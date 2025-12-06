# models.py
import uuid

class Place:
    def __init__(self, name, category, image_url, menu=[]):
        """
        Inicializa un objeto Place con sus atributos.

        Args:
            name (str): Nombre del lugar.
            category (str): Categoría del lugar.
            image_url (str): URL de la imagen del lugar.
            menu (list, opcional): Menú del lugar. Por defecto es una lista vacía.
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.category = category
        self.image_url = image_url
        self.menu = menu  # list of {"category": ..., "dish_name": ..., "price": ...}
        self.rating = 0.0       # average rating
        self.num_ratings = 0    # number of ratings

class Comment:
    def __init__(self, place_id, user_name, user_image, text, rating=0):
        """
        Inicializa un objeto Comment con sus atributos.

        Args:
            place_id (str): ID del lugar asociado al comentario.
            user_name (str): Nombre del usuario que hizo el comentario.
            user_image (str): URL de la imagen del usuario.
            text (str): Texto del comentario.
            rating (int, opcional): Calificación del lugar. Por defecto es 0.
        """
        self.id = str(uuid.uuid4())
        self.place_id = place_id
        self.user_name = user_name
        self.user_image = user_image
        self.text = text
        self.rating = rating
