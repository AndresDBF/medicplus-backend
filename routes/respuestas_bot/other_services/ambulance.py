import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_ambulance import user_state_ambulance
from routes.user import get_user_state_ambulance, update_user_state_ambulance

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
 
def get_list_municipalities(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "preview_url": False,
            "body": "Indicame el municipio donde requieres tu traslado y me pondré en contacto en breves minutos con una unidad disponible🚑\n1. La Asunción\n2. Juangriego\n3. Porlamar\n4. Pampatar\n5. Santa Ana\n6. Punta de Piedra\n7. Altagracia"
        }
    }   
    enviar_mensajes_whatsapp(data)
    update_user_state_ambulance(numero, 'WAITING_FOR_MUNICIPALITI')
    return True

def select_municipalities(numero, texto):
    result = update_user_state_ambulance(numero, 'WAITING_CONFIRM_AMBULANCE',texto)
    if result == True:
        with engine.connect() as conn:
            location = conn.execute(select(user_state_ambulance.c.location).select_from(user_state_ambulance).where(user_state_ambulance.c.numero==numero)).scalar()
        
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"El costo del traslado desde el municipio {location} es de 30$, ¿Deseas confirmar de inmediato el traslado de la unidad?.🚑"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconfirmambulance",
                                "title": "Confirmar Unidad"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idcancelambulance",
                                "title": "Cancelar Unidad"
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
                "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente a las opciones que te he propuesto🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        update_user_state_ambulance(numero, "WAITING_FOR_MUNICIPALITI")
        return True 
 
def confirm_ambulance(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"He generado una alarma inmediata a una unidad disponible 📢 en breves minutos serás contactado por nuestro personal para el cobro del traslado de la ambulancia📲💸"
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
    enviar_mensajes_whatsapp(data)
    update_user_state_ambulance(numero, "CONFIRM_AMBULANCE", confirm=True)
    return True 

def cancel_ambulance(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"He cancelado tu solicitud de ambulancia ❌ Puedes solicitarla cuando desees ubicandote en el menú y en la opción Ambulancia📍"
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
    enviar_mensajes_whatsapp(data)
    update_user_state_ambulance(numero, "CANCEL_AMBULANCE", confirm=False)
    return True 