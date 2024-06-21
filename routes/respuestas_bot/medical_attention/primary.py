
import json
import http
from database.connection import engine
from models.usuarios import usuarios
from models.log import log
from routes.user import get_user_state, get_user_state_register
from routes.user import verify_user
from datetime import datetime
from sqlalchemy import insert, select


def agregar_mensajes_log(texto):
    try:
        texto_str = json.dumps(texto)
        print("asi queda el texto antes de insertar en el log: ", texto_str)
        print("y este es el tipo de dato: ", type(texto_str))
        with engine.connect() as conn:
            conn.execute(log.insert().values(texto=texto_str, fecha_y_hora=datetime.utcnow()))
            conn.commit()
        print("Mensaje guardado en el log:", texto)
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
        print("se enviaron los mensajes")
        print("este fue el response al enviar el mensaje: ", response.status, response.reason, response_data)
        if response.status != 200:
            agregar_mensajes_log(f"Error al enviar mensaje: {response.status} {response.reason} {response_data}")
    except Exception as e:
        print(f"Exception: {e}")
        agregar_mensajes_log(f"Exception al enviar mensaje: {e}")
    finally:
        connection.close()
        
def get_info_primary_attention(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": "¿Desea Generar una Alarma para ser llamado?📞 \nsi seleccionas Si☑️ en minutos recibirias una llamadas de uno de nuestros operadores disponibles \nSi seleccionas No❌ daremos por cancelada tu petición. \nPuedes volver a la pantalla principal Presionando el botón Volver al inicio↩️.  "
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "llamar",
                            "title": "Sí"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "nollamar",
                            "title": "No"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "volver",
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

def confirm_call(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive":{
            "type": "button",
            "body": {
                "text": "La alarma ha sido Generada 📢 recibirá una llamada en los proximos minutos📞⌚"
            },
            "action": {
                "buttons":[
                    {
                        "type": "reply",
                        "reply": {
                            "id": "volver",
                            "title": "Volver al inicio"
                        }
                    },
                ]
            }
        }
    }
    enviar_mensajes_whatsapp(data)
    return True