import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_lab import user_state_laboratory
from routes.user import get_user_state_lab, update_user_state_lab

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
 
 
def get_eco_or_rx(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"MedicPlus cuenta con servicios de Imagenología como Eco y Rx🩻 selecciona una de ellas:"
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idtestrx",
                            "title": "Prueba de RX"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idtesteco",
                            "title": "Prueba de Eco"
                        }
                    },
                ]
            }
        }
    } 
    enviar_mensajes_whatsapp(data)
    return True


def verify_rx(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"La prueba de RX tiene un costo de 30$💸 ¿Desea agendar la visita a nuestro laboratorio?"
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idconfirmrx",
                            "title": "Agendar Visita"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idcancelrx",
                            "title": "Cancelar Visita"
                        }
                    },
                ]
            }
        }
    } 
    enviar_mensajes_whatsapp(data)
    return True
    

def verify_eco(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"La prueba de Eco tiene un costo de 30$💸 ¿Desea agendar la visita a nuestro laboratorio?"
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idconfirmeco",
                            "title": "Agendar Visita"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idcanceleco",
                            "title": "Cancelar Visita"
                        }
                    },
                ]
            }
        }
    } 
    enviar_mensajes_whatsapp(data)
    return True

def confirm_rx(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"He notificado al personal de citas sobre tu solicitud de prueba de RX📢📝, pronto serás contactado por uno de ellos📞"
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idvolver",
                            "title": "Volver al Inicio"
                        }
                    }
                ]
            }
        }
    } 
    enviar_mensajes_whatsapp(data)
    return True

def confirm_eco(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"He notificado al personal de citas sobre tu solicitud de prueba de Eco📢📝, pronto serás contactado por uno de ellos📞"
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idvolver",
                            "title": "Volver al Inicio"
                        }
                    }
                ]
            }
        }
    } 
    enviar_mensajes_whatsapp(data)
    return True

def cancel_test(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"Tu visita ha sido Cancelada❌ Puedo Agendarte otra visita a nuestros laboratorios cuando desees ubicandote en el menú y en la opción Imagenología📍"
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idvolver",
                            "title": "Volver al Inicio"
                        }
                    }
                ]
            }
        }
    } 
    enviar_mensajes_whatsapp(data)
    return True