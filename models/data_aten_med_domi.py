from sqlalchemy import Column, Table, String, Integer, CHAR, TIMESTAMP, Boolean
from sqlalchemy.sql.functions import func
from database.connection import engine, meta_data

# Tabla para almacenar el estado del usuario
data_aten_med_domi = Table("data_aten_med_domi", meta_data,
              Column("id", Integer, primary_key=True),
              Column("hor_diu", Boolean, nullable=False),
              Column("des_dom", String(191), nullable=False),
              Column("pre_amd", Integer, nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine, checkfirst=True)

