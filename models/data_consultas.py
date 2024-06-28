from sqlalchemy import Column, Table, String, Integer, CHAR, TIMESTAMP
from sqlalchemy.sql.functions import func
from database.connection import engine, meta_data

# Tabla para almacenar el estado del usuario
data_consultas = Table("data_consultas", meta_data,
              Column("id", Integer, primary_key=True),
              Column("tip_con", String(191), nullable=False),
              Column("pre_con", Integer, nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine, checkfirst=True)
