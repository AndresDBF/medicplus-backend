""" import http.client
import json
from fastapi import FastAPI, Request, HTTPException, status, Query, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database.connection import engine

from models.log import log

from routes.webhook import agregar_mensajes_log

sendmessages = APIRouter(tags=["Login"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})
    
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

         """