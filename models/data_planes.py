from sqlalchemy import Column, Table, String, Integer, CHAR, TIMESTAMP, TEXT
from sqlalchemy.sql.functions import func
from database.connection import engine, meta_data

# Tabla para almacenar el estado del usuario
data_planes = Table("data_planes", meta_data,
              Column("id", Integer, primary_key=True),
              Column("tip_pla", String(50), nullable=False),
              Column("des_pla", TEXT, nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine, checkfirst=True)
