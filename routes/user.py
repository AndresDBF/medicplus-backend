import re
import pytz
from database.connection import engine
from models.roles import roles
from models.usuarios import usuarios
from models.user_roles import user_roles
from models.user_state_register import user_state_register
from models.user_state_attention import user_state_attention
from models.user_state_domiciliary import user_state_domiciliary
from models.user_state_especiality import user_state_especiality
from models.user_state_lab import user_state_laboratory
from models.user_state_ambulance import user_state_ambulance
from models.user_state_imaging import user_state_imaging

from models.data_consultas import data_consultas
from models.data_imagenologia import data_imagenologia
from models.data_planes import data_planes


from sqlalchemy import select, insert, update, text

from googletrans import Translator

from datetime import time, datetime

#para tomar el status del registro
def get_user_state(numero):
    print("---------------------entra en get_user_state---------------------")
    with engine.connect() as conn:
        
        result = conn.execute(select(user_state_register).where(user_state_register.c.numero == numero)).fetchone()
        
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "language", "plan", "nombre", "apellido", "cedula", "email", "fecha_y_hora"]
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
            columns = ["numero", "state", "nom_esp", "num_esp", "precio", "nombre_medico", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
        
            return result_dict
        else:
            return {"consult": None}

#para tomar el status de imagenologia
def get_user_state_imaging(numero):
    print("---------------------entra en get_user_state_imaging---------------------")
    with engine.connect() as conn:
        result = conn.execute(select(user_state_imaging).where(user_state_imaging.c.numero == numero)).fetchone()
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "opcion", "nombre", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
        
            return result_dict
        else:
            return {"consult": None}

#para tomar el status de la solicitud de atencion domiciliaria
def get_user_state_domiciliary(numero):
    print("---------------------entra en get_user_state_domiciliary---------------------")
    with engine.connect() as conn:
        result = conn.execute(select(user_state_domiciliary).where(user_state_domiciliary.c.numero == numero)).fetchone()
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "location", "precio", "confirm", "fecha_y_hora"]
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
            columns = ["numero", "state", "opcion", "test", "precio", "domicilio","fecha_y_hora"]
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
            columns = ["numero", "state", "location", "precio", "confirm", "fecha_y_hora"]
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
                verify_plan = conn.execute(data_planes.select().where(data_planes.c.id==plan)).first()
                if not verify_plan:
                    return False
                else:
                
                    conn.execute(
                        update(user_state_register)
                        .where(user_state_register.c.numero == numero)
                        .values(state=state, plan=plan)
                    )
                    conn.commit()
                    return True
                
            if nombre:
                if not re.fullmatch(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', nombre) or len(nombre) < 3:
                    return False
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, nombre=nombre)
                )
                conn.commit()
                
            if apellido:
                if not re.fullmatch(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', apellido) or len(apellido) < 3:
                    return False
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, apellido=apellido)
                )
                conn.commit()
                
            if cedula:
                if not re.fullmatch(r'\d{7,}', cedula) or len(cedula) < 7 or len(cedula) > 9:
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

#para la solicitud de atencion medica domiciliaria 
def update_user_state_domiciliary(numero, state, municipalities=None, confirm=None):
    with engine.connect() as conn:
        print("---------------------entra en update_user_state_domiciliary---------------------")
        print("el numero: ", numero)
        print("el status: ", state)
        print("el municipio: ", municipalities)
        
        result = get_user_state_domiciliary(numero)
        print("sale de get_user_state_domiciliary ")
        if result["consult"] is not None:
            if municipalities:
                print("entra en el if de municipalities")
                if municipalities not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                    return False
                
                number = 0
    
               
                list_munic= conn.execute(text("select * from data_aten_med_domi where hor_diu = True;")).fetchall()
                print("esto muestra el list imag ", list_munic)
                # Crear un diccionario de mapeo de números a tipos de municipios exactos
                munic_map = {}
                
                for munic in list_munic:
                    number += 1
                    munic_map[number] = munic.des_dom  # Mapear número a nombre exacto del municipio
                   
                selected_munic = munic_map[int(municipalities)]
                list_munic= conn.execute(text(f"select * from data_aten_med_domi where hor_diu = True and des_dom='{selected_munic}';")).first()
                print("esto trae el list_munic: ", list_munic)
                print("el selected_munic: ", selected_munic)
               
                conn.execute(user_state_domiciliary.update().where(user_state_domiciliary.c.numero==numero)
                             .values(numero=numero, state=state, location=selected_munic, precio=int(list_munic.pre_amd)))
                conn.commit()
                
                return True                
            elif confirm:
                print("entra en confirmacion")
                conn.execute(user_state_domiciliary.update().where(user_state_domiciliary.c.numero == numero)
                            .values(numero=numero, state=state, confirm=True))
                conn.commit()
                return True
            else:
                print("entra en el else donde no consigue parametros")
                conn.execute(
                    update(user_state_domiciliary)
                    .where(user_state_domiciliary.c.numero == numero)
                    .values(numero=numero, state=state)
                )
                conn.commit()
                return True
        else:   
            print("entra en el else ")        
            conn.execute(user_state_domiciliary.insert().values(numero=numero, state=state))
            conn.commit()
            return True

#para la solicitud de especialidades
def update_user_state_especiality(numero, state, language=None, especialidad=None, nombre_medico=None):
    translator = Translator()
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
                verify_esp = conn.execute(data_consultas.select().where(data_consultas.c.id==especialidad)).first()
                print("esto trae el verify_esp: ", verify_esp)
                if not verify_esp:
                    print("entra en el if")
                    return False
                else:
                    if language:
                        name_esp = translator.translate(verify_esp.tip_con, src='es', dest='en').text
                    else:
                        name_esp = verify_esp.tip_con
                    print("entra en el else")
                    conn.execute(user_state_especiality.update().where(user_state_especiality.c.numero == numero)
                             .values(numero=numero, state=state, nom_esp=name_esp, num_esp=especialidad, precio=verify_esp.pre_con))
                    conn.commit() 
                    return True
            elif nombre_medico:
                print("entra en nombre medico")
                if not re.fullmatch(r'^\d+$', nombre_medico):
                    print("entra en el if del regex")
                    return False
                print("pasa el if del regex")
                conn.execute(user_state_especiality.update().where(user_state_especiality.c.numero == numero)
                             .values(numero=numero, state=state, nombre_medico=nombre_medico))
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



















#para la solicitud de imagenologia
def update_user_state_imaging(numero, state, language=None, opcion=None, opcion2=None, test=None,  confirm=None):
    translator = Translator()
    with engine.connect() as conn:
        print("---------------------entra en update_user_state_imaging---------------------")
        print("el numero: ", numero)
        print("el status: ", state)
        print("la prueba: ", test)
        number = 0
        result = get_user_state_imaging(numero)
        list_imag = conn.execute(text("select distinct tip_con from data_imagenologia;")).fetchall()
        print("el list imag: ", list_imag)
        
            
        
        if result["consult"] is not None:
            print("encuentra datos del status")
            if opcion:
                print("entra en opcion esto es lo que trae opcion: ", opcion)
                #opcion trae el nombre del estudio de la lista de mapas, ejemplo: ecografia, rayos x
                conn.execute(user_state_imaging.update().where(user_state_imaging.c.numero==numero)
                             .values(numero=numero, state=state, opcion=opcion))
                conn.commit()
                return True
            if test:
                
                #guardamos el texto que ingresa el usuario para tomarlo en la siguiente fase del flujo, ejemplo: Columna, pierna, brazo
                with engine.connect() as conn:
                    if language:
                        translated_resp = translator.translate(test, src='en', dest='es').text
                    else:
                        translated_resp = test
                    print("entra en test esto es lo que guardara: ", translated_resp)
                    conn.execute(user_state_imaging.update().where(user_state_imaging.c.numero==numero).values(numero=numero, state=state, opcion2=translated_resp))
                    conn.commit()
                    return True
            if opcion2:
                print("esto trae la opcion2: ", opcion2)
                
                #consultamos con las opciones que ha ingresado el usuario
                
                selected_service =  conn.execute(user_state_imaging.select().where(user_state_imaging.c.numero==numero)).first()
                print("el selectec_service: ", selected_service)
                print("el selected_service.opcion2: ", selected_service.opcion2, " y el opcion: ", selected_service.opcion)
                list_study = conn.execute(text(f"select * from data_imagenologia where des_pru like '%{selected_service.opcion2}%' and tip_con='{selected_service.opcion}'")).fetchall()
                print("esto es el list_study: ", list_study)
                # Crear un diccionario de mapeo de números a tipos de servicios exactos
                service_map = {}
                data_list = []
                for imag in list_study:
                    number += 1
                    service_map[number] = imag.des_pru  # Mapear número a nombre exacto del servicio
                    data_list.append(f"\n{number}. {imag.des_pru.title()}")
                print("esto es el service map: ", service_map)
                selected_service_map = ""
                if int(opcion2) not in service_map:
                    print("entra en el if")
                    return False
                else:
                    print("entra en el else, esto va a colocar en nombre: ", selected_service_map)
                    selected_service_map = service_map[int(opcion2)]
                    print("esto trae el selected_service: ", selected_service_map)
                    conn.execute(user_state_imaging.update().where(user_state_imaging.c.numero==numero)
                                 .values(numero=numero, state=state, nombre=selected_service_map))
                    conn.commit()
                    return True
                
            else:
                print("entra en el else de que no consiguio parametros")
                conn.execute(user_state_imaging.update().where(user_state_imaging.c.numero==numero)
                            .values(numero=numero, state=state))
                conn.commit()
                return True
        else:   
            print("entra en el else ")        
            conn.execute(user_state_imaging.insert().values(numero=numero, state=state))
            conn.commit()
            return True























#para la solicitud de una prueba de laboratorio
def update_user_state_lab(numero, state, language=None, test=None, opcion=None, confirm_domi=None):
    translator = Translator()
    with engine.connect() as conn:
        print("---------------------entra en update_user_state_lab---------------------")
        print("el numero: ", numero)
        print("el status: ", state)
        print("la prueba: ", test)
        
        result = get_user_state_lab(numero)        
        if result["consult"] is not None:
            if test:
                print("entra en test")
                conn.execute(user_state_laboratory.update().where(user_state_laboratory.c.numero==numero)
                            .values(numero=numero, state=state, test=test))
                conn.commit()
                return True
            if opcion:
                print("entra en opcion: ", opcion)
                number = 0
                if language:
                    
                    find_test = conn.execute(select(user_state_laboratory.c.test).select_from(user_state_laboratory)
                                            .where(user_state_laboratory.c.numero==numero).order_by(user_state_laboratory.c.created_at.asc())).scalar()
                    translated_resp = translator.translate(find_test, src='en', dest='es').text
                    print("esto trae el find test: ", find_test)
                else:
                    
                    find_test = conn.execute(select(user_state_laboratory.c.test).select_from(user_state_laboratory)
                                            .where(user_state_laboratory.c.numero==numero).order_by(user_state_laboratory.c.created_at.asc())).scalar()
                    translated_resp = find_test
                    print("esto trae el find test: ", find_test)
                    
                
                list_tests = conn.execute(text(f"select * from data_laboratorios where tip_pru like '%{translated_resp}%'")).fetchall()
                
                service_map = {}
                data_list = []
                for info_test in list_tests:
                    number += 1
                    service_map[number] = info_test.tip_pru  # Mapear número a nombre exacto del servicio
                    data_list.append(f"\n{number}. {info_test.tip_pru.title()}")
                print("este es el data_list: ", data_list)
                if int(opcion) not in service_map.keys():
                    return False
                selected_service = service_map[int(opcion)]
                
                verify_test = conn.execute(text(f"select * from data_laboratorios where tip_pru like '%{selected_service}%'")).first()
                if language:
                    trans_opcion = translator.translate(verify_test.tip_pru, src='es', dest='en').text
                else:
                    trans_opcion = verify_test.tip_pru
                conn.execute(user_state_laboratory.update().where(user_state_laboratory.c.numero==numero)
                            .values(numero=numero, state=state, opcion=trans_opcion, precio=verify_test.pre_pru))
                conn.commit()
                return True
            if confirm_domi:
                print("entra en el elif de confirmar y actualizar el domicilio")
                conn.execute(user_state_laboratory.update().where(user_state_laboratory.c.numero==numero)
                             .values(numero=numero, state=state, domicilio=True))
                conn.commit()
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

#para la solicitud de una ambulancia 
def update_user_state_ambulance(numero, state, municipalities=None, confirm=None):
    with engine.connect() as conn:
        print("---------------------entra en update_user_state_lab---------------------")
        print("el numero: ", numero)
        print("el status: ", state)
        print("la prueba: ", municipalities)
        
        result = get_user_state_ambulance(numero)
        
        if result["consult"] is not None:
            if municipalities:
                print("entra en el if de municipalities")
                if municipalities not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                    return False
                
                number = 0
    
                venezuela_tz = pytz.timezone('America/Caracas')
    
                # Obtener la hora actual en la zona horaria de Venezuela
                now = datetime.now(venezuela_tz)
                
                
                morning_limit = time(6, 0)  # 6:00 AM
                evening_limit = time(19, 0)  # 7:00 PM
                print("el now ", now)
                print("el morning_limit: ", morning_limit)
                print("el evening_limit: ", evening_limit)
            
                if now.time() <= evening_limit or now.time() >= morning_limit: 
                    list_munic= conn.execute(text("select * from data_aten_med_domi where hor_diu = True;")).fetchall()
                    print("esto muestra el list imag ", list_munic)
                    # Crear un diccionario de mapeo de números a tipos de municipios exactos
                    munic_map = {}
                    
                    for munic in list_munic:
                        number += 1
                        munic_map[number] = munic.des_dom  # Mapear número a nombre exacto del municipio
                    
                    selected_munic = munic_map[int(municipalities)]
                    list_munic= conn.execute(text(f"select * from data_aten_med_domi where hor_diu = True and des_dom='{selected_munic}';")).first()
                    print("esto trae el list_munic: ", list_munic)
                    print("el selected_munic: ", selected_munic)
                
                    conn.execute(user_state_ambulance.update().where(user_state_ambulance.c.numero==numero)
                                .values(numero=numero, state=state, location=selected_munic, precio=int(list_munic.pre_amd)))
                    conn.commit()
                    
                    return True   
                else:
                    list_munic= conn.execute(text("select * from data_aten_med_domi where hor_diu = False;")).fetchall()
                    print("esto muestra el list imag ", list_munic)
                    # Crear un diccionario de mapeo de números a tipos de municipios exactos
                    munic_map = {}
                    
                    for munic in list_munic:
                        number += 1
                        munic_map[number] = munic.des_dom  # Mapear número a nombre exacto del municipio
                    
                    selected_munic = munic_map[int(municipalities)]
                    list_munic= conn.execute(text(f"select * from data_aten_med_domi where hor_diu = True and des_dom='{selected_munic}';")).first()
                    print("esto trae el list_munic: ", list_munic)
                    print("el selected_munic: ", selected_munic)
                
                    conn.execute(user_state_ambulance.update().where(user_state_ambulance.c.numero==numero)
                                .values(numero=numero, state=state, location=selected_munic, precio=int(list_munic.pre_amd)))
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
 
