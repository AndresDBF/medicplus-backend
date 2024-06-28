from sqlalchemy import Column, Table, String, Integer, CHAR, TIMESTAMP
from sqlalchemy.sql.functions import func
from database.connection import engine, meta_data

# Tabla para almacenar el estado del usuario
user_state_register = Table("user_state_register", meta_data,
              Column("numero", String(30), primary_key=True),
              Column("state", String(191), nullable=False),
              Column("plan", String(1), nullable=True),
              Column("nombre", String(80), nullable=True),
              Column("apellido", String(80), nullable=True),
              Column("cedula", String(20), nullable=True),
              Column("email", String(80), nullable=True),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine, checkfirst=True)
