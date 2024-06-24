import json
import http
from database.connection import engine
from models.log import log
from routes.user import verify_user
from datetime import datetime
from sqlalchemy import insert

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
        "Authorization": "Bearer EAAOJtyjmw9EBO8dJGrruwB1PiX9keXnZBH4Ga82ECi0ZAcAh3uIWQrSg30q8ljJDzldrZA7utAZAkWqU2SP3AwK2dJQjOdGcDoIdyJxbqYdPKD8HszolWnVLMsAJBpe95TLlUu7NUjq0SCMq92K6RTIdtOoqvsEPiMLltCIICKlyvNndz0KQHMcrfglDFUQvOnZCmIvg7DKZAGL3GoqwIZD"
    }
    
    connection = http.client.HTTPSConnection("graph.facebook.com")
    
    try:
        connection.request("POST", "/v19.0/330743666794546/messages", data, headers)
        response = connection.getresponse()
        response_data = response.read().decode()
        
        if response.status != 200:
            agregar_mensajes_log(f"Error al enviar mensaje: {response.status} {response.reason} {response_data}")
    except Exception as e:
        print(f"Exception: {e}")
        agregar_mensajes_log(f"Exception al enviar mensaje: {e}")
    finally:
        connection.close()
        
def principal_message(numero):
    print("pasa las expresiones regulares")
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "¡Hola!👋🏼 Soy MedicBot🤖, tu asistente virtual de salud. ¿En qué puedo ayudarte hoy? Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud. ¡Escribe tu consulta y comencemos!."
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
    print("envia el mensaje principal")
    enviar_mensajes_whatsapp(data)
    return True

def get_services(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "A continuación te enseño los servicios que Medic Plus puede ofrecerte 🩺, puedes seleccionar alguno de ellos y a la brevedad te guiaré los pasos que deberás seguir según tu solicitud📌👨🏻‍💻"
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
                            "title": "Primaria"
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
                        "id": "conmed",
                        "title": "Consultas Médicas"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": "labori",
                        "title": "Laboratorio"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": "ambula",
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

def get_plan(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "Aun no cuento con esta funcion, pronto podre ayudarte"
        }
    }
    enviar_mensajes_whatsapp(data)

def return_button(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Gracias por confiar en nuestros servicios de MedicPlus🩺. ¿En que puedo ayudarte nuevamente?📝."
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

def message_not_found(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "preview_url": False,
            "body": (
                "No comprendo muy bien tu mensaje, por favor puedes repetirlo nuevamente.\n \nRecuerda Utilizar los botones proporcionados para poderte ayudar🤖"
            )
        }
    }
    enviar_mensajes_whatsapp(data)
    return True
    
""" 
def is_affiliate(numero):
    result_json = verify_user(numero)
    #mensajes que seran mostrados cuando el usuario seleccione que es afiliado se verifica si de verdad esta registrado
    #se encontrara un mensaje positivo dando las opciones y otro para pedir registrarse o hacerlo mas tarde
    print("------------saliendo de verify_user-----------------")
    print("esto trae el result_json: ", result_json)
    if result_json["registered"] == False:
        print("entra en el if")
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"{result_json['text']}"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idtarde",
                                "title": "Mas tarde"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idno",
                                "title": "Quiero Registrarme"
                            }
                        }
                    ]
                }
            }
        }
        print("envia el mensaje principal 3")
        enviar_mensajes_whatsapp(data)
        return True
    else:
        print("entra en el else")
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": f"{result_json['text']}"
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
                                "title": "Primaria"
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
                            "id": "conmed",
                            "title": "Consultas Médicas"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "labori",
                            "title": "Laboratorio"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "ambula",
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

def affiliate_later(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": f"Puedo ayudarte en el momento que desees 🤖 Bien sea, programar una cita👨🏼‍⚕️ o responder preguntas generales de salud 📝 ¡Puedes volver al inicio cuando desees presionando el boton inferior!☑️🔘"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idinicio",
                            "title": "Ir al Inicio"
                        }
                    }
                ]
            }
        }
    }
    print("envia el mensaje principal 3")
    enviar_mensajes_whatsapp(data)
    return True

 """