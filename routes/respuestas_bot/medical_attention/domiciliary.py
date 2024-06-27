import json
import http
from database.connection import engine
from models.usuarios import usuarios
from models.log import log
from routes.user import get_user_state, get_user_state_register, get_user_state_domiciliary, update_user_state_domiciliary
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

def get_municipality(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "preview_url": False,
            "body": "Indicame el municipio donde requieres tu traslado y me pondré en contacto en breves minutos con el equipo médico disponible🚑\n1. La Asunción\n2. Juangriego\n3. Porlamar\n4. Pampatar\n5. Santa Ana\n6. Punta de Piedra\n7. Altagracia"
        }
    }   
    enviar_mensajes_whatsapp(data)
    update_user_state_domiciliary(numero, 'WAITING_FOR_MUNICIPALITI_DOMI')
    return True 

def confirm_service(numero, location):
    result = update_user_state_domiciliary(numero, 'WAITING_CONFIRM_MEDIC',municipalities=location)
    if result == True:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "El tiempo de respuesta es de 30 minutos ⏳⏰ y el costo es de $30💵, ¿Desea confirmar el servicio?"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconfirmdomiciliary",
                                "title": "Si"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "iddeclinedomiciliary",
                                "title": "No"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idvolver",
                                "title": "Volver"
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
    get_user_state_domiciliary(numero, 'CONFIRM_MEDIC_TEAM')
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
                            "title": "Volver"
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
    get_user_state_domiciliary(numero, 'CANCEL_MEDIC_TEAM')
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