
import json
import http
from database.connection import engine
from models.usuarios import usuarios
from models.log import log
from routes.user import get_user_state, get_user_state_register, get_user_state_identification, get_user_state_identification_register
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
        "Authorization": "Bearer EAAOJtyjmw9EBOyAEc9G5t2L0OpAwMMrGKgOMyZAFxZAxagGQxZC4qwIOZBVxdVMLafbM84V3Va8IOTexfJK3wP2JDubvyNeVZAjaFZBVQRfo8fzJhmdtJXe3qQsFE5YwzVjVZAfgC4qgoyOZBj4LfkgBNkkGnlduqd3TtwMYcWIhcZCSHpAkgu2fZAodR5ndKcKVvVtDwSdrhtnwtjatklOdUZD"
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

#pregunta primero si es afiliado o no 
def question_affilate(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"Gracias por seleccionar nuestro servicio de Atención Médica Inmediata👨🏼‍⚕️, Primeramente me gustaria que me indicaras si eres Afiliado de Medic Plus🩺"
            },
            
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idconfirmaffiliate",
                            "title": "Si Soy afiliado"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idnotaffiliate",
                            "title": "No Soy Afiliado"
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

#en caso de ser afiliado comienza este flujo 

#funcion utilizada al inicio del flujo para afiliados y verifica el numero de identidad
def get_info_identification_attention_primary(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "preview_url": False,
            "body": "Gracias por escoger nuestro servicio de Atención Médica Inmediata 🚑🩺\n\n Por favor me indicas tu numero de identidad y buscare en el sistema que tipo de afiliado eres.👨🏻‍💻"
        }
    }    
    print("envia el mensaje principal")
    enviar_mensajes_whatsapp(data)
    get_user_state_identification_register(numero, 'WAITING_FOR_ID')
    return True


def get_information_for_identification(numero, cedula):
    result = get_user_state_identification(numero, "IDENTIFICATION_FOUND", cedula)
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
                        "text": f"No he encontrado en el sistema el número de identidad que me has proporcionado.\n\n Puedes volver a darme tu identificación y realizaré la busqueda en el sistema.👨🏻‍💻 \n\nTambién puedes volver al inicio si deseas↩️"
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
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"He contactado con nuestros operadores que brindaran tu servicio solicitado mediante una alarma a nombre de {user.nom_usu} {user.ape_usu}📢 en breves minutos seras contacto por uno de ellos📲☎️"
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
                "body": "El numero de identidad ingresado no es válido, puedes volver a proporcionarlo tomando en cuenta los siguientes aspectos: \n\n☑️ Cádena de Números mayor a 7\n\n☑️ El mensaje no debe contener letras, espacios o caracteres especiales (puntos, comas, numerales, etc)"
            }
        }    
        print("envia el mensaje principal")
        enviar_mensajes_whatsapp(data)
        return True
        
#funcion utilizada solo para los no afiliados 
def get_info_primary_attention(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": "¿Desea Generar una Alarma para ser llamado?📞 \n\nSí seleccionas Si☑️ en minutos recibirias una llamadas de uno de nuestros operadores disponibles, con el fin de cubrir tu atención médica inmediata.👨🏼‍⚕️ \n\nSí seleccionas No❌ daremos por cancelada tu petición. \n\nPuedes volver a la pantalla principal Presionando el botón Volver al inicio↩️."
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idllamar",
                            "title": "Sí"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "idnollamar",
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

def cancel_call(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "He cancelado tu solicitud de atención médica inmediata🗑 ¿En que puedo ayudarte nuevamente?📝."
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

#funcion tanto para afiliado como para no afiliado
def confirm_call(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": "He generado la alarma hacia nuestros operadores 📢 Tomando en cuenta tu número telefónico📱, recibirás una llamada en los proximos minutos📞⌚"
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
    enviar_mensajes_whatsapp(data)
    return True



