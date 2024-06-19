from sqlalchemy import create_engine, MetaData
# Configuración de la base de datos SQLITE
engine = create_engine('sqlite:///./metapython.db')
meta_data = MetaData()