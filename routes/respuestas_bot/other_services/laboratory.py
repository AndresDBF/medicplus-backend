import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_lab import user_state_laboratory
from routes.user import get_user_state_lab, update_user_state_lab

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
 
def get_service_lab(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "preview_url": False,
            "body": "Selecciona el número correspondiente a la prueba que deseas adquirir🧬💉\n1. Prueba de Sangre.\n2. Prueba de Orina\n3. Prueba de Eces.\n4. Prueba de COVID-19.\n5. Placa de Torax\n6. Imagenologia."
        }
    }   
    enviar_mensajes_whatsapp(data)
    update_user_state_lab(numero, 'WAITING_FOR_TEST')
    return True

def send_service_location(numero, test):
    result = update_user_state_lab(numero, 'WAITING_FOR_LOCATION', test)
    if result == True:
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
                                "id": "idconfirmdomi",
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
        update_user_state_lab(numero, "WAITING_FOR_TEST")
        return True 

def select_service_lab(numero, texto):
    if texto == "idconfirmdomi":
        update_user_state_lab(numero=numero, state='WAITING_FOR_CONFIRM_LAB', confirm_domi=True)
    
        with engine.connect() as conn:
            test = conn.execute(select(user_state_laboratory.c.test).select_from(user_state_laboratory).where(user_state_laboratory.c.numero==numero)
                                .order_by(user_state_laboratory.c.created_at.asc())).scalar()
        
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"La {test.test} tiene un costo de 30$💸 , ¿Deseas agendar la visita al laboratorio💉? Tu confirmación la agendaré al personal para indicarle disponibilidad📝 "
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
        data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"La {test.test} tiene un costo de 30$ junto con una recarga de 10$ del domicilio 💸, ¿Deseas confirmar el traslado del equipo médico💉?"
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
    update_user_state_lab(numero=numero, state="CONFIRM_VISIT_LAB")
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"He programado tu visita al laboratorio y he contactado con el personal de cita. Pronto te indicarán la disponibilidad de tu solicitud📢📝"
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
#para la confirmacion en caso de pedir el domicilio 
def confirm_domiciliary_lab(numero):
    update_user_state_lab(numero=numero, state="CONFIRM_DOMICILIARY_LAB")
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"He notificado al personal de citas sobre tu solicitud📢📝, pronto serás contactado por uno de ellos para realizar el proceso de cobro"
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

#para la cancelacion en caso de visitar el lugar
def cancel_visit_lab(numero):
    update_user_state_lab(numero, 'CANCEL_VISIT_LAB')
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"Tu visita ha sido Cancelada ❌ Puedo Agendarte otra visita a nuestros laboratorios cuando desees ubicandote en el menú y en la opción Laboratorio📍"
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


#cancelar en caso de pedir el domicilio 
def cancel_domiciliary_lab(numero):
    update_user_state_lab(numero, 'CANCEL_DOMICILIARY_LAB')
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": f"Tu domicilio ha sido Cancelado ❌ Puedo Agendarte otra prueba a nuestros laboratorios cuando desees ubicandote en el menú y en la opción Laboratorio📍"
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
