import json
import http
from database.connection import engine
from models.usuarios import usuarios
from models.log import log
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
        

def get_plan(numero):
    with engine.connect() as conn:
        user =  conn.execute(usuarios.select().where(usuarios.c.tel_usu==numero)).first()
    if user is None:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Gracias por decidir formar parte del grupo de Afiliados de MedicPlus, Te Guiaré los pasos que deberas seguir para formar parte de nuestro equipo🩺👨🏼‍⚕️\nComenzamos Escogiendo un plan en el que te gustaria pertenecer, puedes escoger alguno escribiendo el número correspondiente al plan #️⃣\n1. Plan 1.\n2. Plan 2.\n3. Plan 3.\n4. Plan 4.\n5. Plan 5."
            }
        }
        enviar_mensajes_whatsapp(data)
        get_user_state_register(numero, 'WAITING_FOR_PLAN')
        get_user_state_identification_register(numero,'INIT')
        
        return True
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "Contamos con tu registro en nuestro sistema como afiliado de Medic Plus.👨🏻‍💻 Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud. ¡Selecciona la opcion que deseas consultar!"
                },
                "action": {
                    "buttons":[
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
                        },
                    ]
                }
            }
        }
        print("envia el mensaje principal 1")
        enviar_mensajes_whatsapp(data)
        get_user_state_identification_register(numero, 'INIT')
        return True

#funcion en caso de que quiera pedir los planes y ya se encuentre registrado
def is_affiliate(numero):
    with engine.connect() as conn:
        user = conn.execute(select(usuarios.c.plan).select(usuarios).where(usuarios.c.tel_usu==numero)).first()
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": f"Contamos con tu registro en nuestro sistema como afiliado de Medic Plus con el plan {user.plan}.👨🏻‍💻 Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud. ¡Selecciona la opcion que deseas consultar!"
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
                "text": "Otros Servicios."
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
                
    print("envia el mensaje principal 3")
    enviar_mensajes_whatsapp(data)
    return True


def insert_plan(numero, texto):
    result = get_user_state_register(numero, 'WAITING_FOR_NAME', plan=texto)
    if result == True:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Gracias. Por favor envía tus nombres completos:"
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
                "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente al plan que te he propuesto🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        return True
    
def insert_name(numero, texto):
    result = get_user_state_register(numero, 'WAITING_FOR_SURNAME', nombre=texto)
    if result == True:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Por favor envía tus apellidos completos:"
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
                "body": "No comprendí muy bien tu respuesta, recuerda ingresar un nombre mayor a 2 caracteres y utilizando solamente letras para continuar con el proceso🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        return True    
    
def insert_last_name(numero, texto):
    result = get_user_state_register(numero, 'WAITING_FOR_ID', apellido=texto)
    if result == True:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Por favor envía tu cédula de identidad:"
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
                "body": "No comprendí muy bien tu respuesta, recuerda ingresar un apellido mayor a 2 caracteres y utilizando solamente letras para continuar con el proceso🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        return True    
 

def insert_identification(numero, texto):
    result = get_user_state_register(numero, 'WAITING_FOR_EMAIL', cedula=texto)
    if result == True:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Finalmente, por favor envía tu correo electrónico:"
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
                "body": "No comprendí muy bien tu respuesta, recuerda ingresar el número de cedula utilizando solamente números y que sean un mininmo de 7 para continuar con el proceso🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        return True
    
def insert_email(numero, texto, user):
    result = get_user_state_register(numero, 'INIT', email=texto)
    if result == True:
        # Aquí guarda el usuario en la base de datos
        print(f"el user plan: {user['plan']} y el tipo de dato es {type(user['plan'])}")
        plan = int(user['plan'])
        print(f"asi queda el plan {plan} y este es el tipo de dato {type(plan)}")
        with engine.connect() as conn:
            conn.execute(usuarios.insert().values(use_nam=user['nombre'].lower(),
                                                  email=texto,
                                                  nom_usu=user['nombre'].title(),
                                                  ape_usu=user['apellido'].title(), 
                                                  ced_usu=user['cedula'],
                                                  plan=plan,
                                                  tel_usu=numero))
            conn.commit()
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "He procesado tu información exitosamente.📝 uno de nuestros asesores de ventas 🧑🏻‍💼👨🏼‍💼 se pondrá en contacto contigo en la brevedad posible."
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idvolver",
                                "title": "Volver"
                            }
                        }
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
                "body": "No comprendí muy bien tu respuesta, debes ingresar una direccion de correo válida para continuar con el proceso🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)    
        return True 
    