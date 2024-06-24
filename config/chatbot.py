import http.client
import json
import re
from fastapi import FastAPI, Request, HTTPException, status, Query, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from database.connection import engine

from models.log import log
from models.usuarios import usuarios

from routes.user import get_user_state, get_user_state_register, verify_user, get_user_state_identification, get_user_state_identification_register

#rutas para respuestas del bot 
from routes.respuestas_bot.principal import principal_message, return_button, message_not_found, get_services, get_plan
from routes.respuestas_bot.register.register import get_plan, insert_plan, insert_name, insert_last_name, insert_identification, insert_email
from routes.respuestas_bot.medical_attention.primary import get_info_identification_attention_primary, get_information_for_identification, get_info_primary_attention, confirm_call, cancel_call, question_affilate
from routes.respuestas_bot.medical_attention.telemedicine import get_info_identification_telemedicine, send_information_for_telemedicine
from routes.respuestas_bot.medical_attention.domiciliary import get_municipality, confirm_service, accept_domiciliary, decline_domiciliary
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

def contestar_mensajes_whatsapp(texto: str, numero):
    #consulta para tomar el status del usuario cuando ingrese la cedula 
    user_id = get_user_state_identification(numero)
    print("sale de get_user_state_identification")
    #consulta para tomar el status del usuario en el registro
    user_register = get_user_state(numero)
    print("sale de get_user_state")
    if user_id["consult"] is None:
        print("el user es null entra en el if")
        get_user_state_identification_register(numero, "INIT")
        user_id = get_user_state_identification(numero)
        user_id("actualiza user ")
    if user_register["consult"] is None:
        print("el user register es null, entra en el if ")
        get_user_state_register(numero, "INIT")
        user_register = get_user_state(numero)
        print("actualiza el status del user register")
        
    print("pasa el if del user null")
    print("este es el user state: ", user_id["state"])
    print("este es el user register: ", user_register)
    
    
    texto = texto.lower()
    
    
    if any(re.search(r'\b' + saludo + r'\b', texto) for saludo in saludos):
        print("entra en el mensaje principal")
        principal_message(numero)
        return True
    
    #seleccion de las primeras opciones de servicios o planes 
    elif "idservicios" in texto:
        print("entra en seleccion de servicios")
        get_services(numero)
        return True
    
    elif "idplanes" in texto:
        print("entra en planes")
        get_plan(numero)
        return True
    
#---------------------------respuestas a selecciones de los servicios-------------------------

    #para la ejecucion de registros 
    elif "idregistrar" in texto:
        print("entra en la primera fase de escoger plan para registrarse")
        get_plan(numero)
    elif user_register["state"] == 'WAITING_FOR_PLAN':
        print("entra para ingresar el plan")
        insert_plan(numero, texto)
        return True
        
    elif user_register["state"] == 'WAITING_FOR_NAME':
        print("entra para ingresar el nombre del usuario")
        insert_name(numero, texto)
        return True

    elif user_register["state"] == 'WAITING_FOR_SURNAME':
        print("entra para ingresar el apellido del usuario")
        insert_last_name(numero, texto)
        return True

    elif user_register["state"] == 'WAITING_FOR_ID':
        print("entra para ingresar la cedula del usuario")
        insert_identification(numero, texto)
        return True

    elif user_register["state"] == 'WAITING_FOR_EMAIL':
        print("entra para ingresar el correo del usuario")
        insert_email(numero, texto, user_register)
        return True
    
      
    #-------------------atencion medica inmediata----------------------
    #para afiliados
    elif "idatenmedicpri" in texto:
        print("entra en primaria para preguntar si es afiliado o no")
        question_affilate(numero)
    elif "idconfirmaffiliate" in texto:
        print("entra en que si es afiliado")
        get_info_identification_attention_primary(numero)
        return True
    
    elif user_id["state"] == "WAITING_FOR_ID":
        print("entra en recibir cedula")
        get_information_for_identification(numero, texto)
        return True
    
    elif "idnotaffiliate" in texto:
        print("entra para la atencion de los no afiliados")
        get_info_primary_attention(numero)
        return True
    #para no afiliados
    elif "idllamar" in texto:
        print("entra en que quiere llamar")
        confirm_call(numero)
        return True
    elif "idnollamar" in texto:
        print("entra en que no quiere llamar")
        cancel_call(numero)
        return True
    #-------------------telemedicina----------------------
    
    elif "idtelemed" in texto:
        print("entra en la telemedicina")
        get_info_identification_telemedicine(numero)
        return True
    elif user_id["state"] == "WAITING_FOR_ID_TELEMEDICINE":
        print("entra para mostrar la respuesta de telemedina")
        send_information_for_telemedicine(numero,texto)   
    

    #-------------------atencion medica domiciliaria----------------------
    
    elif "idatenmeddomi" in texto:
        print("entra en atencion medica domiciliaria")
        get_municipality(numero)
        return True
    elif "idmunicipio" in texto:
        print("entra en la confirmacion de servicio por municipio")
        confirm_service(numero)
        return True
    elif "idconfirmdomiciliary" in texto:
        print("entra en confirmar domicilio")
        accept_domiciliary(numero)
        return True
    elif "iddeclinedomiciliary" in texto: 
        print("cancelar domicilio")
        decline_domiciliary(numero)
        return True
        
    #boton de volver 
    elif "idvolver" in texto:
        return_button(numero)
        return True
    
    """ user = get_user_state(numero)
    #verifica el status del usuario si ha sido registrado o no
    if user["consult"] is None:
        print("entra en user none")
        get_user_state_register(numero, 'INIT')
        user = get_user_state(numero) 
    print("este es el user state: ", user["state"])
    #----------------------------------------------respuestas para los NO afiliados-----------------------------------------------------
    if user["state"] == 'INIT':
        print("entra en user init")
        #para mostrar el mensaje de inicio al recibir un saludo
        if any(re.search(r'\b' + saludo + r'\b', texto) for saludo in saludos):
            principal_message(numero)
            return True
        #para ir al menu luego de registrarse
        elif "idvolver" in texto:
            print("entra en volver")
            return_button(numero)
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
    
    
    
    #--------------------------------------respuestas para los afiliados ----------------------------------------------------
    elif user["state"] == "REGISTERED":
        print("entra en el register")
        if any(re.search(r'\b' + saludo + r'\b', texto) for saludo in saludos):
            print("entra en el mensaje principal")
            principal_message(numero)
            return True
        
        elif texto == "idsi":
            print("entra en que si es afiliado")
            
            is_affiliate(numero)
        elif texto == 'idno':
            print("entra en el boton que no es afiliado")
            get_plan(numero)
            return True
             
       
        #atencion medica primaria 
        elif "idatenmedicpri" in texto:
            print("-------------------------------------entra en el elif de idatenmedicpri------------------------------------------")
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
        
        #respuestas para telemedicina 
        elif "idtelemed" in texto:
            print("-------------------------------------entra en el elif de telemedicina------------------------------------------")
            get_info_telemedicine_attention(numero)
            return True
        elif "idllamar" in texto:
            print("entra en el elif de llamar ")
            confirm_call(numero)
            return True
        elif "idnollamar" in texto:
            print("entra en el elif de llamar ")
            cancel_telemedicine(numero)
            return True
        
        #atencion medica domiciliaria
        elif "idatenmeddomi" in texto:
            print("entra en atencion medica domiciliaria")
            get_municipality(numero)
            return True
        elif "idmunicipio" in texto:
            print("entra en la confirmacion de servicio por municipio")
            confirm_service(numero)
            return True
        elif "idconfirmdomiciliary" in texto:
            print("entra en confirmar domicilio")
            accept_domiciliary(numero)
            return True
        elif "iddeclinedomiciliary" in texto: 
            print("cancelar domicilio ")
            decline_domiciliary(numero)
            return True
    else:
        print("entra en el else final donde no entiende ningun mensaje ")
        message_not_found(numero)
        return True    
    
    """
   
    
    
    
    
    
    
    
    
    
    
    
    
    
    