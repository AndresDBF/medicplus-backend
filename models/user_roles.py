from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer
from database.connection import engine, meta_data


user_roles = Table("user_roles", meta_data,
              Column("fk_use_id", Integer, ForeignKey("usuarios.id") ,nullable=False),
              Column("fk_rol_id", Integer, ForeignKey("roles.id"), nullable=False)
)

meta_data.create_all(engine, checkfirst=True)
