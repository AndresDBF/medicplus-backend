import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_register import user_state_register

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

def verify_language(numero):
    with engine.connect() as conn:
        result = conn.execute(select(user_state_register.c.language).select_from(user_state_register).where(user_state_register.c.numero==numero)).scalar()
        print(f"-----------------el result del traductor {result}----------------------------")
    return result 
 
def question_operator(numero):
    language = verify_language(numero)
    if language:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"Our trained staff will have enough time to manage your requests, in moments I will contact an operator available to manage your request. Do you want to communicate with an operator? .🚑"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconfirmoper",
                                "title": "Accept"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idcanceloper",
                                "title": "Cancel"
                            }
                        }
                    ]
                }
            }
        }  
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"Nuestro personal capacitado dispondrá del tiempo suficiente en gestionar tus solicitudes, en instantes me comunicaré con un operador disponible para gestionar tu solicitud. ¿Deseas comunicarte con un operador? .🚑"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconfirmoper",
                                "title": "Aceptar"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idcanceloper",
                                "title": "Cancelar"
                            }
                        }
                    ]
                }
            }
        }
        
    enviar_mensajes_whatsapp(data)
    return True

def confirm_oper(numero, name_contact):
    language = verify_language(numero)
    if language:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"I have contacted one of our operators and in minutes you will receive a monitored call to respond to your request📞☎️"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idvolver",
                                "title": "Back to Top"
                            }
                        }
                    ]
                }
            }
        }  
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"He contactado con uno de nuestros operadores y en minutos recibirás una llamada monitoreada para atender a tu solicitud📞☎️"
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
    with engine.connect() as conn:
        user_affiliate = conn.execute(usuarios.select().where(usuarios.c.tel_usu==numero)).first()
    if user_affiliate:
        #enviando un mensaje al operador 
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": "584123939200",
            "type": "text",
            "text": {
                "preview_url": False,
                "body": f"Hola👋🏼 Soy MedicBot 🤖 asistente virtual de MedicPlus, Un usuario afiliado ha solicitado el servicio de un operador para cubrir una solicitud, te he escogido para atender a su llamado☎️ su nombre de afiliado se encuentra registrado como: {user_affiliate.nom_usu} {user_affiliate.ape_usu} y su número de teléfono es: +{numero} \n\nMuchas gracias por tu tiempo✅ "
            }
        }            
        enviar_mensajes_whatsapp(data)
        return True
    else:
       
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": "584123939200",
            "type": "text",
            "text": {
                    "preview_url": False,
                    "body": f"Hola👋🏼 Soy MedicBot 🤖 asistente virtual de MedicPlus, Un usuario ha solicitado el servidor de un operador para cubrir una solicitud, te he escogido para atender a su llamado☎️ su nombre de Whats app es: {name_contact} y su numero de telefono es: +{numero} \n\nMuchas gracias por tu tiempo✅ "
            }
        }            
        enviar_mensajes_whatsapp(data)
        return True
        

def cancel_oper(numero):
    language = verify_language(numero)
    if language:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"I have canceled your call to the operator ❌ You can request it again whenever you want by going to the menu and the option Call an Operator📍"
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
                    "text": f"He cancelado tu llamada al operador ❌ Puedes solicitarla nuevamente cuando desees ubicandote en el menú y en la opción Llamar un Operador📍"
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
    return True 