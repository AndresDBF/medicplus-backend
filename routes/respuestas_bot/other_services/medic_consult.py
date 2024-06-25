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
        "Authorization": "Bearer EAAOJtyjmw9EBOwEe0P5DH6HMBh1J5jeJbhit9spStB7Nd4UOaffVpAtZBfKhpK6N1LDMZAqvokHUCNGVpGV4jF9YyCKjTtKLgAMWGFKXkmfpn6LqVGpTU5WcrhOpWj0ngwOolUuDval3RlezP5hE1T9HnEdPaYJdAIZCOAn0W1ZAry4qBnFH3PlAIeHZBgia72cPXtafqLtlZCJZALUv0YZD"
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
            "body": "Gracias por escoger nuestro servicio de Consultas Médicas 🩻 \n\nComencemos escogiendo algunas de nuestras especialidades disponibles y en breves minutos podré agendar tu cita📆. Estas son nuestras especialidades disponibles:\n1. Médico General\n2. Pediatría \n3. Traumatología \n4. Neumología \n5. Neurología \n6. Cardiología \nPuedes escribirme el número correspondiente a la especialidad y continuaré con el proceso."
        }
    }   
    enviar_mensajes_whatsapp(data)
    update_user_state_especiality(numero, 'WAITING_FOR_SPECIALITY')
    return True

def get_names_especialitys(numero, especialidad):
    result = update_user_state_especiality(numero, 'WAITING_FOR_NAME_ESP',especialidad)
    if result == True:
        if especialidad == "1":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los médicos generales disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️"
                }
            }   
        elif especialidad == "2":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Pediatría disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️"
                }
            }   
        elif especialidad == "3":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Traumatología disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️"
                }
            }   
        elif especialidad == "4":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Neumología disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️"
                }
            }   
            
        elif especialidad == "5":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Neurología disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️"
                }
            }   
        elif especialidad == "6":
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "text": {
                    "preview_url": False,
                    "body": "A continuación te daré los nombres de los especialistas en Cardiología disponibles que tenemos para tí, escribe el número correspondiente al cuál, deseas agendar la cita 📝👨🏼‍⚕️"
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
                "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente al plan que te he propuesto🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        update_user_state_especiality(numero, "WAITING_FOR_SPECIALITY")
        return True 
        
def save_appointment(numero, nombre_medico):
    especiality = update_user_state_especiality(numero, 'WAITING_FOR_CONFIRM', nombre_medico)
    if especiality == True:
        with engine.connect() as conn:
            name_esp = conn.execute(user_state_especiality.select().where(user_state_especiality.c.numero==numero).order_by(user_state_especiality.c.created_at.asc())).first()
            
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": f"El costo total de la consulta es de 30$💸\n¿Desea Agendar la cita con el especialista en {name_esp.nom_esp}?  \n\nSi confirmas la consulta, transferiré tu solicitud hacia la persona encargada de citas.\n\nPuedes cancelar la solicitud presionando el boton de Volver al inicio↩️"
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
                                "title": "Volver"
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
                "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente al plan que te he propuesto🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        update_user_state_especiality(numero, "WAITING_FOR_NAME_ESP")
        return True 
        