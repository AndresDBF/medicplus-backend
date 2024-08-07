import json
import http
import pytz
from database.connection import engine
from models.usuarios import usuarios
from models.data_aten_med_domi import data_aten_med_domi
from models.user_state_domiciliary import user_state_domiciliary
from models.user_state_register import user_state_register
from models.log import log
from routes.user import get_user_state, get_user_state_register, get_user_state_domiciliary, update_user_state_domiciliary
from routes.user import verify_user
from datetime import datetime
from sqlalchemy import insert, select, text
from datetime import datetime, time

def agregar_mensajes_log(texto):
    try:
        texto_str = json.dumps(texto)
       
        with engine.connect() as conn:
            conn.execute(log.insert().values(texto=texto_str, fecha_y_hora=datetime.utcnow()))
            conn.commit()
        
    except Exception as e:
        print(f"Error al guardar el mensaje en el log: {e}")

def enviar_mensajes_whatsapp (data):
    
    data = json.dumps(data)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAOJtyjmw9EBOyJBUw5wn6z8g1uIVktFfdiQUos9qnnRBC78p0xQH6r1UwxuRlYsUqz1mSq3eJI2ZBZAAF37TjWAWUcRuh8EV0xf95oAVlCj29vPqow15SBou9T9ZAIPaA6nP8ZCgYIhKTXeA8tMuVZALiZBnHwo7j9c8fSF2Kvq6PF9QWGpiZBnbnArbTxlwzT"
    }
    
    connection = http.client.HTTPSConnection("graph.facebook.com")
    
    try:
        connection.request("POST", "/v19.0/378961785290654/messages", data, headers)
        response = connection.getresponse()
        response_data = response.read().decode()
        
        if response.status != 200:
            agregar_mensajes_log(f"Error al enviar mensaje: {response.status} {response.reason} {response_data}")
    except Exception as e:
        print(f"Exception: {e}")
        agregar_mensajes_log(f"Exception al enviar mensaje: {e}")
    finally:
        connection.close() 

def verify_language(numero):
    with engine.connect() as conn:
        result = conn.execute(select(user_state_register.c.language).select_from(user_state_register).where(user_state_register.c.numero==numero)).scalar()
        print(f"--------------el lenguaje: {result}---------------")
    return result 

def get_municipality(numero):
    language = verify_language(numero)
    number = 0
    
    with engine.connect() as conn:
        list_munic= conn.execute(text("select * from data_aten_med_domi where hor_diu = True;")).fetchall()
        print("esto muestra el list imag ", list_munic)
    # Crear un diccionario de mapeo de números a tipos de servicios exactos
    service_map = {}
    data_list = []
    for munic in list_munic:
        number += 1
        service_map[number] = munic.des_dom  # Mapear número a nombre exacto del servicio
        data_list.append(f"\n{number}. {munic.des_dom.title()}")
    if language:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": f"Tell me the number of the municipality where you require your transfer and I will contact the available medical team in a few minutes🚑 \n{''.join(data_list)}"
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": f"Indicame el número del municipio donde requieres tu traslado y me pondré en contacto en breves minutos con el equipo médico disponible🚑 \n{''.join(data_list)}"
            }
        }
         
    enviar_mensajes_whatsapp(data)
    update_user_state_domiciliary(numero, 'WAITING_FOR_MUNICIPALITI_DOMI')
    return True

def confirm_service(numero, location):
    language = verify_language(numero)
    result = update_user_state_domiciliary(numero, 'WAITING_CONFIRM_MEDIC',municipalities=location)
    if result == True:
        with engine.connect() as conn: 
            domiciliary = conn.execute(user_state_domiciliary.select().where(user_state_domiciliary.c.numero==numero)
                                       .order_by(user_state_domiciliary.c.created_at.asc())).first()
        venezuela_tz = pytz.timezone('America/Caracas')
    
        # Obtener la hora actual en la zona horaria de Venezuela
        now = datetime.now(venezuela_tz)
        
        
        morning_limit = time(6, 0)  # 6:00 AM
        evening_limit = time(19, 0)  # 7:00 PM
        print("el now ", now)
        print("el morning_limit: ", morning_limit)
        print("el evening_limit: ", evening_limit)
       
        if now.time() <= evening_limit or now.time() >= morning_limit: 
            print("entra en el if ")
            with engine.connect() as conn:
                municipality = conn.execute(data_aten_med_domi.select()
                                            .where(data_aten_med_domi.c.des_dom==domiciliary.location)
                                            .where(data_aten_med_domi.c.hor_diu==True)).first()
            if language:
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": f"The daytime cost to the municipality {domiciliary.location} is {municipality.pre_amd}$💵. Do you want to confirm the service?"
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idconfirmdomiciliary",
                                        "title": "Confirm Service"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "iddeclinedomiciliary",
                                        "title": "Cancel Service"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idvolver",
                                        "title": "Back to top"
                                    }
                                },
                            ]
                        }
                    }
                }
            else:
                
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": f"El costo diurno al municipio {domiciliary.location} es de {municipality.pre_amd}$💵, ¿Desea confirmar el servicio?"
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idconfirmdomiciliary",
                                        "title": "Confirmar Servicio"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "iddeclinedomiciliary",
                                        "title": "Cancelar Servicio"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idvolver",
                                        "title": "Volver al Inicio"
                                    }
                                },
                            ]
                        }
                    }
                }
                
            print("envia el mensaje principal 2")
            enviar_mensajes_whatsapp(data)
            return True
        else:
            print("entra en el else")
            with engine.connect() as conn:
                municipality = conn.execute(data_aten_med_domi.select()
                                            .where(data_aten_med_domi.c.des_dom==domiciliary.location)
                                            .where(data_aten_med_domi.c.hor_diu==False)).first()
            if language:
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": f"The nightly cost to the municipality {domiciliary.location} is {municipality.pre_amd}$💵. Do you want to confirm the service?"
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idconfirmdomiciliary",
                                        "title": "Confirm Service"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "iddeclinedomiciliary",
                                        "title": "Cancel Service"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idvolver",
                                        "title": "Back to Top"
                                    }
                                },
                            ]
                        }
                    }
                }
            else:
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": f"El costo nocturno al municipio {domiciliary.location} es de {municipality.pre_amd}$💵, ¿Desea confirmar el servicio?"
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idconfirmdomiciliary",
                                        "title": "Confirmar Servicio"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "iddeclinedomiciliary",
                                        "title": "Cancelar Servicio"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idvolver",
                                        "title": "Volver al Inicio"
                                    }
                                },
                            ]
                        }
                    }
                }
            print("envia el mensaje principal 2")
            enviar_mensajes_whatsapp(data)
            return True
            
    else:
       
        if language:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "I didn't understand your answer very well, remember to only use the number corresponding to the options that I have proposed to you🤖👨🏻‍💻"
                }
            }
        else:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente a las opciones que te he propuesto🤖👨🏻‍💻"
                }
            }
        enviar_mensajes_whatsapp(data)
        update_user_state_domiciliary(numero, "WAITING_FOR_MUNICIPALITI_DOMI")
        return True 
    
def accept_domiciliary(numero):
    language = verify_language(numero)
    update_user_state_domiciliary(numero, 'CONFIRM_MEDIC_TEAM', confirm=True)
    if language:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "The Home Health Care Service has been confirmed 🩺, a medical team is on the way 🚑"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idvolver",
                                "title": "Back to Top"
                            }
                        },
                    ]
                }
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "El Servicio de atención médica domiciliaria ha sido confirmado 🩺, un equipo medico va en camino🚑"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idvolver",
                                "title": "Volver al Inicio"
                            }
                        },
                    ]
                }
            }
        }
        
    print("envia el mensaje principal 2")
    enviar_mensajes_whatsapp(data)
    return True

def decline_domiciliary(numero):
    language = verify_language(numero)
    update_user_state_domiciliary(numero, 'CANCEL_MEDIC_TEAM', confirm=False)
    if language:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "I have canceled the transportation of the medical equipment🗑 How can I help you again?📝."
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idservicios",
                                "title": "Services"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idplanes",
                                "title": "Plans"
                            }
                        }
                    ]
                }
            }
        }        
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "He cancelado el transporte del equipo médico🗑 ¿En que puedo ayudarte nuevamente?📝."
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idservicios",
                                "title": "Servicios"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idplanes",
                                "title": "Planes"
                            }
                        }
                    ]
                }
            }
        }   
    enviar_mensajes_whatsapp(data)
    return True