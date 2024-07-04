import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_lab import user_state_laboratory
from models.user_state_imaging import user_state_imaging
from models.user_state_register import user_state_register

from models.data_imagenologia import data_imagenologia
from routes.user import get_user_state_imaging, update_user_state_imaging

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
        print(f"-----------------el result del traductor {result}----------------------------")
    return result 



#realizar la correccion de imagenologia a que se parezca a laboratorios
def get_eco_or_rx(numero):
    language = verify_language(numero)
    translator = Translator()
    number = 0
    
    with engine.connect() as conn:
        list_imag = conn.execute(text("select distinct tip_con from data_imagenologia;")).fetchall()
        print("esto muestra el list imag ", list_imag)
    # Crear un diccionario de mapeo de números a tipos de servicios exactos
    service_map = {}
    data_list = []
    for imag in list_imag:
        number += 1
        service_map[number] = imag.tip_con  # Mapear número a nombre exacto del servicio
        if language:
            tranlated_text = translator.translate(imag.tip_con, src='es', dest='en').text
        else:
            tranlated_text = imag.tip_con
        data_list.append(f"\n{number}. {tranlated_text.title()}")
    if language:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": f"MedicPlus has Imaging services such as: \n{''.join(data_list)} \n\nSelect one of them🩻"
            }
        } 
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": f"MedicPlus cuenta con servicios de Imagenología tales como: \n{''.join(data_list)} \n\nSelecciona una de ellas🩻"
            }
        } 
        
    enviar_mensajes_whatsapp(data)
    update_user_state_imaging(numero, 'WAITING_FOR_IMAGING')
    return True

def send_tip_imaging(numero, texto):
    number = 0
    language = verify_language(numero)
    translator = Translator()
    with engine.connect() as conn:
        list_imag = conn.execute(text("select distinct tip_con from data_imagenologia;")).fetchall()
        print("esto muestra el list imag ", list_imag)
    # Crear un diccionario de mapeo de números a tipos de servicios exactos
    service_map = {}
    data_list = []
    for imag in list_imag:
        number += 1
        service_map[number] = imag.tip_con  # Mapear número a nombre exacto del servicio
        if language:
            tranlated_text = translator.translate(imag.tip_con, src='es', dest='en').text
        else:
            tranlated_text = imag.tip_con
        data_list.append(f"\n{number}. {tranlated_text.title()}")
    selected_service = service_map[int(texto)]
    if selected_service is None:
        if language:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "I didn't understand your answer very well, remember to only use the number corresponding to the options that I have proposed🤖👨🏻‍💻"
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
                    "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente a las opciones que tehe propuesto🤖👨🏻‍💻"
                }
            }
            
        enviar_mensajes_whatsapp(data)
        return True
    else:
        with engine.connect() as conn:
            list_imag_selected = conn.execute(text(f"select * from data_imagenologia where tip_con='{selected_service}'")).fetchall()
        for imag in list_imag_selected:
            number += 1
            service_map[number] = imag.tip_con  # Mapear número a nombre exacto del servicio
            if language:
                tranlated_text = translator.translate(imag.tip_con, src='es', dest='en').text
            else:
                tranlated_text = imag.tip_con
            data_list.append(f"\n{number}. {tranlated_text.title()}")
        if language:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": f"You can provide more information about our {selected_service} studies🩻, Write the specific study you want and I will search the system for the available options 👨🏻‍💻"
                }
            }  
            tranlated_selected_service = translator.translate(selected_service, src='en', dest='es').text    
        else:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": f"Puedo proporcionarte mas información sobre nuestros estudios de {selected_service}🩻, Escribe el estudio especifico que deseas y buscaré en sistema las opciones disponibles 👨🏻‍💻"
                }
            }  
            tranlated_selected_service = selected_service
        enviar_mensajes_whatsapp(data)
        update_user_state_imaging(numero, 'WAITING_FOR_SEND_IMAGING', opcion=tranlated_selected_service)
        return True
      
def verify_imaging(numero, texto):
    translator = Translator()
    language = verify_language(numero)
    
    if language:
        translated_resp = translator.translate(texto, src='en', dest='es').text
    else:
        translated_resp = texto
    # Crear un diccionario de mapeo de números a tipos de servicios exactos
    print("el translated_resp: ", translated_resp)
    with engine.connect() as conn:
        selected_service =  conn.execute(user_state_imaging.select().where(user_state_imaging.c.numero==numero)).first()
        list_study = conn.execute(text(f"select * from data_imagenologia where des_pru like '%{translated_resp}%' and tip_con='{selected_service.opcion}'")).fetchall()
    print("el selected_service: ", selected_service)
    print("el list_study: ", list_study)
    if len(list_study) < 1:
        print("entra en el if de if len(list_study) < 1:")
        if language:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": "I have not been able to get the study that you indicate in the system❌ you can indicate another study that you want or go back to the beginning ↩️"
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
                        "text": "No he logrado conseguir en sistema el estudio que me indicas❌ puedes volver a indicarme otro estudio que desees o volver al inicio ↩️"
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
        return True
    else:
        print("llega al else")
        number = 0
        service_map = {}
        data_list = []
        for study in list_study:
            number += 1
            service_map[number] = study.des_pru  
            if language:
                translated_des_pru = translator.translate(study.des_pru, src='es', dest='en').text
            else:
                translated_des_pru = study.des_pru
            data_list.append(f"\n{number}. {translated_des_pru.title()}. {study.pre_pru}$💵")
        
        if language:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": f"I have found the {selected_service.opcion} study you need in the system 👨🏻‍💻 below I show you the names and prices available: \n{''.join(data_list)} \n\nSelect one of them💉"
                }
            }
        else:
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": f"He encontrado el estudio de {selected_service.opcion} que necesitas en sistema 👨🏻‍💻 a continuación te muestro los nombres y precios disponibles: \n{''.join(data_list)} \n\nAl especificarme💉"
                }
            }
        
        enviar_mensajes_whatsapp(data)
        update_user_state_imaging(numero, 'WAITING_FOR_SELECT_IMAGING', language=language, test=texto)
        return True
    
def question_visit_lab(numero, texto):
    
    translator = Translator()
    language = verify_language(numero)
    result = update_user_state_imaging(numero, 'CONFIRM_VISIT_IMAGING', language=language, test=texto)
    if result == True:
        with engine.connect() as conn:
            test = conn.execute(user_state_imaging.select().where(user_state_imaging.c.numero==numero)
                                .where(user_state_imaging.c.opcion==texto).order_by(user_state_imaging.c.created_at.asc())).first()
            if language:
                translate_resp = translator.translate(test.nombre, src='en', dest='es').text
                name_test = conn.execute(text(f"select distinct tip_con from data_imagenologia where tip_con='{translate_resp}'")).scalar()
                trans_name_test = translator.translate(name_test, src='es', dest='en').text
                min_price = conn.execute(text(f"select min(pre_pru) from data_imagenologia where tip_con='{translate_resp}'")).scalar()
                max_price = conn.execute(text(f"select max(pre_pru) from data_imagenologia where tip_con='{translate_resp}'")).scalar()
            else:
                
                name_test = conn.execute(text(f"select distinct tip_con from data_imagenologia where tip_con='{test.nombre}'")).scalar()
                trans_name_test = name_test
                min_price = conn.execute(text(f"select min(pre_pru) from data_imagenologia where tip_con='{test.nombre}'")).scalar()
                max_price = conn.execute(text(f"select max(pre_pru) from data_imagenologia where tip_con='{test.nombre}'")).scalar()
        print("el name_test: ", name_test) 
        print("el min_price: ", min_price)
        print("el max_price: ", max_price)
        if language:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"The {trans_name_test.title()} test has a minimum cost of {min_price}$ and a maximum of {max_price}$💸 \n When scheduling the visit, I will put you in contact with the staff in charge where you can specify the type of test you need📞 Do you want to schedule a visit to our laboratory?"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmvisitimag",
                                    "title": "Schedule Visit"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idcancelvisitimag",
                                    "title": "Cancel Visit"
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
                        "text": f"La prueba de {trans_name_test.title()} tiene un costo minimo de {min_price}$ y un maximo de {max_price}$💸 \n Al agendar la visita, te pondria en contacto con el personal encargado donde podrás especificarle el tipo de prueba que necesitas📞¿Desea agendar la visita a nuestro laboratorio?"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmvisitimag",
                                    "title": "Agendar Visita"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idcancelvisitimag",
                                    "title": "Cancelar Visita"
                                }
                            },
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
        update_user_state_imaging(numero, "WAITING_FOR_IMAGING")
        return True 
    
def confirm_visit_imag(numero):
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
                    "text": f"I have notified the appointment staff about your request📢📝, you will be contacted by one of them soon📞"
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
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"He notificado al personal de citas sobre tu solicitud📢📝, pronto serás contactado por uno de ellos📞"
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
    return True

def cancel_test(numero):
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
                    "text": f"Your visit has been Canceled❌ I can schedule another visit to our laboratories whenever you want by locating yourself in the menu and in the Imaging option📍"
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
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"Tu visita ha sido Cancelada❌ Puedo Agendarte otra visita a nuestros laboratorios cuando desees ubicandote en el menú y en la opción Imagenología📍"
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
    return True























































