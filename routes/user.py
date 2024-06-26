import re
from database.connection import engine
from models.roles import roles
from models.usuarios import usuarios
from models.user_roles import user_roles
from models.user_state_register import user_state_register
from models.user_state_attention import user_state_attention
from models.user_state_especiality import user_state_especiality
from models.user_state_lab import user_state_laboratory
from models.user_state_ambulance import user_state_ambulance

from sqlalchemy import select, insert, update

#para tomar el status del registro
def get_user_state(numero):
    print("---------------------entra en get_user_state---------------------")
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
    print("---------------------entra en get_user_state_identification---------------------")
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
    print("---------------------entra en get_user_state_especiality---------------------")
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

#para la solicitud de una prueba de laboratorio
def get_user_state_lab(numero):
    print("---------------------entra en get_user_state_lab---------------------")
    with engine.connect() as conn:
        result = conn.execute(select(user_state_laboratory).where(user_state_laboratory.c.numero == numero)).fetchone()
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "test", "eco", "rx", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
        
            return result_dict
        else:
            return {"consult": None}

#para la solicitud de una ambulancia 
def get_user_state_ambulance(numero):
    print("---------------------entra en get_user_state_lab---------------------")
    with engine.connect() as conn:
        result = conn.execute(select(user_state_ambulance).where(user_state_ambulance.c.numero == numero)).fetchone()
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "location", "confirm", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
        
            return result_dict
        else:
            return {"consult": None}
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
        
#funciones para maneras status del usuario durante la conversacion con el bot 
#para el registro
def get_user_state_register(numero, state, plan=None, nombre=None, apellido=None, cedula=None, email=None):
    print("---------------------entra en get_user_state_register---------------------")
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
    print("---------------------entra en get_user_state_identification_register---------------------")
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
        print("---------------------entra en update_user_state_especiality---------------------")
        print("el numero: ", numero)
        print("el status: ", state)
        print("la especialidad: ", especialidad)
        print("el nombre_medico: ", nombre_medico)
        result = get_user_state_especiality(numero)
        
        if result["consult"] is not None:
          
            if especialidad:
                print("entra en el if de especialidad")
                if especialidad not in ["1", "2", "3", "4", "5", "6"]:
                    return False
                elif especialidad == "1":
                    print("entra en 1")
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Medicina General')
                    )
                    conn.commit()
                elif especialidad == "2":
                    print("entra en 2")
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Pediatría')
                    )
                    conn.commit()
                elif especialidad == "3":
                    print("entra en 3")
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Traumatología')
                    )
                    conn.commit()
                elif especialidad == "4":
                    print("entra en 4")
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Neumonología')
                    )
                    conn.commit()
                elif especialidad == "5":
                    print("entra en 5")
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Neurología')
                    )
                    conn.commit()
                elif especialidad == "6":
                    print("entra en 6")
                    conn.execute(
                        update(user_state_especiality)
                        .where(user_state_especiality.c.numero == numero)
                        .values(numero=numero, state=state, nom_esp='Cardiología')
                    )
                    conn.commit()
                

                
                return True                
            elif nombre_medico:
                print("entra en nombre medico")
                if not re.fullmatch(r'^\d+$', nombre_medico):
                    print("entra en el if del regex")
                    return False
                print("pasa el if del regex")
                conn.execute(user_state_especiality.update().where(user_state_especiality.c.numero == numero)
                             .values(numero=numero, state=state, especiality=nombre_medico))
                conn.commit()
                print("actualiza los datos")
                return True
            else:
                print("entra en el else donde no consigue parametros")
                conn.execute(
                    update(user_state_especiality)
                    .where(user_state_especiality.c.numero == numero)
                    .values(numero=numero, state=state)
                )
                conn.commit()
                return True
        else:   
            print("entra en el else ")        
            conn.execute(user_state_especiality.insert().values(numero=numero, state=state))
            conn.commit()
            return True
    
#para la solicitud de una prueba de laboratorio
def update_user_state_lab(numero, state, test=None, rx_or_eco=None):
    with engine.connect() as conn:
        print("---------------------entra en update_user_state_lab---------------------")
        print("el numero: ", numero)
        print("el status: ", state)
        print("la prueba: ", test)
        
        result = get_user_state_lab(numero)
        
        if result["consult"] is not None:
            if test:
                print("entra en el if de test")
                if test not in ["1", "2", "3", "4", "5", "6"]:
                    return False
                elif test == "1":
                    print("entra en 1")
                    conn.execute(
                        update(user_state_laboratory)
                        .where(user_state_laboratory.c.numero == numero)
                        .values(numero=numero, state=state, test='Prueba de Sangre')
                    )
                    conn.commit()
                elif test == "2":
                    print("entra en 2")
                    conn.execute(
                        update(user_state_laboratory)
                        .where(user_state_laboratory.c.numero == numero)
                        .values(numero=numero, state=state, test='Prueba de Orina')
                    )
                    conn.commit()
                elif test == "3":
                    print("entra en 3")
                    conn.execute(
                        update(user_state_laboratory)
                        .where(user_state_laboratory.c.numero == numero)
                        .values(numero=numero, state=state, test='Prueba de Eces')
                    )
                    conn.commit()
                elif test == "4":
                    print("entra en 4")
                    conn.execute(
                        update(user_state_laboratory)
                        .where(user_state_laboratory.c.numero == numero)
                        .values(numero=numero, state=state, test='Prueba de COVID-19')
                    )
                    conn.commit()
                elif test == "5":
                    print("entra en 5")
                    conn.execute(
                        update(user_state_laboratory)
                        .where(user_state_laboratory.c.numero == numero)
                        .values(numero=numero, state=state, test='Placa de Torax')
                    )
                    conn.commit()
                elif test == "6":
                    print("entra en 6")
                    conn.execute(
                        update(user_state_laboratory)
                        .where(user_state_laboratory.c.numero == numero)
                        .values(numero=numero, state=state, test='Imagenología')
                    )
                    conn.commit()
                return True                
            elif rx_or_eco:
                print("entra en eco o rayos x")
                if rx_or_eco not in ["ideco", "idrayosrx"]:
                    print("entra en el if del regex")
                    return False
                print("pasa el if del regex")
                if rx_or_eco == "ideco":
                    conn.execute(user_state_laboratory.update().where(user_state_laboratory.c.numero == numero)
                                .values(numero=numero, state=state, eco=True, rx=False))
                    conn.commit()
                else:
                    conn.execute(user_state_laboratory.update().where(user_state_laboratory.c.numero == numero)
                                .values(numero=numero, state=state, eco=False, rx=True))
                    conn.commit()
                print("actualiza los datos")
                return True
            else:
                print("entra en el else donde no consigue parametros")
                conn.execute(
                    update(user_state_laboratory)
                    .where(user_state_laboratory.c.numero == numero)
                    .values(numero=numero, state=state)
                )
                conn.commit()
                return True
        else:   
            print("entra en el else ")        
            conn.execute(user_state_laboratory.insert().values(numero=numero, state=state))
            conn.commit()
            return True

def update_user_state_ambulance(numero, state, municipalities=None, confirm=None):
    with engine.connect() as conn:
        print("---------------------entra en update_user_state_lab---------------------")
        print("el numero: ", numero)
        print("el status: ", state)
        print("la prueba: ", municipalities)
        
        result = get_user_state_ambulance(numero)
        
        if result["consult"] is not None:
            if municipalities:
                print("entra en el if de test")
                if municipalities not in ["1", "2", "3", "4", "5", "6", "7"]:
                    return False
                elif municipalities == "1":
                    print("entra en 1")
                    conn.execute(
                        update(user_state_ambulance)
                        .where(user_state_ambulance.c.numero == numero)
                        .values(numero=numero, state=state, location='La Asunción')
                    )
                    conn.commit()
                elif municipalities == "2":
                    print("entra en 2")
                    conn.execute(
                        update(user_state_ambulance)
                        .where(user_state_ambulance.c.numero == numero)
                        .values(numero=numero, state=state, location='Juangriego')
                    )
                    conn.commit()
                elif municipalities == "3":
                    print("entra en 3")
                    conn.execute(
                        update(user_state_ambulance)
                        .where(user_state_ambulance.c.numero == numero)
                        .values(numero=numero, state=state, location='Porlamar')
                    )
                    conn.commit()
                elif municipalities == "4":
                    print("entra en 4")
                    conn.execute(
                        update(user_state_ambulance)
                        .where(user_state_ambulance.c.numero == numero)
                        .values(numero=numero, state=state, location='Pampatar')
                    )
                    conn.commit()
                elif municipalities == "5":
                    print("entra en 5")
                    conn.execute(
                        update(user_state_ambulance)
                        .where(user_state_ambulance.c.numero == numero)
                        .values(numero=numero, state=state, location='Santa Ana')
                    )
                    conn.commit()
                elif municipalities == "6":
                    print("entra en 6")
                    conn.execute(
                        update(user_state_ambulance)
                        .where(user_state_ambulance.c.numero == numero)
                        .values(numero=numero, state=state, location='Punta de Piedra')
                    )
                    conn.commit()
                elif municipalities == "7":
                    print("entra en 7")
                    conn.execute(
                        update(user_state_ambulance)
                        .where(user_state_ambulance.c.numero == numero)
                        .values(numero=numero, state=state, location='Altagracia')
                    )
                    conn.commit()
                return True                
            elif confirm:
                print("entra en confirmacion")
                conn.execute(user_state_ambulance.update().where(user_state_ambulance.c.numero == numero)
                            .values(numero=numero, state=state, confirm=True))
                conn.commit()
                return True
            else:
                print("entra en el else donde no consigue parametros")
                conn.execute(
                    update(user_state_ambulance)
                    .where(user_state_ambulance.c.numero == numero)
                    .values(numero=numero, state=state)
                )
                conn.commit()
                return True
        else:   
            print("entra en el else ")        
            conn.execute(user_state_ambulance.insert().values(numero=numero, state=state))
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
 
