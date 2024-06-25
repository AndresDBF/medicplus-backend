import re
from database.connection import engine
from models.roles import roles
from models.usuarios import usuarios
from models.user_roles import user_roles
from models.user_state_register import user_state_register
from models.user_state_attention import user_state_attention
from models.user_state_especiality import user_state_especiality

from sqlalchemy import select, insert, update

#para tomar el status del registro
def get_user_state(numero):
    with engine.connect() as conn:
        
        result = conn.execute(select(user_state_register).where(user_state_register.c.numero == numero)).fetchone()
        
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "plan", "nombre", "apellido", "cedula", "email", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
            return result_dict
        else:
            return {"consult": None}

#para tomar el status de la solicitud de identidad
def get_user_state_identification(numero):
    with engine.connect() as conn:
        
        result = conn.execute(select(user_state_attention).where(user_state_attention.c.numero == numero)).fetchone()
        
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "cedula", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
        
            return result_dict
        else:
            return {"consult": None}

#para tomar el status de las consultas medicas 
def get_user_state_especiality(numero):
    with engine.connect() as conn:
        result = conn.execute(select(user_state_especiality).where(user_state_especiality.c.numero == numero)).fetchone()
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "nom_esp", "especiality", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
        
            return result_dict
        else:
            return {"consult": None}



#---------------------------------------------------------------------------
        
#funciones para maneras status del usuario durante la conversacion con el bot 
#para el registro
def get_user_state_register(numero, state, plan=None, nombre=None, apellido=None, cedula=None, email=None):
    with engine.connect() as conn:
        
        result = get_user_state(numero)
        if result["consult"] is not None:
            
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
                if not re.fullmatch(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', nombre):
                    return False
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, nombre=nombre)
                )
                conn.commit()
                
            if apellido:
                if not re.fullmatch(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', apellido):
                    return False
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
           
            return True
        else:
            
            conn.execute(user_state_register.insert().values(numero=numero, state=state))
            conn.commit()
            
            return True

#para la solicitud de identidad 
def get_user_state_identification_register(numero, state, cedula=None):
    with engine.connect() as conn:
       
        result = get_user_state_identification(numero)
        if result["consult"] is not None:
           
            if cedula:
           
                if not re.fullmatch(r'\d{7,}', cedula):
                    print("entra en cedula incorrecta")
                    return False
           
                conn.execute(
                    update(user_state_attention)
                    .where(user_state_attention.c.numero == numero)
                    .values(numero=numero, state=state, cedula=cedula)
                )
                conn.commit()
           
                return True
            else:
           
                conn.execute(
                    update(user_state_attention)
                    .where(user_state_attention.c.numero == numero)
                    .values(numero=numero, state=state)
                )
                conn.commit()
           
                return True
                
        else:
           
            conn.execute(user_state_attention.insert().values(numero=numero, state=state))
            conn.commit()
            return True

#para la solicitud de especialidades
def update_user_state_especiality(numero, state, especialidad=None, nombre_medico=None):
    with engine.connect() as conn:
        print("entra en update_user_state_especiality")
        print("el numero: ", numero)
        print("el status: ", state)
        result = get_user_state_especiality(numero)
        
        if result["consult"] is not None:
            print("entra en el if esto trae el result: ", result)
            if especialidad:
                if especialidad not in ["1", "2", "3", "4", "5", "6"]:
                    return False
                if especialidad == "1":
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Medicina General')
                    )
                    conn.commit()
                if especialidad == "2":
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Pediatría')
                    )
                    conn.commit()
                if especialidad == "3":
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Traumatología')
                    )
                    conn.commit()
                if especialidad == "4":
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Neumonología')
                    )
                    conn.commit()
                if especialidad == "5":
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Neurología')
                    )
                    conn.commit()
                if especialidad == "6":
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Cardiología')
                    )
                    conn.commit()

                
                return True                
            if nombre_medico:
                if not re.fullmatch(r'^\d+$', nombre_medico):
                    return False
                conn.execute(user_state_especiality.update().where(user_state_especiality.c.numero == numero)
                             .values(numero=numero, state=state, especiality=nombre_medico))
                conn.commit()
        else:   
            print("entra en el else ")        
            conn.execute(user_state_especiality.insert().values(numero=numero, state=state))
            conn.commit()
            return True
    
def verify_user(numero):
    with engine.connect() as conn:
        
        user = conn.execute(usuarios.select().where(usuarios.c.tel_usu==numero)).first()
        
    if user is not None:
        
        texto = f"Hola {user.nom_usu} {user.ape_usu}👋🏼 ¿En que puedo ayudarte hoy?📝."
        return {
            "text": texto,
            "registered": True
        }
    else:
        
        texto = f"Lo siento, no te he encontrado en sistema como usuario afiliado🚫, deseas formar parte de Afiliados en Medic Plus?👨🏼‍⚕️ Registraremos tus datos paso a paso📝"
        return {
            "text": texto,
            "registered": False
        }
 
