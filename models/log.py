
from sqlalchemy import Column, Table, TIMESTAMP, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, DateTime, TEXT
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import func
from database.connection import engine, meta_data
from datetime import datetime

log = Table("log", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fecha_y_hora", DateTime, default=datetime.utcnow()),
              Column("texto", TEXT)
)

meta_data.create_all(engine, checkfirst=True)

