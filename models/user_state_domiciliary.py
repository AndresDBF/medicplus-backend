from sqlalchemy import Column, Table, String, Integer, CHAR, TIMESTAMP, Boolean
from sqlalchemy.sql.functions import func
from database.connection import engine, meta_data

# Tabla para almacenar el estado del usuario
user_state_domiciliary = Table("user_state_domiciliary", meta_data,
              Column("numero", String(30), primary_key=True),
              Column("state", String(80), nullable=False),
              Column("location", String(80), nullable=True),
              Column("confirm", Boolean, nullable=False, default=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine, checkfirst=True)
