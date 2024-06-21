
import json
import http
from database.connection import engine
from models.usuarios import usuarios
from models.log import log
from routes.user import get_user_state, get_user_state_register
from routes.user import verify_user
from datetime import datetime
from sqlalchemy import insert, select

def agregar_mensajes_log(texto):
    try:
        texto_str = json.dumps(texto)
        print("asi queda el texto antes de insertar en el log: ", texto_str)
        print("y este es el tipo de dato: ", type(texto_str))
        with engine.connect() as conn:
            conn.execute(log.insert().values(texto=texto_str, fecha_y_hora=datetime.utcnow()))
            conn.commit()
        print("Mensaje guardado en el log:", texto)
    except Exception as e:
        print(f"Error al guardar el mensaje en el log: {e}")

def enviar_mensajes_whatsapp (data):
    
    data = json.dumps(data)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAOJtyjmw9EBOyAEc9G5t2L0OpAwMMrGKgOMyZAFxZAxagGQxZC4qwIOZBVxdVMLafbM84V3Va8IOTexfJK3wP2JDubvyNeVZAjaFZBVQRfo8fzJhmdtJXe3qQsFE5YwzVjVZAfgC4qgoyOZBj4LfkgBNkkGnlduqd3TtwMYcWIhcZCSHpAkgu2fZAodR5ndKcKVvVtDwSdrhtnwtjatklOdUZD"
    }
    
    connection = http.client.HTTPSConnection("graph.facebook.com")
    
    try:
        connection.request("POST", "/v19.0/330743666794546/messages", data, headers)
        response = connection.getresponse()
        response_data = response.read().decode()
        print("se enviaron los mensajes")
        print("este fue el response al enviar el mensaje: ", response.status, response.reason, response_data)
        if response.status != 200:
            agregar_mensajes_log(f"Error al enviar mensaje: {response.status} {response.reason} {response_data}")
    except Exception as e:
        print(f"Exception: {e}")
        agregar_mensajes_log(f"Exception al enviar mensaje: {e}")
    finally:
        connection.close()
        

def get_plan(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "Para registrarte, Te Guiaré los pasos que deberas seguir para formar parte de nuestros Afiliados en Medic Plus🩺👨🏼‍⚕️\nComenzamos Escogiendo un plan en el que te gustaria pertenecer, puedes escoger alguno escribiendo el numero correspondiente al plan #️⃣\n1. Plan 1.\n2. Plan 2.\n3. Plan 3.\n4. Plan 4.\n5. Plan 5."
        }
    }
    enviar_mensajes_whatsapp(data)
    get_user_state_register(numero, 'WAITING_FOR_PLAN')
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
                "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el numero correspondiente al plan que te he propuesto🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        return True
    
def insert_name(numero, texto):
    get_user_state_register(numero, 'WAITING_FOR_SURNAME', nombre=texto)
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
    
def insert_last_name(numero, texto):
    get_user_state_register(numero, 'WAITING_FOR_ID', apellido=texto)
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "Perfecto. Por favor envía tu cédula:"
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
                "body": "Muy bien. Finalmente, por favor envía tu correo electrónico:"
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
                "body": "No comprendí muy bien tu respuesta, recuerda ingresar el número de cedula utilizando solamente números para continuar con el proceso🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        return True
    
def insert_email(numero, texto, user):
    result = get_user_state_register(numero, 'REGISTERED', email=texto)
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
                    "text": "Su informacion ha sido registrada exitosamente.📝 uno de nuestros asesores de ventas 🧑🏻‍💼👨🏼‍💼 se pondra en contacto con usted en la brevedad posible."
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