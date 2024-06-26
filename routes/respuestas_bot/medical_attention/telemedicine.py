import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from routes.user import get_user_state_identification_register

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
        "Authorization": "Bearer EAAOJtyjmw9EBO6uqJ5DXrNx0Ead4zZBAYLWw9KJ5JbRY8MiaYNj7wQmctyt3C5FzosjRnikFQbmU4ajsJ46HlbXygDodryt1i8Qp4zfEd4rPRMFwXpzZBBUdFE79YA9yD9qT70i6I2FFbyyEP1hKOCa6yeBZCzYJdm7Ea3I56sMGZCKbqsvIFrOvSX1cVmyjZAu7zsxhd72E6oYZC3CAWw8gZDZD"
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
        
def get_info_identification_telemedicine(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "preview_url": False,
            "body": "Gracias por escoger nuestro servicio de telemedicina 📞\n\nPor favor me indicas tu numero de identidad y buscare en el sistema que tipo de afiliado eres.👨🏻‍💻"
        }
    }    
    print("envia el mensaje principal")
    enviar_mensajes_whatsapp(data)
    get_user_state_identification_register(numero, 'WAITING_FOR_ID_TELEMEDICINE')
    return True

def send_information_for_telemedicine(numero, cedula):
    result = get_user_state_identification_register(numero, "IDENTIFICATION_FOUND", cedula)
    if result == True:
        with engine.connect() as conn:
            user = conn.execute(usuarios.select().where(usuarios.c.ced_usu==cedula)).first()
        if not user:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"No he encontrado en el sistema el número de identidad que me has proporcionado, sin embargo puedes decidir entre las siguientes opciones.\n\n☑️Puedes volver a darme tu identificación y realizaré nuevamente la busqueda en el sistema.👨🏻‍💻 \n\n☑️Puedes unirte a nuestro grupo de afiliados de medic plus presionando el boton 'Quiero ser Afiliado'👨🏼‍💼🧑🏻‍💼🔵 \n\n☑️Puedes volver al inicio si deseas↩️"
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
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": "¿Desea Generar una Alarma para ser llamado?📞 \n\nsi seleccionas Si☑️ en minutos recibirias una llamada de uno de nuestros operadores disponibles que cubrirá tu servicio de telemedicina📞👨🏼‍⚕️ \n\nSi seleccionas No❌ daremos por cancelada tu petición. \n\nPuedes volver a la pantalla principal Presionando el botón Volver al inicio↩️.  "
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idconfirmtelemedicine",
                            "title": "Sí"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "iddeclinelemedicine",
                            "title": "No"
                        }
                    },
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


def cancel_telemedicine(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "He cancelado tu solicitud de telemedicina🗑 ¿Deseas alguna otra ayuda?🤖"
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
                            "id": "telemed",
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






