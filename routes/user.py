import re
from database.connection import engine
from models.roles import roles
from models.usuarios import usuarios
from models.user_roles import user_roles
from models.user_state_register import user_state_register
from models.user_state_attention import user_state_attention

from sqlalchemy import select, insert, update

def get_user_state(numero):
    with engine.connect() as conn:
        print("entra en get_user_state")
        result = conn.execute(select(user_state_register).where(user_state_register.c.numero == numero)).fetchone()
        print("esto trae el result: ", result)
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "plan", "nombre", "apellido", "cedula", "email", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
            return result_dict
        else:
            return {"consult": None}

def get_user_state_identification(numero):
    with engine.connect() as conn:
        print("entra en get_user_state_identification")
        result = conn.execute(select(user_state_attention).where(user_state_attention.c.numero == numero)).fetchone()
        print("este es el result: ", result)
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "cedula", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
            print("este es el result_dict: ", result_dict)
            return result_dict
        else:
            return {"consult": None}
        
#funciones para maneras status del usuario durante la conversacion con el bot 
#para el registro
def get_user_state_register(numero, state, plan=None, nombre=None, apellido=None, cedula=None, email=None):
    with engine.connect() as conn:
        print("entra en get_user_state_register")
        result = get_user_state(numero)
        if result["consult"] is not None:
            print("entra en el if para actualizar")
            if plan:
                if plan not in ["1","2","3","4","5"]:
                    return False
                
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, plan=plan)
                )
                conn.commit()
                
            if nombre:
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, nombre=nombre)
                )
                conn.commit()
                
            if apellido:
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, apellido=apellido)
                )
                conn.commit()
                
            if cedula:
                if not re.fullmatch(r'\d{7,}', cedula):
                    return False
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, cedula=cedula)
                )
                conn.commit()
                
            if email:
                if not re.fullmatch(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', email):
                    return False
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, email=email)
                )
                conn.commit()
                
            else:
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state)
                )
                conn.commit()
            print("actualizo los campos")
            return True
        else:
            print("entra en el else para insertar")
            conn.execute(user_state_register.insert().values(numero=numero, state=state))
            conn.commit()
            print("se inserto la fila")
            return True

#para la solicitud de identidad 
def get_user_state_identification_register(numero, state, cedula=None):
    with engine.connect() as conn:
        print("entra en get_user_state_identification_register")
        result = get_user_state_identification(numero)
        if result["consult"] is not None:
            print("entra en el if")
            if cedula:
                print("entra en el if de que existe cedula")
                if not re.fullmatch(r'\d{7,}', cedula):
                    return False
                conn.execute(
                    update(user_state_attention)
                    .where(user_state_attention.c.numero == numero)
                    .values(numero=numero, state=state, cedula=cedula)
                )
                conn.commit()
                return True
            else:
                print("entra en el else de que no existe cedula ")
                conn.execute(
                    update(user_state_attention)
                    .where(user_state_attention.c.numero == numero)
                    .values(numero=numero, state=state)
                )
                conn.commit()
                print("inserta los datos ")
                return True
                
        else:
            print("entra en el else para insertar")
            conn.execute(user_state_attention.insert().values(numero=numero, state=state))
            conn.commit()
            return True
            
def verify_user(numero):
    with engine.connect() as conn:
        print("entra en verify_user")
        user = conn.execute(usuarios.select().where(usuarios.c.tel_usu==numero)).first()
        print("esto trae el user: ", user)
    if user is not None:
        print("entra en el if del verify_user")
        texto = f"Hola {user.nom_usu} {user.ape_usu}👋🏼 ¿En que puedo ayudarte hoy?📝."
        return {
            "text": texto,
            "registered": True
        }
    else:
        print("entra en el else del verify_user")
        texto = f"Lo siento, no te he encontrado en sistema como usuario afiliado🚫, deseas formar parte de Afiliados en Medic Plus?👨🏼‍⚕️ Registraremos tus datos paso a paso📝"
        return {
            "text": texto,
            "registered": False
        }
 
