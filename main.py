from fastapi import FastAPI, Request, HTTPException, status, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, DateTime, Text
from database.connection import engine
from models.log import log

from datetime import datetime
import http.client
import json

app = FastAPI()

# Configuración de plantillas y archivos estáticos
templates = Jinja2Templates(directory="templates")


# Función para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)

@app.get("/")
async def index(request: Request):
    with engine.connect() as conn:
        registros = conn.execute(log.select().order_by(log.c.fecha_y_hora.asc())).fetchall()
    
    return templates.TemplateResponse("index.html", {"request": request, "registros": registros})

# Función para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    texto_str = json.dumps(texto)
    with engine.connect() as conn:
        conn.execute(log.insert().values(texto=texto_str, fecha_y_hora=datetime.utcnow()))
        conn.commit()
    print("Mensaje guardado en el log:", texto)
    
TOKEN_ANDERCODE = "ANDERCODE"

@app.post("/webhook")
async def webhook(req: Request):
    try:
        req_data = await req.json()
        print("Datos JSON recibidos:", req_data)
        
        for entry in req_data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                for message in messages:
                    print("Mensaje recibido:", message)  # Agregamos esta línea para debug
                    if "type" in message:
                        tipo = message["type"]
                        agregar_mensajes_log({"tipo": tipo})
                        agregar_mensajes_log({"mensaje": message})
                        if tipo == "interactive":
                            tipo_interactivo = message["interactive"]["type"]
                            if tipo_interactivo == "button_reply":
                                text = message["interactive"]["button_reply"]["id"]
                                numero = message["from"]
                                enviar_mensajes_whatsapp(text, numero)
                            elif tipo_interactivo == "list_reply":
                                text = message["interactive"]["list_reply"]["id"]
                                numero = message["from"]
                                enviar_mensajes_whatsapp(text, numero)
                        if "text" in message:
                            text = message["text"]["body"]
                            numero = message["from"]
                            enviar_mensajes_whatsapp(text, numero)
                            agregar_mensajes_log({"mensaje": message})
        return JSONResponse(content={'message': 'EVENT_RECEIVED'})
    except Exception as e:
        print("Error al procesar el mensaje:", e)
        return JSONResponse(content={'message': 'ERROR_PROCESSING_EVENT'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/webhook")
async def verify_token(hub_mode: str = Query(..., alias='hub.mode'), hub_challenge: str = Query(..., alias='hub.challenge'), hub_verify_token: str = Query(..., alias='hub.verify_token')):
    if hub_verify_token == TOKEN_ANDERCODE:
        return PlainTextResponse(content=hub_challenge)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalido")




def enviar_mensajes_whatsapp(texto, numero):
    texto = texto.lower()
    if texto in ['hola','buenas','buenos','que tal']:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "¡Hola!👋🏼 Soy MedicBot🤖, tu asistente virtual de salud. ¿En qué puedo ayudarte hoy? Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud. ¡Escribe tu consulta y comencemos!."
                },
                "footer": {
                    "text": "Dinos si eres o quieres ser un Afiliado de MedicPlus."
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply":{
                                "id":"btnsi",
                                "title":"Afiliado"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"btnno",
                                "title":"Quiero Ser Afiliado"
                            }
                        }
                    ]
                }
            }
        }
    elif "btnsi" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Muchas gracias por aceptar"
            }
        }
    elif "btnno" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Es una lastima"
            }
        }
   
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": (
                    "No comprendo muy bien tu mensaje, por favor puedes repetirlo nuevamente."
                )
            }
        }
    
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

        
    