import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_lab import user_state_laboratory
from models.user_state_imaging import user_state_imaging

from models.data_imagenologia import data_imagenologia
from routes.user import get_user_state_imaging, update_user_state_imaging

from datetime import datetime
from sqlalchemy import insert, select, text


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
 
 
def get_eco_or_rx(numero):
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
        data_list.append(f"\n{number}. {imag.tip_con.title()}")
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
    
def verify_imaging(numero, texto):
    result = update_user_state_imaging(numero, 'CONFIRM_VISIT_IMAGING', test=texto)
    if result == True:
        with engine.connect() as conn:
            test = conn.execute(user_state_imaging.select().where(user_state_imaging.c.numero==numero)
                                .where(user_state_imaging.c.opcion==texto).order_by(user_state_imaging.c.created_at.asc())).first()
            name_test = conn.execute(text(f"select distinct tip_con from data_imagenologia where tip_con='{test.nombre}'")).scalar()
            min_price = conn.execute(text(f"select min(pre_pru) from data_imagenologia where tip_con='{test.nombre}'")).scalar()
            max_price = conn.execute(text(f"select max(pre_pru) from data_imagenologia where tip_con='{test.nombre}'")).scalar()
        print("el name_test: ", name_test) 
        print("el min_price: ", min_price)
        print("el max_price: ", max_price)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"La prueba de {name_test} tiene un costo minimo de {min_price}$ y un maximo de {max_price}$💸 \n Al agendar la visita, te pondria en contacto con el personal encargado donde podrás especificarle el tipo de prueba que necesitas📞¿Desea agendar la visita a nuestro laboratorio?"
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