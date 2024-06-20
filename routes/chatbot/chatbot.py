import http.client
import json
import re
from fastapi import FastAPI, Request, HTTPException, status, Query, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from database.connection import engine

from models.log import log
from models.usuarios import usuarios

from routes.user import get_user_state, get_user_state_register

from datetime import datetime

chatbot = APIRouter(tags=["Login"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Configuración de plantillas y archivos estáticos
templates = Jinja2Templates(directory="templates")

TOKEN_ANDERCODE = "ANDERCODE"

@chatbot.get("/")
async def index(request: Request):
    with engine.connect() as conn:
        registros = conn.execute(log.select().order_by(log.c.fecha_y_hora.asc())).fetchall()
    
    return templates.TemplateResponse("index.html", {"request": request, "registros": registros})

def agregar_mensajes_log(texto):
    texto_str = json.dumps(texto)
    with engine.connect() as conn:
        conn.execute(log.insert().values(texto=texto_str, fecha_y_hora=datetime.utcnow()))
        conn.commit()
    print("Mensaje guardado en el log:", texto)

@chatbot.post("/webhook")
async def webhook(req: Request):
    try:
        req_data = await req.json()
        print("Datos JSON recibidos:", req_data)
        
        for entry in req_data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                for message in messages:
                    numero = message['from']
                    if "type" in message:
                        tipo = message["type"]
                        if tipo == "interactive":
                            tipo_interactivo = message["interactive"]["type"]
                            if tipo_interactivo == "button_reply":
                                text = message["interactive"]["button_reply"]["id"]
                                contestar_mensajes_whatsapp(text, numero)
                            elif tipo_interactivo == "list_reply":
                                text = message["interactive"]["list_reply"]["id"]
                                contestar_mensajes_whatsapp(text, numero)
                        elif "text" in message:
                            text = message["text"]["body"]
                            contestar_mensajes_whatsapp(text, numero)
                        
        return JSONResponse(content={'message': 'EVENT_RECEIVED'})
    except Exception as e:
        print("Error al procesar el mensaje:", e)
        return JSONResponse(content={'message': 'ERROR_PROCESSING_EVENT'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@chatbot.get("/webhook")
async def verify_token(hub_mode: str = Query(..., alias='hub.mode'), hub_challenge: str = Query(..., alias='hub.challenge'), hub_verify_token: str = Query(..., alias='hub.verify_token')):
    if hub_verify_token == TOKEN_ANDERCODE:
        return PlainTextResponse(content=hub_challenge)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalido")        

def enviar_mensajes_whatsapp (data):
    
    data = json.dumps(data)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAARqlwZAqLocBO34EBFSMCDZAriZCoCtL7AcwTglEJqmqHSciWlZBDTiDOGuZAOgOa8qo1blrPCUpplPP8e7T3a8gTMzUTPBO4PyNtj7cspsdJfGuWl0bNCKnzisTEjVVZAzwsJv2WAXSpY2Mg4UNPj1rXpbRSNz1bGfZCniIPQu0EKRF4UZBW0WaUz60QgCfr1ZC53jW8kM31ysJRNwxZCmZBc"
    }
    
    connection = http.client.HTTPSConnection("graph.facebook.com")
    
    try:
        connection.request("POST", "/v19.0/373926142459719/messages", data, headers)
        response = connection.getresponse()
        response_data = response.read().decode()
        print(response.status, response.reason, response_data)
        if response.status != 200:
            agregar_mensajes_log(f"Error al enviar mensaje: {response.status} {response.reason} {response_data}")
    except Exception as e:
        print(f"Exception: {e}")
        agregar_mensajes_log(f"Exception al enviar mensaje: {e}")
    finally:
        connection.close()


saludos = [
    'hola', 'buenas', 'buenos', 'hi', 'hello', 'hey', 
    'saludos', 'buenos días', 'buenas tardes', 'buenas noches', 
    'qué tal', 'holi', 'holis', 'qué onda', 'cómo estás', 
    'qué pasa', 'qué hay', 'qué cuentas', 'buen día'
]

def contestar_mensajes_whatsapp(texto, numero):
    texto = texto.lower()
    user = get_user_state(numero)
    if user is None:
        get_user_state_register(numero, 'INIT')
    if user['state'] == 'INIT' or texto == "volver":
        if any(re.search(r'\b' + saludo + r'\b', texto) for saludo in saludos):
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
        elif texto == "si":
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Estas registrado ya nos comunicaremos contigo"
                }
            }
            enviar_mensajes_whatsapp(data)
        elif texto == 'no':
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Para registrarte, por favor envía tu nombre:"
                }
            }
            enviar_mensajes_whatsapp(data)
            get_user_state_register(numero, 'WAITING_FOR_NAME')

    elif user['state'] == 'WAITING_FOR_NAME':
        get_user_state_register(numero, 'WAITING_FOR_SURNAME', nombre=texto)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Gracias. Ahora, por favor envía tu apellido:"
            }
        }
        enviar_mensajes_whatsapp(data)

    elif user['state'] == 'WAITING_FOR_SURNAME':
        get_user_state_register(numero, 'WAITING_FOR_ID', apellido=texto)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Perfecto. Por favor envía tu cédula:"
            }
        }
        enviar_mensajes_whatsapp(data)

    elif user['state'] == 'WAITING_FOR_ID':
        get_user_state_register(numero, 'WAITING_FOR_EMAIL', cedula=texto)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Muy bien. Finalmente, por favor envía tu correo electrónico:"
            }
        }
        enviar_mensajes_whatsapp(data)

    elif user['state'] == 'WAITING_FOR_EMAIL':
        get_user_state_register(numero, 'REGISTERED', email=texto)
        
        # Aquí guarda el usuario en la base de datos
        with engine.connect() as conn:
            conn.execute(usuarios.insert().values(
                use_nam=user['nombre'].lower(),  # Cambia según tus necesidades
                email=texto,
                password="default",  # Asigna un valor por defecto o genera uno
                nom_usu=user['nombre'],
                ape_usu=user['apellido'],
                gen_usu="U",  # Asigna un valor por defecto o solicita al usuario
                tel_usu=numero
            ))
        data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": "Su informacion ha sido registrada exitosamente.📝 uno de nuestros asesores de ventas 🧑🏻‍💼👨🏼‍💼 se pondra en contacto con usted en la brevedad posible."
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "volver",
                                    "title": "Volver"
                                }
                            }
                        ]
                    }
                }
            }
        
        enviar_mensajes_whatsapp(data)        
    
    #respuestas en caso de ser afiliado
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": (
                    "No comprendo muy bien tu mensaje, por favor puedes repetirlo nuevamente.\n \n Recuerda Utilizar los botones proporcionados para poderte ayudar🤖"
                )
            }
        }
        enviar_mensajes_whatsapp(data)
    