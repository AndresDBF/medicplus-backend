from sqlalchemy import Column, Table, String, Integer, CHAR, TIMESTAMP
from sqlalchemy.sql.functions import func
from database.connection import engine, meta_data

# Tabla para almacenar el estado del usuario
user_state_especiality = Table("user_state_especiality", meta_data,
              Column("numero", String(30), primary_key=True),
              Column("state", String(191), nullable=False),
              Column("nom_esp", String(191), nullable=True),
              Column("num_esp", String(3), nullable=True),
              Column("precio", Integer, nullable=True),
              Column("nombre_medico", String(191), nullable=True),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine, checkfirst=True)
