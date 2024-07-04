import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_lab import user_state_laboratory
from models.user_state_register import user_state_register
from routes.user import get_user_state_lab, update_user_state_lab

from datetime import datetime
from sqlalchemy import insert, select, text

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

def get_service_lab(numero):
    language = verify_language(numero)
    if language:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "I can help you in providing necessary information about the laboratory tests that we can offer at MedicPlus 👨🏼‍⚕️write to me what type of test you want to perform with your specific name🧬💉 I will do my job in searching the system and I will tell you if I have the test that you need. you need👨🏻‍💻."
            }
        }  
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Puedo ayudarte en brindar información necesaria de las pruebas de laboratorio que podemos ofrecer en MedicPlus 👨🏼‍⚕️escribeme que tipo de prueba deseas realizarte con su nombre específico🧬💉 Cumpliré con mi trabajo en buscar en sistema y te diré si dispongo de la prueba que necesitas👨🏻‍💻."
            }
        }  
         
    enviar_mensajes_whatsapp(data)
    update_user_state_lab(numero, 'WAITING_FOR_TEST')
    return True


def get_list_service_lab(numero, texto):
    language = verify_language(numero)
    translator = Translator()
    if language:
        translated_resp = translator.translate(texto, src='en', dest='es').text
    else:
        translated_resp = texto
    # Crear un diccionario de mapeo de números a tipos de servicios exactos
    with engine.connect() as conn:
        list_tests = conn.execute(text(f"select * from data_laboratorios where tip_pru like '%{translated_resp}%'")).fetchall()
    
    if len(list_tests) < 1:
        if language:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": "I have not been able to get the test that you indicate in the system❌ you can indicate another test that you want or go back to the beginning ↩️"
                    },
                    "action": {
                        "buttons": [
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
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": "No he logrado conseguir en sistema la prueba que me indicas❌ puedes volver a indicarme otra prueba que desees o volver al inicio ↩️"
                    },
                    "action": {
                        "buttons": [
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
        update_user_state_lab(numero, 'WAITING_FOR_TEST')
        return True
    else:
        number = 0
        service_map = {}
        data_list = []
        for test in list_tests:
            number += 1
            service_map[number] = test.tip_pru  
            if language:
                translated_tip_pru = translator.translate(test.tip_pru, src='es', dest='en').text
            else:
                translated_tip_pru = test.tip_pru
            data_list.append(f"\n{number}. {translated_tip_pru.title()}: {test.pre_pru}$")
        
        if language:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": f"I have found the test you need in the system 👨🏻‍💻 below I show you the names and prices available: \n{''.join(data_list)} \n\nSelect one of them💉"
                }
            }
        else:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": f"He encontrado la prueba que necesitas en sistema 👨🏻‍💻 a continuación te muestro los nombres y precios disponibles: \n{''.join(data_list)} \n\nSelecciona una de ellas💉"
                }
            }
        
        enviar_mensajes_whatsapp(data)
        update_user_state_lab(numero, 'WAITING_FOR_SELECT_TEST', test=texto)
        return True

def send_service_location(numero, texto):
    language = verify_language(numero)
    result = update_user_state_lab(numero, 'WAITING_FOR_LOCATION', language=language, opcion=texto)
    if result == True:
        if language:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"MedicPlus has a home service for the implementation of laboratory tests, so a trained medical team will carry out the work from the comfort of your home 🏠👨🏼‍⚕️Do you want to request a home or would you prefer to visit our laboratory?"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmdomilab",
                                    "title": "Request Address"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idvisitlab",
                                    "title": "Visit Laboratory"
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
                        "text": f"MedicPlus cuenta con servicio domiciliario para la implementación de pruebas de laboratorios, por lo que un equipo médico capacitado realizará el trabajo desde la comodidad de tu casa 🏠👨🏼‍⚕️¿Deseas solicitar un domicilio o prefieres visitar nuestro laboratorio?."
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmdomilab",
                                    "title": "Pedir Domicilio"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idvisitlab",
                                    "title": "Visitar Laboratorio"
                                }
                            }
                        ]
                    }
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
                    "body": "I didn't understand your answer very well, remember to only use the number corresponding to the options that I have proposed to you🤖👨🏻‍💻"
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
                    "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente a las opciones que te he propuesto🤖👨🏻‍💻"
                }
            }
            
        enviar_mensajes_whatsapp(data)
        print("a punto de llamar a la funcion en el else de respuesta incorrecta")
        update_user_state_lab(numero, "WAITING_FOR_SELECT_TEST")
        return True 

def select_service_lab(numero, texto):
    language = verify_language(numero)
    with engine.connect() as conn:
            test = conn.execute(select(user_state_laboratory.c.opcion, user_state_laboratory.c.precio)
                                .select_from(user_state_laboratory).where(user_state_laboratory.c.numero==numero)
                                .order_by(user_state_laboratory.c.created_at.asc())).first()
    if texto == "idvisitlab":
        print("entra en el if de selec service lab")
        update_user_state_lab(numero=numero, state='WAITING_FOR_CONFIRM_LAB', confirm_domi=False)
        if language:
            
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"The {test.opcion} test has a cost of {test.precio}$💸. Do you want to schedule a visit to the laboratory💉? I will schedule your confirmation to the staff to indicate availability📝 "
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmvisit",
                                    "title": "Confirm Visit"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idcancelvisit",
                                    "title": "Cancel Visit"
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
                        "text": f"La prueba de {test.opcion} tiene un costo de {test.precio}$💸 , ¿Deseas agendar la visita al laboratorio💉? Tu confirmación la agendaré al personal para indicarle disponibilidad📝 "
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmvisit",
                                    "title": "Confirmar Visita"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idcancelvisit",
                                    "title": "Cancelar Visita"
                                }
                            }
                        ]
                    }
                }
            }  
            
        enviar_mensajes_whatsapp(data)
        return True
    else:
        update_user_state_lab(numero=numero, state='WAITING_FOR_CONFIRM_LAB', confirm_domi=True)
        print("entra en el else de selec service lab")
        if language:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"The {test.opcion} test has a cost of {test.precio}$💸 with an additional cost of the address 💸, I will contact the appointment staff who can provide you with more information about it once you accept the request. Do you want to confirm the transfer of the medical team💉?"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmequip",
                                    "title": "Confirm"
                                    }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idcancelequip",
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
                        "text": f"La prueba de {test.opcion} tiene un costo de {test.precio}$💸 con un costo adicional del domicilio 💸, contactaré con el personal de citas quien te podrá brindar mas informacion al respecto una vez aceptes la solicitud. ¿Deseas confirmar el traslado del equipo médico💉?"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmequip",
                                    "title": "Confirmar"
                                    }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idcancelequip",
                                    "title": "Cancelar"
                                }
                            }
                        ]
                    }
                }
            } 
            
        enviar_mensajes_whatsapp(data)
        return True
     

#para la confirmacion en caso de visitar el lugar 
def confirm_visit_lab(numero):
    language = verify_language(numero)
    update_user_state_lab(numero=numero, state="CONFIRM_VISIT_LAB")
    
    if language:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"I have scheduled your visit to the laboratory and have contacted the appointment staff. They will soon indicate the availability of your request📢📝\n\nDo you want to look for another test?💉"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idbuscarprueba",
                                "title": "Search Test"
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
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"He programado tu visita al laboratorio y he contactado con el personal de cita. Pronto te indicarán la disponibilidad de tu solicitud📢📝\n\n¿Deseas buscar alguna otra prueba?💉"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idbuscarprueba",
                                "title": "Buscar Prueba"
                            }
                        }, 
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
#para la confirmacion en caso de pedir el domicilio 
def confirm_domiciliary_lab(numero):
    language = verify_language(numero)
    update_user_state_lab(numero=numero, state="CONFIRM_DOMICILIARY_LAB")
    if language:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"I have notified the appointment staff about your request📢📝, you will soon be contacted by one of them to carry out the collection process\n\nDo you want to look for another test?💉"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idbuscarprueba",
                                "title": "Search Test"
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
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"He notificado al personal de citas sobre tu solicitud📢📝, pronto serás contactado por uno de ellos para realizar el proceso de cobro.\n\n¿Deseas buscar alguna otra prueba?💉"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idbuscarprueba",
                                "title": "Buscar Prueba"
                            }
                        }, 
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

#para la cancelacion en caso de visitar el lugar
def cancel_visit_lab(numero):
    language = verify_language(numero)
    update_user_state_lab(numero, 'CANCEL_VISIT_LAB')
    if language:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"Your visit has been Canceled ❌ I can schedule you another visit to our laboratories whenever you want by locating yourself in the menu and in the Laboratory option 📍\n\nDo you want to look for another test?💉"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idbuscarprueba",
                                "title": "Search Test"
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
                    "text": f"Tu visita ha sido Cancelada ❌ Puedo Agendarte otra visita a nuestros laboratorios cuando desees ubicandote en el menú y en la opción Laboratorio📍\n\n¿Deseas buscar alguna otra prueba?💉"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idbuscarprueba",
                                "title": "Buscar Prueba"
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
    enviar_mensajes_whatsapp(data)
    return True


#cancelar en caso de pedir el domicilio 
def cancel_domiciliary_lab(numero):
    language = verify_language(numero)
    update_user_state_lab(numero, 'CANCEL_DOMICILIARY_LAB')
    if language:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"Your address has been Canceled ❌ I can schedule another test for you at our laboratories whenever you want by locating yourself in the menu and in the Laboratory option 📍\n\nDo you want to look for another test?💉"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idbuscarprueba",
                                "title": "Search Test"
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
                    "text": f"Tu domicilio ha sido Cancelado ❌ Puedo Agendarte otra prueba a nuestros laboratorios cuando desees ubicandote en el menú y en la opción Laboratorio📍\n\n¿Deseas buscar alguna otra prueba?💉"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idbuscarprueba",
                                "title": "Buscar Prueba"
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
             
    enviar_mensajes_whatsapp(data)
    return True
