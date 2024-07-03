import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_register import user_state_register
from routes.user import get_user_state_identification_register

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
        print(f"--------------el lenguaje: {result}---------------")
    return result    

 
def get_info_identification_telemedicine(numero):
    language = verify_language(numero)
    if language:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Please tell me your identity number and I will search the system to find out what type of affiliate you are.👨🏻‍💻"
            }
        }  
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Por favor me indicas tu número de identidad y buscare en el sistema que tipo de afiliado eres.👨🏻‍💻"
            }
        }  
    print("envia el mensaje principal")
    enviar_mensajes_whatsapp(data)
    get_user_state_identification_register(numero, 'WAITING_FOR_ID_TELEMEDICINE')
    return True

def send_information_for_telemedicine(numero, cedula):
    language = verify_language(numero)
    result = get_user_state_identification_register(numero, "IDENTIFICATION_FOUND", cedula)
    if result == True:
        with engine.connect() as conn:
            user = conn.execute(usuarios.select().where(usuarios.c.ced_usu==cedula)).first()
        if language:
            if not user:
                data = {
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": f"I have not found the identity number that you have provided me in the system, you can do the following: You can join our group of MedicPlus affiliates by pressing the button I want to be an Affiliate👨🏼‍💼🧑🏻‍💼🔵 \n\n☑️You can go back to the beginning if you want↩️"
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idregistrar",
                                        "title": "Be affiliated"
                                    }
                                },
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
                print("envia el mensaje principal")
                enviar_mensajes_whatsapp(data)
                get_user_state_identification_register(numero, "WAITING_FOR_ID_TELEMEDICINE", cedula)
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
                            "text": f"I have contacted our operators in charge of telemedicine services through an alarm in the name of {user.nom_usu} {user.ape_usu}📢 in a few minutes you will be contacted by one of them📲☎️"
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idvolver",
                                        "title": "Volver al inicio"
                                    }
                                },
                            ]
                        }
                    }
                }  
                print("envia el mensaje principal")
                enviar_mensajes_whatsapp(data)
                return True
        else:
            if not user:
                data = {
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": f"No he encontrado en el sistema el número de identidad que me has proporcionado, puedes realizar lo siguiente:.\n\n☑️Puedes volver a darme tu identificación y realizaré nuevamente la busqueda en el sistema.👨🏻‍💻 \n\n☑️Puedes unirte a nuestro grupo de afiliados de MedicPlus presionando el boton Quiero ser Afiliado👨🏼‍💼🧑🏻‍💼🔵 \n\n☑️Puedes volver al inicio si deseas↩️"
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idregistrar",
                                        "title": "Quiero ser Afiliado"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idvolver",
                                        "title": "Volver al inicio"
                                    }
                                }
                            ]
                        }
                    }
                }    
                print("envia el mensaje principal")
                enviar_mensajes_whatsapp(data)
                get_user_state_identification_register(numero, "WAITING_FOR_ID_TELEMEDICINE", cedula)
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
                            "text": f"He contactado con nuestros operadores encargados de los servicios de telemedicina mediante una alarma a nombre de {user.nom_usu} {user.ape_usu}📢 en breves minutos seras contactado por uno de ellos📲☎️"
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "idvolver",
                                        "title": "Volver al inicio"
                                    }
                                },
                            ]
                        }
                    }
                }  
                print("envia el mensaje principal")
                enviar_mensajes_whatsapp(data)
                return True
    else:
        if language:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "The identity number entered is not valid, you can provide it again taking into account the following aspects: \n\n☑️ Number String greater than 7\n\n☑️ The message must not contain letters, spaces or special characters (dots, commas, numerals, etc.)"
                }
            }    
        else:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "El número de identidad ingresado no es válido, puedes volver a proporcionarlo tomando en cuenta los siguientes aspectos: \n\n☑️ Cádena de Números mayor a 7\n\n☑️ El mensaje no debe contener letras, espacios o caracteres especiales (puntos, comas, numerales, etc)"
                }
            }  
        print("envia el mensaje principal")
        enviar_mensajes_whatsapp(data)
        get_user_state_identification_register(numero, "WAITING_FOR_ID_TELEMEDICINE", cedula)
        return True
   
 
def get_info_telemedicine_attention(numero):
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
                    "text": "Do you want to Generate an Alarm to be called?📞 \n\nIf you select Yes☑️ in minutes you would receive a call from one of our available operators who will cover your telemedicine service📞👨🏼‍⚕️ \n\nIf you select No❌ we will cancel your petition. \n\nYou can return to the main screen by pressing the Back to Home↩️ button.  "
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconfirmtelemedicine",
                                "title": "Confirm"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "iddeclinelemedicine",
                                "title": "Cancel"
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
                    "text": "¿Deseas Generar una Alarma para ser llamado?📞 \n\nsi seleccionas Si☑️ en minutos recibirias una llamada de uno de nuestros operadores disponibles que cubrirá tu servicio de telemedicina📞👨🏼‍⚕️ \n\nSi seleccionas No❌ daremos por cancelada tu petición. \n\nPuedes volver a la pantalla principal Presionando el botón Volver al inicio↩️.  "
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconfirmtelemedicine",
                                "title": "Confirmar"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "iddeclinelemedicine",
                                "title": "Cancel"
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
        
    print("envia el mensaje principal")
    enviar_mensajes_whatsapp(data)
    return True


def cancel_telemedicine(numero):
    language = verify_language(numero)
    if language:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "I have canceled your telemedicine request🗑 How can I help you again?📝."
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
                    "text": "He cancelado tu solicitud de telemedicina🗑 ¿En que puedo ayudarte nuevamente?📝."
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
    print("envia el mensaje principal 1")
    enviar_mensajes_whatsapp(data)
    return True
