import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la configuración de la base de datos desde las variables de entorno
def get_db_config():
    """
    db_config debe ser un diccionario con las claves:
    host, dbname, user, password, port
    """
    
    return {
        'host': os.getenv('DB_HOST'),
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': int(os.getenv('DB_PORT', 5432))  # Asume 5432 como puerto por defecto si no se especifica
    }