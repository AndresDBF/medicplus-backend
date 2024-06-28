import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from models.user_state_attention import user_state_attention
from models.user_state_register import user_state_register
from models.user_state_especiality import user_state_especiality
from models.user_state_lab import user_state_laboratory
from models.user_state_imaging import user_state_imaging
from models.user_state_ambulance import user_state_ambulance
from routes.user import verify_user, get_user_state_identification_register, get_user_state_register, update_user_state_especiality, update_user_state_lab
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
                "text": "¡Hola!👋🏼 Soy MedicBot🤖, tu asistente virtual de salud. ¿En qué puedo ayudarte hoy? Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud.\n\nDurante el transcurso de tus solicitudes te brindaré variedad de opciones a traves de botones, por lo que no tendrás necesidad de escribir, enviar audios o imagenes en su mayoria. ¡Selecciona una opción para comenzar!"
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
    print("envia el mensaje principal")
    enviar_mensajes_whatsapp(data)
    return True

def get_services(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "A continuación te enseño los servicios que Medic Plus puede ofrecerte 🩺, puedes seleccionar alguno de ellos y a la brevedad te guiaré los pasos que deberás seguir según tu solicitud📌👨🏻‍💻"
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
                            "id": "idtelemed",
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
                "text": "Citas y Pruebas"
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
                            "id": "idimagenologia",
                            "title": "Imagenología"
                        }
                    }
                ]
            }
        }
    }
                
    print("envia el mensaje principal 3")
    enviar_mensajes_whatsapp(data)

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": "Citas y Pruebas"
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
                            "id": "idimagenologia",
                            "title": "Imagenología"
                        }
                    }
                ]
            }
        }
    }

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
                            "id": "idcalloper",
                            "title": "Llamar un Operador"
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
                
    print("envia el mensaje principal 4")
    enviar_mensajes_whatsapp(data)
    return True

def get_plan_service(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "Aun no cuento con esta función, pronto podré ayudarte"
        }
    }
    enviar_mensajes_whatsapp(data)

def return_button(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Gracias por confiar en nuestros servicios de MedicPlus🩺. ¿En que puedo ayudarte nuevamente?📝."
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
    print("envia el mensaje principal 1")
    enviar_mensajes_whatsapp(data)
    with engine.connect() as conn:
        verify_register = conn.execute(select(user_state_register.c.state).select_from(user_state_register).where(user_state_register.c.numero==numero)).scalar()
        verify_ident = conn.execute(select(user_state_attention.c.state).select_from(user_state_attention).where(user_state_attention.c.numero==numero)).scalar()
        verify_consult = conn.execute(select(user_state_especiality.c.state).select_from(user_state_especiality).where(user_state_especiality.c.numero==numero)).scalar()
        verify_lab = conn.execute(select(user_state_laboratory.c.state).select_from(user_state_laboratory).where(user_state_laboratory.c.numero==numero)).scalar()
        verify_imaging = conn.execute(select(user_state_imaging.c.state).select_from(user_state_imaging).where(user_state_imaging.c.numero==numero)).scalar()
        verify_ambulance = conn.execute(select(user_state_ambulance.c.state).select_from(user_state_ambulance).where(user_state_ambulance.c.numero==numero)).scalar()
        if verify_register:
            if verify_register != "REGISTERED":
                print("entra en el if para reiniciar status de registro")
                get_user_state_register(numero,'INIT')
        #la condicion se puede extender a medida que se creen las opciones
        if verify_ident:
            if verify_ident == "WAITING_FOR_ID_TELEMEDICINE" or verify_ident == "WAITING_FOR_ID":
                print("entra en el if para reiniciar status de identidad")
                get_user_state_identification_register(numero,'INIT')
        if verify_consult:
            if verify_consult not in ['CONFIRM_CONSULT', 'CANCEL_CONSULT']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_especiality(numero, 'INIT')
        if verify_lab:
            if verify_lab not in ['CONFIRM_VISIT_LAB', 'CANCEL_VISIT_LAB']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT')
        if verify_imaging:
            if verify_imaging != ['CONFIRM_VISIT_IMAGING']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT')
        if verify_ambulance:
            if verify_ambulance not in ['CONFIRM_AMBULANCE', 'CANCEL_AMBULANCE']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT') 
                
    return True

def cancel_button(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "He cancelado tu solicitud🩺. ¿En que puedo ayudarte nuevamente?📝."
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
    print("envia el mensaje principal 1")
    enviar_mensajes_whatsapp(data)
    #verificamos el status del registro y de la solicitud de cedula 
    with engine.connect() as conn:
        verify_register = conn.execute(select(user_state_register.c.state).select_from(user_state_register).where(user_state_register.c.numero==numero)).scalar()
        verify_ident = conn.execute(select(user_state_attention.c.state).select_from(user_state_attention).where(user_state_attention.c.numero==numero)).scalar()
        verify_consult = conn.execute(select(user_state_especiality.c.state).select_from(user_state_especiality).where(user_state_especiality.c.numero==numero)).scalar()
        verify_lab = conn.execute(select(user_state_laboratory.c.state).select_from(user_state_laboratory).where(user_state_laboratory.c.numero==numero)).scalar()
        verify_imaging = conn.execute(select(user_state_imaging.c.state).select_from(user_state_imaging).where(user_state_imaging.c.numero==numero)).scalar()
        verify_ambulance = conn.execute(select(user_state_ambulance.c.state).select_from(user_state_ambulance).where(user_state_ambulance.c.numero==numero)).scalar()
        if verify_register:
            if verify_register != "REGISTERED":
                print("entra en el if para reiniciar status de registro")
                get_user_state_register(numero,'INIT')
        #la condicion se puede extender a medida que se creen las opciones
        if verify_ident:
            if verify_ident == "WAITING_FOR_ID_TELEMEDICINE" or verify_ident == "WAITING_FOR_ID":
                print("entra en el if para reiniciar status de identidad")
                get_user_state_identification_register(numero,'INIT')
        if verify_consult:
            if verify_consult not in ['CONFIRM_CONSULT', 'CANCEL_CONSULT']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_especiality(numero, 'INIT')
        if verify_lab:
            if verify_lab not in ['CONFIRM_VISIT_LAB', 'CANCEL_VISIT_LAB']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT')
        if verify_imaging:
            if verify_imaging != ['CONFIRM_VISIT_IMAGING']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT')
        if verify_ambulance:
            if verify_ambulance not in ['CONFIRM_AMBULANCE', 'CANCEL_AMBULANCE']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT') 
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

def decline_action(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "He cancelado tu proceso🩺. ¿En que puedo ayudarte nuevamente?📝."
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
    #verificamos el status del registro y de la solicitud de cedula 
    with engine.connect() as conn:
        verify_register = conn.execute(select(user_state_register.c.state).select_from(user_state_register).where(user_state_register.c.numero==numero)).scalar()
        verify_ident = conn.execute(select(user_state_attention.c.state).select_from(user_state_attention).where(user_state_attention.c.numero==numero)).scalar()
        verify_consult = conn.execute(select(user_state_especiality.c.state).select_from(user_state_especiality).where(user_state_especiality.c.numero==numero)).scalar()
        verify_lab = conn.execute(select(user_state_laboratory.c.state).select_from(user_state_laboratory).where(user_state_laboratory.c.numero==numero)).scalar()
        verify_imaging = conn.execute(select(user_state_imaging.c.state).select_from(user_state_imaging).where(user_state_imaging.c.numero==numero)).scalar()
        verify_ambulance = conn.execute(select(user_state_ambulance.c.state).select_from(user_state_ambulance).where(user_state_ambulance.c.numero==numero)).scalar()
        if verify_register:
            if verify_register != "REGISTERED":
                print("entra en el if para reiniciar status de registro")
                get_user_state_register(numero,'INIT')
        #la condicion se puede extender a medida que se creen las opciones
        if verify_ident:
            if verify_ident == "WAITING_FOR_ID_TELEMEDICINE" or verify_ident == "WAITING_FOR_ID":
                print("entra en el if para reiniciar status de identidad")
                get_user_state_identification_register(numero,'INIT')
        if verify_consult:
            if verify_consult not in ['CONFIRM_CONSULT', 'CANCEL_CONSULT']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_especiality(numero, 'INIT')
        if verify_lab:
            if verify_lab not in ['CONFIRM_VISIT_LAB', 'CANCEL_VISIT_LAB']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT')
        if verify_imaging:
            if verify_imaging != ['CONFIRM_VISIT_IMAGING']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT')
        if verify_ambulance:
            if verify_ambulance not in ['CONFIRM_AMBULANCE', 'CANCEL_AMBULANCE']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT') 
    return True

def goodbye_message(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "preview_url": False,
            "body": "Ha sido un placer ofrecerte mi ayuda 🤖, en MedicPlus cumplimos por velar el bienestar de nuestros Afiliados👨🏼‍⚕️☑️  puedes contactar conmigo cuando desees 📲 y con gusto serás atendido👨🏻‍💻"
        }
    }    
    print("envia el mensaje principal")
    enviar_mensajes_whatsapp(data)
    with engine.connect() as conn:
        verify_register = conn.execute(select(user_state_register.c.state).select_from(user_state_register).where(user_state_register.c.numero==numero)).scalar()
        verify_ident = conn.execute(select(user_state_attention.c.state).select_from(user_state_attention).where(user_state_attention.c.numero==numero)).scalar()
        verify_consult = conn.execute(select(user_state_especiality.c.state).select_from(user_state_especiality).where(user_state_especiality.c.numero==numero)).scalar()
        verify_lab = conn.execute(select(user_state_laboratory.c.state).select_from(user_state_laboratory).where(user_state_laboratory.c.numero==numero)).scalar()
        verify_imaging = conn.execute(select(user_state_imaging.c.state).select_from(user_state_imaging).where(user_state_imaging.c.numero==numero)).scalar()
        verify_ambulance = conn.execute(select(user_state_ambulance.c.state).select_from(user_state_ambulance).where(user_state_ambulance.c.numero==numero)).scalar()
        if verify_register:
            if verify_register != "REGISTERED":
                print("entra en el if para reiniciar status de registro")
                get_user_state_register(numero,'INIT')
        #la condicion se puede extender a medida que se creen las opciones
        if verify_ident:
            if verify_ident == "WAITING_FOR_ID_TELEMEDICINE" or verify_ident == "WAITING_FOR_ID":
                print("entra en el if para reiniciar status de identidad")
                get_user_state_identification_register(numero,'INIT')
        if verify_consult:
            if verify_consult not in ['CONFIRM_CONSULT', 'CANCEL_CONSULT']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_especiality(numero, 'INIT')
        if verify_lab:
            if verify_lab not in ['CONFIRM_VISIT_LAB', 'CANCEL_VISIT_LAB']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT')
        if verify_imaging:
            if verify_imaging != ['CONFIRM_VISIT_IMAGING']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT')
        if verify_ambulance:
            if verify_ambulance not in ['CONFIRM_AMBULANCE', 'CANCEL_AMBULANCE']:
                print("entra en el if para reiniciar status de consulta")
                update_user_state_lab(numero, 'INIT') 
    return True

