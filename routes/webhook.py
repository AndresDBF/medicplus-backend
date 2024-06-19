import http.client
import json
from fastapi import FastAPI, Request, HTTPException, status, Query, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from database.connection import engine

from models.log import log

from routes.send_messages import enviar_mensajes_whatsapp

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

@chatbot.get("/webhook")
async def verify_token(hub_mode: str = Query(..., alias='hub.mode'), hub_challenge: str = Query(..., alias='hub.challenge'), hub_verify_token: str = Query(..., alias='hub.verify_token')):
    if hub_verify_token == TOKEN_ANDERCODE:
        return PlainTextResponse(content=hub_challenge)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalido")

