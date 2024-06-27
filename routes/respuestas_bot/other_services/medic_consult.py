import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_especiality import user_state_especiality
from routes.user import verify_user, get_user_state_identification, get_user_state_identification_register, update_user_state_especiality, get_user_state_especiality

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
    
def get_list_speciality(numero):
    print("entra en el mensaje de consultas medicas ")
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "preview_url": False,
            "body": "Gracias por escoger nuestro servicio de Consultas Médicas 🩻 \n\Indicame el número de algunas de nuestras especialidades disponibles y en breves minutos podré agendar tu cita📆. Estas son nuestras especialidades disponibles:\n1. Médico General\n2. Pediatría \n3. Traumatología \n4. Neumología \n5. Neurología \n6. Cardiología \n"
        }
    }   
    enviar_mensajes_whatsapp(data)
    update_user_state_especiality(numero, 'WAITING_FOR_SPECIALITY')
    return True

def get_names_especialitys(numero, especialidad):
    
    result = update_user_state_especiality(numero=numero, state='WAITING_FOR_NAME_ESP', especialidad=especialidad)
    if result == True:
        if especialidad == "1":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los médicos generales disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️\n1. Doctor 1\n2. Doctor 2\n3. Doctor 3\n4. Doctor 4"
                }
            }   
        elif especialidad == "2":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Pediatría disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️ \n1. Doctor 1\n2. Doctor 2\n3. Doctor 3\n4. Doctor 4"
                }
            }   
        elif especialidad == "3":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Traumatología disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️ \n1. Doctor 1\n2. Doctor 2\n3. Doctor 3\n4. Doctor 4"
                }
            }   
        elif especialidad == "4":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Neumología disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️ \n1. Doctor 1\n2. Doctor 2\n3. Doctor 3\n4. Doctor 4"
                }
            }   
            
        elif especialidad == "5":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Neurología disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️ \n1. Doctor 1\n2. Doctor 2\n3. Doctor 3\n4. Doctor 4"
                }
            }   
        elif especialidad == "6":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Cardiología disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️ \n1. Doctor 1\n2. Doctor 2\n3. Doctor 3\n4. Doctor 4"
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
                "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente a la especialidad que te he propuesto🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        update_user_state_especiality(numero, "WAITING_FOR_SPECIALITY")
        return True 
        
def save_appointment(numero, nombre_medico):
    print("entra en save_appointment")
    print("a punto de llamar a la funcion para la variable especiality")
    especiality = update_user_state_especiality(numero=numero, state='WAITING_FOR_CONFIRM', nombre_medico=nombre_medico)
    
    if especiality == True:
        with engine.connect() as conn:
            name_esp = conn.execute(user_state_especiality.select().where(user_state_especiality.c.numero==numero).order_by(user_state_especiality.c.created_at.asc())).first()
            print("esto trae name_esp: ", name_esp)            
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"El costo total de la consulta es de 30$💸\n¿Deseas Agendar la cita con el especialista en {name_esp.nom_esp}?  \n\nSi confirmas la consulta, transferiré tu solicitud hacia la persona encargada de citas.\n\nPuedes cancelar la solicitud presionando el boton No❌ o Volver al inicio↩️"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconfirmconsult",
                                "title": "Si"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "iddeclineconsult",
                                "title": "No"
                            }
                        },
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
                "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente a los doctores que te he propuesto🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        print("a punto de llamar a la funcion en el else de respuesta incorrecta")
        update_user_state_especiality(numero, "WAITING_FOR_NAME_ESP")
        return True 

def confirm_consult(numero):
    print("llama a la funcion en confirm consult")
    update_user_state_especiality(numero, "CONFIRM_CONSULT")
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"Tu consulta ha sido confirmada exitosamente📝✅ Agendaré tu cita con el especialista seleccionado!"
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

def cancel_consult(numero):
    print("llama a la funcion en cancel_consult")
    update_user_state_especiality(numero, 'CANCEL_CONSULT')
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"Tu consulta ha sido Cancelada ❌ Puedo Agendarte otra cita cuando desees ubicandote en el menú y en la opción Consultas Médicas📍"
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

