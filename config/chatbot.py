import http.client
import json
import re
from fastapi import FastAPI, Request, HTTPException, status, Query, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from database.connection import engine

from models.log import log
from models.usuarios import usuarios

from routes.user import get_user_state, get_user_state_register, verify_user

#rutas para respuestas del bot 
from routes.respuestas_bot.principal import principal_message, is_affiliate, return_button, message_not_found, affiliate_later
from routes.respuestas_bot.register.register import get_plan, insert_plan, insert_name, insert_last_name, insert_identification, insert_email
from routes.respuestas_bot.medical_attention.primary import get_info_primary_attention, confirm_call, cancel_call
from routes.respuestas_bot.principal import agregar_mensajes_log

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
                    print("esto trae el message: ", message)
                    agregar_mensajes_log({"message": message})
                    numero = message['from']
                    if "type" in message:
                        tipo = message["type"]
                        if tipo == "interactive":
                            print("entra en interactive")
                            tipo_interactivo = message["interactive"]["type"]
                            if tipo_interactivo == "button_reply":
                                text = message["interactive"]["button_reply"]["id"]
                                print(f"esto se pasa al contestar mensajes whats app: el texto {text} y el numero {numero}")
                                agregar_mensajes_log({"numero": numero})
                                agregar_mensajes_log({"tipo": tipo})
                                agregar_mensajes_log({"mensaje": text})
                                contestar_mensajes_whatsapp(text, numero)
                            elif tipo_interactivo == "list_reply":
                                text = message["interactive"]["list_reply"]["id"]
                                contestar_mensajes_whatsapp(text, numero)
                        elif "text" in message:
                            print("entra en text")
                            text = message["text"]["body"]
                            print(f"esto se pasa al contestar mensajes whats app: el texto {text} y el numero {numero}")
                            agregar_mensajes_log({"numero": numero})
                            agregar_mensajes_log({"tipo": tipo})
                            agregar_mensajes_log({"mensaje": text})
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

saludos = [
    'hola', 'buenas', 'buenos', 'hi', 'hello', 'hey', 
    'saludos', 'buenos días', 'buenas tardes', 'buenas noches', 
    'qué tal', 'holi', 'holis', 'qué onda', 'cómo estás', 
    'qué pasa', 'qué hay', 'qué cuentas', 'buen día'
]

def contestar_mensajes_whatsapp(texto, numero):
    texto = texto.lower()
    user = get_user_state(numero)
    if user["consult"] is None:
        print("entra en user none")
        get_user_state_register(numero, 'INIT')
        user = get_user_state(numero) #para actualizar user 
    print("este es el user state: ", user["state"])
    
    if user["state"] == 'INIT':
        print("entra en user init")
        #para mostrar el mensaje de inicio al recibir un saludo
        if any(re.search(r'\b' + saludo + r'\b', texto) for saludo in saludos):
            principal_message(numero)
            return True
        #respuesta de botones en caso que sea afiliado o se quiera afiliar 
        elif texto == "idsi":
            print("entra en que si es afiliado")
            
            is_affiliate(numero)
        elif texto == 'idno':
            print("entra en el boton que no es afiliado")
            get_plan(numero)
            return True
        elif texto == 'idtarde':
            affiliate_later(numero)
            return True
        elif "idinicio":
            principal_message(numero)
            return True
    
    #mensajes de flujo de registro 
    elif user["state"] == 'WAITING_FOR_PLAN':
        print("entra para ingresar el plan")
        insert_plan(numero, texto)
        return True
        
    elif user["state"] == 'WAITING_FOR_NAME':
        print("entra para ingresar el nombre del usuario")
        insert_name(numero, texto)
        return True

    elif user["state"] == 'WAITING_FOR_SURNAME':
        print("entra para ingresar el apellido del usuario")
        insert_last_name(numero, texto)
        return True

    elif user["state"] == 'WAITING_FOR_ID':
        print("entra para ingresar la cedula del usuario")
        insert_identification(numero, texto)
        return True

    elif user["state"] == 'WAITING_FOR_EMAIL':
        print("entra para ingresar el correo del usuario")
        insert_email(numero, texto, user)
        return True
    elif user["state"] == "REGISTERED":
        print("entra en el register")
        if any(re.search(r'\b' + saludo + r'\b', texto) for saludo in saludos):
            print("entra en el mensaje principal")
            principal_message(numero)
            return True
               
        #para ir al menu luego de registrarse
        elif "idvolver" in texto:
            print("entra en volver")
            return_button(numero)
            return True
        #respuestas para los afiliados 
        
        #atencion medica primaria 
        elif "idatenmedicpri" in texto:
            print("-------------------------------------entra en el elif de atenmedicpri------------------------------------------")
            get_info_primary_attention(numero)
            return True
        elif "idllamar" in texto:
            print("entra en el elif de llamar ")
            confirm_call(numero)
            return True
        elif "idnollamar" in texto:
            print("entra en el elif de llamar ")
            cancel_call(numero)
            return True
        
    else:
        print("entra en el else final donde no entiende ningun mensaje ")
        message_not_found(numero)
        return True    