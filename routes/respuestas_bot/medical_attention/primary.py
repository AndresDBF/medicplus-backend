
import json
import http
from database.connection import engine
from models.usuarios import usuarios
from models.user_state_register import user_state_register
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

#pregunta primero si es afiliado o no 
def question_affilate(numero):
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
                    "text": f"Thank you for selecting our Immediate Medical Care service👨🏼‍⚕️, tell me if you are a MedicPlus Affiliate🩺"
                },
                
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconfirmaffiliate",
                                "title": "I am an Affiliate"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idnotaffiliate",
                                "title": "Unaffiliated"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idvolver",
                                "title": "Back To Top"
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
                    "text": f"Gracias por seleccionar nuestro servicio de Atención Médica Inmediata👨🏼‍⚕️, indicame si eres Afiliado de MedicPlus🩺"
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
                "body": "Por favor me indicas tu número de identidad y buscaré en el sistema que tipo de afiliado eres.👨🏻‍💻"
            }
        }      
    print("envia el mensaje principal")
    enviar_mensajes_whatsapp(data)
    get_user_state_identification_register(numero, 'WAITING_FOR_ID')
    return True


def get_information_for_identification(numero, cedula):
    language = verify_language(numero)
    result = get_user_state_identification_register(numero, "IDENTIFICATION_FOUND", cedula)
    if result == True:
        with engine.connect() as conn:
            user = conn.execute(usuarios.select().where(usuarios.c.ced_usu==cedula)).first()
        if not user:
            if language:
                data = {
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": f"I have not found the identity number that you have provided me in the system.\n\n You can give me your identification again and I will perform the search in the system.👨🏻‍💻 \n\nYou can also go back to the beginning if you want↩️"
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
            get_user_state_identification_register(numero, "WAITING_FOR_ID", cedula)
            return True
        else:
            if language:
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": f"I have contacted our operators who will provide your requested service through an alarm in the name of {user.nom_usu} {user.ape_usu}📢 in a few minutes you will be contacted by one of them📲☎️"
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
                            "text": f"He contactado con nuestros operadores que brindarán tu servicio solicitado mediante una alarma a nombre de {user.nom_usu} {user.ape_usu}📢 en breves minutos serás contactado por uno de ellos📲☎️"
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
        get_user_state_identification_register(numero, "WAITING_FOR_ID", cedula)
        return True
        
#funcion utilizada solo para los no afiliados 
def get_info_primary_attention(numero):
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
                    "text": "Do you want to Generate an Alarm to be called?📞 \n\nIf you select Yes☑️ in minutes you will receive a call from one of our available operators that will cover your service👨🏼‍⚕️ \n\nIf you select No❌ we will cancel your request. \n\nYou can return to the main screen by pressing the Back to Home↩️ button."
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idllamar",
                                "title": "Confirm"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idnollamar",
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
                    "text": "¿Deseas Generar una Alarma para ser llamado?📞 \n\nSí seleccionas Si☑️ en minutos recibirás una llamadas de uno de nuestros operadores disponibles que cubriran tu servicio👨🏼‍⚕️ \n\nSí seleccionas No❌ daremos por cancelada tu petición. \n\nPuedes volver a la pantalla principal Presionando el botón Volver al inicio↩️."
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idllamar",
                                "title": "Confirmar"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idnollamar",
                                "title": "Cancelar"
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
                    "text": "I have canceled your request for immediate medical attention🗑 How can I help you again?📝."
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
                    "text": "I have generated the alarm towards our operators 📢, you will receive a call in the next few minutes 📞⌚"
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
                    "text": "He generado la alarma hacia nuestros operadores 📢, recibirás una llamada en los proximos minutos📞⌚"
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



