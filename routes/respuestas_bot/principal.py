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
            "footer": {
                "text": "Dinos si eres o quieres ser un Afiliado de MedicPlus."
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "si",
                            "title": "Afiliado"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "no",
                            "title": "Quiero Ser Afiliado"
                        }
                    }
                ]
            }
        }
    }
    print("envia el mensaje principal")
    enviar_mensajes_whatsapp(data)
    return True

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
                                "id": "tarde",
                                "title": "Mas tarde"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "no",
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
                                "id": "atenmedicpri",
                                "title": "Primaria"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "telemed",
                                "title": "Telemedicina"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "atenmeddomi",
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

def return_button(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "Gracias por formar parte de los afiliados de MedicPlus🩺. ¿En que puedo ayudarte hoy?📝."
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
                            "id": "atenmedicpri",
                            "title": "Primaria"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "telemed",
                            "title": "Telemedicina"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "atenmeddomi",
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
    
