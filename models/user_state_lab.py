from sqlalchemy import Column, Table, String, Integer, CHAR, TIMESTAMP, Boolean
from sqlalchemy.sql.functions import func
from database.connection import engine, meta_data

# Tabla para almacenar el estado del usuario
user_state_laboratory = Table("user_state_laboratory", meta_data,
              Column("numero", String(30), primary_key=True),
              Column("state", String(20), nullable=False),
              Column("test", String(1), nullable=True),
              Column("eco", Boolean, nullable=False, default=False),
              Column("rx", Boolean, nullable=False, default=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine, checkfirst=True)
