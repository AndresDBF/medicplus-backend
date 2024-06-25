import json
import http
from database.connection import engine
from models.log import log
from models.usuarios import usuarios
from routes.user import verify_user, get_user_state_identification, get_user_state_identification_register, update_user_state_especiality

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
        "Authorization": "Bearer EAAOJtyjmw9EBO8SQ5fR7Ej3tmTTRZBoAO5y8RCXIQHiVXSrZA5Nm5EEGY22hEBSC1NOfIWsZAiQzhkN1bU2sjDhViEK19ZCPahNWirvCnwpX2TeysE7HR25FgZAazbEMiOIfwmxXDTdRTHdK5M2o7tSDjzxEkNXsGloOdiZAcXBr8K3HTWlLjvRoCfZC9FWBoFIvYiRPQLTwyfr1G2S1LkZD"
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
    
def get_list_especiality(numero):
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