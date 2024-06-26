from sqlalchemy import Column, Table, String, Integer, CHAR, TIMESTAMP
from sqlalchemy.sql.functions import func
from database.connection import engine, meta_data

# Tabla para almacenar el estado del usuario
user_state_especiality = Table("user_state_especiality", meta_data,
              Column("numero", String(30), primary_key=True),
              Column("state", String(20), nullable=False),
              Column("nom_esp", String(80), nullable=True),
              Column("especiality", String(80), nullable=True),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine, checkfirst=True)