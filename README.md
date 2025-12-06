# cucei-foods-backend
CUCEI Foods app repository for backend development

## Descripción

Cucei Foods Backend es una aplicación diseñada para gestionar y proporcionar servicios backend para la gestión de alimentos. Este proyecto incluye funcionalidades como la gestión de bases de datos, modelos de datos y utilidades relacionadas con la aplicación.

## Estructura del Proyecto

La estructura principal del proyecto es la siguiente:

```
main.py
README.md
requirements.txt
app/
	__init__.py
	models.py
	utils.py
	db/
		__init__.py
		models.py
uploads/
```

- **main.py**: Archivo principal para ejecutar la aplicación.
- **requirements.txt**: Archivo que contiene las dependencias necesarias para el proyecto.
- **app/**: Contiene los módulos principales de la aplicación.
  - **models.py**: Define los modelos de datos.
  - **utils.py**: Contiene funciones auxiliares.
  - **db/**: Módulo relacionado con la base de datos.
- **uploads/**: Carpeta destinada para almacenar archivos subidos.

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

## Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/andyglez3245/cucei-foods-backend.git
   ```

2. Navega al directorio del proyecto:

   ```bash
   cd cucei-foods-backend
   ```

3. Crea un entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Ejecuta la aplicación:

   ```bash
   python main.py
   ```

2. La aplicación estará lista para recibir solicitudes y procesar datos.

## Contribución

Si deseas contribuir a este proyecto, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama para tus cambios:

   ```bash
   git checkout -b nombre-de-tu-rama
   ```

3. Realiza tus cambios y haz commit:

   ```bash
   git commit -m "Descripción de tus cambios"
   ```

4. Sube tus cambios a tu repositorio:

   ```bash
   git push origin nombre-de-tu-rama
   ```

5. Crea un Pull Request en el repositorio original.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

## Contacto

Para cualquier duda o consulta, puedes contactar al propietario del repositorio en [andyglez3245](https://github.com/andyglez3245).

## Tecnologías Utilizadas

Este backend utiliza las siguientes tecnologías:

- **Python**: Lenguaje de programación principal.
- **Flask**: Framework web ligero para construir APIs.
- **SQLAlchemy**: ORM (Object-Relational Mapping) para la gestión de bases de datos.
- **Werkzeug**: Biblioteca utilizada para la gestión de contraseñas y utilidades WSGI.
- **SQLite**: Base de datos utilizada para el almacenamiento de datos durante el desarrollo.