from database.connection import engine
from models.roles import roles
from models.usuarios import usuarios
from models.user_roles import user_roles
from models.user_state_register import user_state_register

from sqlalchemy import select, insert, update

def get_user_state(numero):
    with engine.connect() as conn:
        print("entra en get_user_state")
        result = conn.execute(select(user_state_register).where(user_state_register.c.numero == numero)).fetchone()
        print("esto trae el result: ", result)
        if result is not None:
            # Asumiendo que result tiene los campos en este orden: numero, state, nombre, apellido, cedula, email, fecha_y_hora
            columns = ["numero", "state", "nombre", "apellido", "cedula", "email", "fecha_y_hora"]
            result_dict = dict(zip(columns, result))
            result_dict["consult"] = True
            return result_dict
        else:
            return {"consult": None}

def get_user_state_register(numero, state, nombre=None, apellido=None, cedula=None, email=None):
    with engine.connect() as conn:
        print("entra en get_user_state_register")
        result = get_user_state(numero)
        if result["consult"] is not None:
            print("entra en el if para actualizar")
            if nombre:
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, nombre=nombre)
                )
                conn.commit()
            if apellido:
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, apellido=apellido)
                )
                conn.commit()
            if cedula:
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, cedula=cedula)
                )
                conn.commit()
            if email:
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state, email=email)
                )
                conn.commit()
            else:
                conn.execute(
                    update(user_state_register)
                    .where(user_state_register.c.numero == numero)
                    .values(state=state)
                )
                conn.commit()
            print("actualizo los campos")
        else:
            print("entra en el else para insertar")
            conn.execute(user_state_register.insert().values(numero=numero, state=state))
            conn.commit()
            print("se inserto la fila")

def verify_user(numero):
    with engine.connect() as conn:
        print("entra en verify_user")
        user = conn.execute(usuarios.select().where(usuarios.c.tel_usu==numero)).first()
        print("esto trae el user: ", user)
    if user is not None:
        print("entra en el if del verify_user")
        texto = f"Hola {user.nom_usu} {user.ape_usu}👋🏼 ¿En que puedo ayudarte hoy?📝."
        return {
            "text": texto,
            "registered": True
        }
    else:
        print("entra en el else del verify_user")
        texto = f"Lo siento, no te he encontrado en sistema como usuario afiliado🚫, deseas formar parte de Afiliados en Medic Plus?👨🏼‍⚕️ Registraremos tus datos paso a paso📝"
        return {
            "text": texto,
            "registered": False
        }
    
""" 
 
 def recibir_mensajes(req):
    print("el req: ", req)
    try:
        req_data = request.get_json()
        print("Datos JSON recibidos:", req_data)
        
        for entry in req_data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                for message in messages:
                    numero = message.get('from')
                    user = user_create_state(numero)
                    
                    if user.state == 'INIT':
                        if 'text' in message:
                            texto = message['text']['body'].lower()
                            if texto in ['hola', 'buenas', 'buenos', 'que tal']:
                                enviar_mensajes_interactivo(numero)
                                update_user_state(numero, 'WAITING_FOR_CEDULA')
                                
                    elif user.state == 'WAITING_FOR_CEDULA':
                        if 'text' in message:
                            cedula = message['text']['body']
                            # Aquí puedes agregar la lógica para verificar la cédula en tu base de datos
                            # Ejemplo de verificación de cédula:
                            if verificar_cedula(cedula):
                                enviar_mensaje(numero, "Cédula verificada correctamente.")
                                update_user_state(numero, 'VERIFIED', cedula)
                            else:
                                enviar_mensaje(numero, "Cédula no encontrada. Inténtalo de nuevo.")
                                
        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        print("Error al procesar el mensaje:", e)
        return jsonify({'message': 'ERROR_PROCESSING_EVENT'}), 500





def enviar_mensajes_interactivo(numero):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "¡Hola!👋🏼 Soy MedicBot🤖, tu asistente virtual de salud. ¿En qué puedo ayudarte hoy? Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud. ¡Escribe tu consulta y comencemos!."
            },
            "footer": {
                "text": "Dinos si eres o quieres ser un Afiliado de MedicPlus."
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "si",
                            "title": "Afiliado"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "no",
                            "title": "Quiero Ser Afiliado"
                        }
                    }
                ]
            }
        }
    }
    enviar_mensajes_whatsapp(data)

def enviar_mensaje(numero, texto):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": texto
        }
    }
    enviar_mensajes_whatsapp(data)


def verificar_cedula(cedula):
    # Aquí va la lógica para verificar la cédula en tu base de datos
    # Ejemplo:
    usuario = Usuario.query.filter_by(cedula=cedula).first()
    return usuario is not None
 """