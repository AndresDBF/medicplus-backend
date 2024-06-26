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
        "Authorization": "Bearer EAAOJtyjmw9EBO6uqJ5DXrNx0Ead4zZBAYLWw9KJ5JbRY8MiaYNj7wQmctyt3C5FzosjRnikFQbmU4ajsJ46HlbXygDodryt1i8Qp4zfEd4rPRMFwXpzZBBUdFE79YA9yD9qT70i6I2FFbyyEP1hKOCa6yeBZCzYJdm7Ea3I56sMGZCKbqsvIFrOvSX1cVmyjZAu7zsxhd72E6oYZC3CAWw8gZDZD"
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
            "body": "Por favor selecciona dentro de estas opciones el número correspondiente a la prueba que deseas realizarte🧬💉\n1. Prueba de Sangre.\n2. Prueba de Orina\n3. Prueba de Eces.\n4. Prueba de COVID-19.\n5. Placa de Torax\n6. Imagenologia."
        }
    }   
    enviar_mensajes_whatsapp(data)
    return True
    