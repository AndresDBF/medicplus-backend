from sqlalchemy import create_engine, MetaData
# Configuración de la base de datos SQLITE

DB_USER = '735dev'  # Usuario de la base de datos
DB_PASSWORD = '735dev'  # Contraseña de la base de datos 
DB_HOST = 'localhost'  # Dirección del servidor de la base de datos
DB_PORT = '3306'  # Puerto de la base de datos (por defecto para MySQL)
DB_NAME = 'medicplus'  # Nombre de la base de datos

# Crear la cadena de conexión a la base de datos
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear el motor de SQLAlchemy
engine = create_engine(DB_URL)

# Crear el objeto de conexión
conn = engine.connect()

# Crear objeto MetaData
meta_data = MetaData()