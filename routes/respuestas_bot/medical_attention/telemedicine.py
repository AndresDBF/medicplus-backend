import json
import http
from database.connection import engine
from models.log import log
from routes.user import verify_user
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
        
    
def get_info_telemedicine_attention(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": "¿Desea Generar una Alarma para ser llamado?📞 \n\nsi seleccionas Si☑️ en minutos recibirias una llamada de uno de nuestros operadores disponibles, con el de cubrir tu atención de telemedicina📞👨🏼‍⚕️ \n\nSi seleccionas No❌ daremos por cancelada tu petición. \n\nPuedes volver a la pantalla principal Presionando el botón Volver al inicio↩️.  "
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



def cancel_telemedicine(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "He cancelado tu solicitud de telemedicina🗑 ¿Deseas alguna otra ayuda?🤖"
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
                            "title": "Primaria"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "telemed",
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
                "text": "Otros Servicios."
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "conmed",
                            "title": "Consultas Médicas"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "labori",
                            "title": "Laboratorio"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "ambula",
                            "title": "Ambulancia"
                        }
                    },
                ]
            }
        }
    }
        
    print("envia el mensaje principal 3")
    enviar_mensajes_whatsapp(data)
    return True






