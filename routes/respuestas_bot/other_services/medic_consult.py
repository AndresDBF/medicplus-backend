import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_especiality import user_state_especiality
from models.user_state_especiality import user_state_especiality
from models.user_state_register import user_state_register
from models.data_consultas import data_consultas
from routes.user import verify_user, get_user_state_identification, get_user_state_identification_register, update_user_state_especiality, get_user_state_especiality

from datetime import datetime
from sqlalchemy import insert, select

from googletrans import Translator
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
    return result 
    
def get_list_speciality(numero):
    language = verify_language(numero)
    translator = Translator()
    number = 0
    print("el language: ", language)
    with engine.connect() as conn:
        list_consult = conn.execute(data_consultas.select()).fetchall()
    data_list = []
    for consult in list_consult:
        number = number + 1
        name_consult = consult.tip_con.title()
        if language:
            translated_name_consult = translator.translate(name_consult, src='es', dest='en').text
        else:
            translated_name_consult = name_consult
        data_list.append(f"\n{number}. {translated_name_consult}")
        
    print("entra en el mensaje de consultas medicas ")
    if language:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": f"Thank you for choosing our Medical Consultation service 🩻 \nTell me the number of some of our available specialties and in a few minutes I will be able to schedule your appointment 📆. These are our available specialties:\n{''.join(data_list)}"
            }
        }   
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": f"Gracias por escoger nuestro servicio de Consultas Médicas 🩻 \nIndícame el número de algunas de nuestras especialidades disponibles y en breves minutos podré agendar tu cita 📆. Estas son nuestras especialidades disponibles:\n{''.join(data_list)}"
            }
        }   
    
    enviar_mensajes_whatsapp(data)
    update_user_state_especiality(numero, 'WAITING_FOR_SPECIALITY')
    return True

def get_names_especialitys(numero, especialidad):
    language = verify_language(numero)
    result = update_user_state_especiality(numero=numero, state='WAITING_FOR_NAME_ESP', language=language, especialidad=especialidad)
    with engine.connect() as conn:
        especialidad = conn.execute(user_state_especiality.select().where(user_state_especiality.c.numero==numero)
                                    .where(user_state_especiality.c.num_esp==especialidad).order_by(user_state_especiality.c.created_at.asc())).first()
        
    if result == True:
        if language:
            data = {
                    "messaging_product": "whatsapp",
                    "to": numero,
                    "text": {
                        "preview_url": False,
                        "body": f"You have chosen the option: {especialidad.nom_esp.title()} Below I will give you the names of the available specialists, write the number corresponding to which you want to schedule the appointment 📝👨🏼‍⚕️\n1. Doctor 1\n2. Doctor 2\n3. Doctor 3\n4. Doctor 4"
                    }
            } 
        else:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": f"Has escogido la opcion: {especialidad.nom_esp.title()} A continuación te daré los nombres de los especialistas disponibles, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️\n1. Doctor 1\n2. Doctor 2\n3. Doctor 3\n4. Doctor 4"
                }
            }
        enviar_mensajes_whatsapp(data)
        return True
    else:
        if language:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "I didn't understand your answer very well, remember to only use the number corresponding to the specialty that I have proposed to you🤖👨🏻‍💻"
                }
            }
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
    language = verify_language(numero)
    print("entra en save_appointment")
    print("a punto de llamar a la funcion para la variable especiality")
    especiality = update_user_state_especiality(numero=numero, state='WAITING_FOR_CONFIRM', nombre_medico=nombre_medico)
    print("sale de update_user_state_especiality")
    if especiality == True:
        print("entra en el if ")
        with engine.connect() as conn:
            name_esp = conn.execute(user_state_especiality.select().where(user_state_especiality.c.numero==numero).order_by(user_state_especiality.c.created_at.asc())).first()
            print("esto trae name_esp: ", name_esp)     
            name_consult = name_esp.nom_esp.title()       
        if language:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"The total cost of the {name_consult} is {name_esp.precio}$💸\nDo you want to schedule the appointment? \n\nIf you confirm the consultation, I will transfer your request to the person in charge of appointments.\n\nYou can cancel the request by pressing the No❌ button or Return to the top↩️"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmconsult",
                                    "title": "Confirm"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "iddeclineconsult",
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
                        "text": f"El costo total de la {name_consult} es de {name_esp.precio}$💸\n¿Deseas Agendar la cita?  \n\nSi confirmas la consulta, transferiré tu solicitud hacia la persona encargada de citas.\n\nPuedes cancelar la solicitud presionando el boton No❌ o Volver al inicio↩️"
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
        if language:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "I didn't understand your answer very well, remember to only use the number corresponding to the doctors that I have proposed to you🤖👨🏻‍💻"
                }
            }
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

def confirm_consult(numero, name_contact):
    translator = Translator()
    language = verify_language(numero)
    print("llama a la funcion en confirm consult")
    update_user_state_especiality(numero, "CONFIRM_CONSULT")
    if language:
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"Your consultation has been successfully confirmed📝✅ I will schedule your appointment with the selected specialist!"
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
    
    with engine.connect() as conn:
        user_affiliate = conn.execute(usuarios.select().where(usuarios.c.tel_usu==numero)).first()
        user_consult = conn.execute(user_state_especiality.select().where(user_state_especiality.c.numero==numero)).first()
        if language:
            name_especiality = translator.translate(user_consult.nom_esp, src='en', dest='es').text
        else:
            name_especiality = user_consult.nom_esp
        #enviando un mensaje al operador 
        if user_affiliate:
            
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": "584120404049",
                "type": "text",
                "text": {
                        "preview_url": False,
                        "body": f"Hola👋🏼 Soy MedicBot 🤖 asistente virtual de MedicPlus, un nuevo usuario ha agendado una cita para: {name_especiality.title()}☎️ te he seleccionado para cumplir la agenda de su cita. Su nombre de afiliado se encuentra registrado como: {user_affiliate.nom_usu} {user_affiliate.ape_usu} y su número de teléfono es: +{numero} \n\nMuchas gracias por tu tiempo✅ "
                }
            }                
            enviar_mensajes_whatsapp(data)
            return True
        else:

                
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": "584120404049",
                "type": "text",
                "text": {
                        "preview_url": False,
                        "body": f"Hola👋🏼 Soy MedicBot 🤖 asistente virtual de MedicPlus, un nuevo usuario ha agendado una cita para: {name_especiality.title()}☎️ te he seleccionado para cumplir la agenda de su cita. Su nombre de whats app se encuentra registrado como: {name_contact} y su número de teléfono es: +{numero} \n\nMuchas gracias por tu tiempo✅ "
                }
            }
            
            enviar_mensajes_whatsapp(data)
            return True
        
def cancel_consult(numero):
    language = verify_language(numero)
    print("llama a la funcion en cancel_consult")
    update_user_state_especiality(numero, 'CANCEL_CONSULT')
    if language:
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"Your consultation has been Canceled ❌ I can schedule you another appointment whenever you want by locating yourself in the menu and in the Medical Consultations option📍"
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

