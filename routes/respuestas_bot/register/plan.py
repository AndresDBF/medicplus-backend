
import json
import http
from database.connection import engine
from models.usuarios import usuarios
from models.log import log
from models.user_state_register import user_state_register
from routes.user import get_user_state, get_user_state_register, get_user_state_identification_register
from routes.user import verify_user
from datetime import datetime
from sqlalchemy import insert, select

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
        
def get_list_plan(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "Puedo proporcionarte la información suficiente sobre nuestros planes para afiliados de MedicPlus🩺👨🏼‍⚕️, escribe el número correspondiente a uno de ellos para poder ayudarte👨‍💻\n\n1. Plan 1.\n2. Plan 2.\n3. Plan 3.\n4. Plan 4.\n5. Plan 5."
        }
    }
    
    enviar_mensajes_whatsapp(data)
    get_user_state_identification_register(numero,'INIT')
    with engine.connect() as conn:
        status_user = conn.execute(user_state_register.select().where(user_state_register.c.numero==numero)).first()
        if status_user.plan != "REGISTERED":
            
            get_user_state_register(numero, 'WAITING_FOR_SERVICE_PLAN')
    
        
    return True

def send_info_plan(numero, plan):
    result = get_user_state_register(numero, 'INIT', plan=plan)
    print("esto trae el result dentro de send info plan: ", result)
    if result == True:
        with engine.connect() as conn:
            get_plan = conn.execute(user_state_register.select().where(user_state_register.c.numero==numero)).first()
            #en esta linea vendria la consulta para la tabla donde se guardara la informacion de los planes 
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"A continuación de daré información sobre el plan {get_plan.plan}, finalmente puedes indicarme si deseas formar parte del grupo de Afiliados de MedicPlus y realizariamos en registro en el sistema en base a este plan👨‍💻:\n\n*Plan {get_plan.plan}*\n\nLorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries."
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconfirmplan",
                                "title": "Quiero ser Afiliado"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idplanes",
                                "title": "Planes"
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
        enviar_mensajes_whatsapp(data)
        return True
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "No comprendí muy bien tu respuesta, recuerda ingresar el número al plan que te he proporcionado para continuar con el proceso🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        get_user_state_register(numero, 'WAITING_FOR_SERVICE_PLAN')
        return True   
    
def send_name_affiliate(numero):
    print("entra en send_name_affiliate")
    with engine.connect() as conn:
        user = conn.execute(select(usuarios.c.plan).select_from(usuarios).where(usuarios.c.tel_usu==numero)).scalar()
        print("este es el user ", user)
    if user:
        print("entra en el if")
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": f"Contamos con tu registro en nuestro sistema como afiliado de Medic Plus con el plan {user}.👨🏻‍💻 Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud. ¡Selecciona la opcion que deseas consultar!"
            }
        }
        print("envia el mensaje principal 1")
        enviar_mensajes_whatsapp(data)
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "Atenciones Médicas"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idatenmedicpri",
                                "title": "Inmediata"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idtelemed",
                                "title": "Telemedicina"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idatenmeddomi",
                                "title": "Domiciliaria"
                            }
                        },
                    ]
                }
            }
        }
        print("envia el mensaje principal 2")
        enviar_mensajes_whatsapp(data)
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "Citas y Pruebas"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconmed",
                                "title": "Consultas Médicas"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idimagenologia",
                                "title": "Imagenología"
                            }
                        }
                    ]
                }
            }
        }
                    
        print("envia el mensaje principal 3")
        enviar_mensajes_whatsapp(data)

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "Citas y Pruebas"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconmed",
                                "title": "Consultas Médicas"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idimagenologia",
                                "title": "Imagenología"
                            }
                        }
                    ]
                }
            }
        }

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "Otros Servicios."
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idcalloper",
                                "title": "Llamar un Operador"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idlabori",
                                "title": "Laboratorio"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idambula",
                                "title": "Ambulancia"
                            }
                        },
                    ]
                }
            }
        }
                    
        print("envia el mensaje principal 4")
        enviar_mensajes_whatsapp(data)
        return True
    else:
        print("entra en el else")
        get_user_state_register(numero, 'WAITING_FOR_NAME')

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Comencemos con el registro para afiliados de Medicplus, Por favor envía tus nombres completos:"
            }
        }
        enviar_mensajes_whatsapp(data)
        return True
    