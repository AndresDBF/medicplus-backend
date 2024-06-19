from fastapi import FastAPI, Request, HTTPException, status, Query
from fastapi.responses import JSONResponse
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
        conn.execute(log.insert().values(texto=texto))
        conn.commit()
    
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
        return JSONResponse(content={"hub.challenge": hub_challenge})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalido")



def enviar_mensajes_whatsapp(texto, numero):
    texto = texto.lower()
    if "hola" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Hola, ¿cómo estás? Bienvenido"
            }
        }
    elif "1" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem corporis quia sit molestias rerum! Cumque, ut? Excepturi id amet, mollitia vero eligendi iure debitis veritatis cumque voluptatibus unde possimus quibusdam!"
            }
        }
    elif "2" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "location",
            "location": {
                "latitude": "7.773414271044237",
                "longitude": "-72.20275777341328",
                "name": "Casa pirineos",
                "address": "Pirineos 2 edificio 21"
            }
        }

    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": (
                    "🚀Hola, visita mi web para más información\n"
                    "📌Por favor, ingresa un número #️⃣ para recibir información. \n"
                    "1️⃣ Información del curso. ❔ \n"
                    "2️⃣ Ubicación Local📍 \n"
                    "3️⃣ Audio explicando curso 🎧 \n"
                    "4️⃣ Video de introducción🎥\n"
                    "5️⃣ Habla conmigo🫡 \n"
                    "6️⃣ Horario de Atención🕙 \n"
                    "0️⃣ Regresar al menú⏪"
                )
            }
        }
    
    data = json.dumps(data)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAARqlwZAqLocBO3tS2JnIw1ZBHVjHC8ukbaQxQPaiXegRZB1tA8RcfAQHvB2Kop2P4q8uxuGX0zlc9MPIupKynMekc1sLOocZB13UL0F4DcVwk3ZBHmdKRROrOErQudWQrvFFZBkEnsuMptoynKrSZBKtINH8AgdLZBagBIlw9bZCHfzTT36UpjZBO52z72KCR9UsJYZBsQElKJu6CcehLSIpgZD"
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
        
    