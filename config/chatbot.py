import http.client
import json
import re
from fastapi import FastAPI, Request, HTTPException, status, Query, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from database.connection import engine

from models.log import log
from models.usuarios import usuarios
from models.user_state_register import user_state_register

from routes.user import get_user_state, get_user_state_register, verify_user, get_user_state_identification, get_user_state_domiciliary, get_user_state_especiality, get_user_state_imaging, get_user_state_lab, get_user_state_ambulance, get_user_state_identification_register, update_user_state_domiciliary, update_user_state_especiality, update_user_state_lab, update_user_state_ambulance, update_user_state_imaging

#rutas para respuestas del bot 
from routes.respuestas_bot.principal import principal_message, return_button, message_not_found, get_services, cancel_button, goodbye_message, change_english, change_spanish
from routes.respuestas_bot.register.register import get_plan, is_affiliate, insert_plan, insert_name, insert_last_name, insert_identification, insert_email
from routes.respuestas_bot.register.plan import get_list_plan, send_info_plan, send_name_affiliate
#atenciones medicas
from routes.respuestas_bot.medical_attention.primary import get_info_identification_attention_primary, get_information_for_identification, get_info_primary_attention, confirm_call, cancel_call, question_affilate
from routes.respuestas_bot.medical_attention.telemedicine import get_info_identification_telemedicine, send_information_for_telemedicine
from routes.respuestas_bot.medical_attention.domiciliary import get_municipality, confirm_service, accept_domiciliary, decline_domiciliary
#otros servicios
from routes.respuestas_bot.other_services.medic_consult import get_list_speciality, get_names_especialitys, save_appointment, confirm_consult, cancel_consult
from routes.respuestas_bot.other_services.laboratory import get_service_lab, select_service_lab, send_service_location, confirm_visit_lab, cancel_visit_lab, confirm_domiciliary_lab, cancel_domiciliary_lab, get_list_service_lab
from routes.respuestas_bot.other_services.ambulance import get_list_municipalities, select_municipalities, confirm_ambulance, cancel_ambulance
from routes.respuestas_bot.other_services.call_oper import question_operator, confirm_oper, cancel_oper
from routes.respuestas_bot.other_services.imaging import get_eco_or_rx, send_tip_imaging, verify_imaging, cancel_test, confirm_visit_imag, question_visit_lab
from routes.respuestas_bot.principal import agregar_mensajes_log

from datetime import datetime

from googletrans import Translator

chatbot = APIRouter(tags=["Login"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Configuración de plantillas y archivos estáticos
templates = Jinja2Templates(directory="templates")

TOKEN_ANDERCODE = "ANDERCODE"

translate_to_english = False

@chatbot.get("/")
async def index(request: Request):
    with engine.connect() as conn:
        registros = conn.execute(log.select().order_by(log.c.fecha_y_hora.asc())).fetchall()
    
    return templates.TemplateResponse("index.html", {"request": request, "registros": registros})

@chatbot.post("/webhook")
async def webhook(req: Request):
    try:
        req_data = await req.json()
        
        
        for entry in req_data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                contacts = value.get('contacts',[])
                for contact in contacts: 
                    name_contact = contact["profile"]["name"]
                for message in messages:
                   
                    agregar_mensajes_log({"message": message})
                    numero = message['from']
                    if "type" in message:
                        tipo = message["type"]
                        if tipo == "interactive":
                   
                            tipo_interactivo = message["interactive"]["type"]
                            if tipo_interactivo == "button_reply":
                                text = message["interactive"]["button_reply"]["id"]
                               
                                print(f"esto se pasa al contestar mensajes whats app: el texto {text} y el numero {numero}")
                                agregar_mensajes_log({"numero": numero})
                                agregar_mensajes_log({"tipo": tipo})
                                agregar_mensajes_log({"mensaje": text})
                                contestar_mensajes_whatsapp(text, name_contact, numero)
                            elif tipo_interactivo == "list_reply":
                                text = message["interactive"]["list_reply"]["id"]
                                agregar_mensajes_log({"numero": numero})
                                agregar_mensajes_log({"tipo": tipo})
                                agregar_mensajes_log({"mensaje": text})
                                contestar_mensajes_whatsapp(text, name_contact, numero)
                        elif "text" in message:
                            print("entra en text")
                            text = message["text"]["body"]
                            # Activar/desactivar traducción según la palabra clave
                            
                                
                            print(f"esto se pasa al contestar mensajes whats app: el texto {text} y el numero {numero}")
                            agregar_mensajes_log({"numero": numero})
                            agregar_mensajes_log({"tipo": tipo})
                            agregar_mensajes_log({"mensaje": text})
                            contestar_mensajes_whatsapp(text, name_contact, numero)
                        
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
    'hola', 'buenas', 'buenos', 
    'saludos', 'buenos días', 'buenas tardes', 'buenas noches', 
    'qué tal', 'holi', 'holis', 'qué onda', 'cómo estás', 
    'qué pasa', 'qué hay', 'qué cuentas', 'buen día', 'informacion'
]

saludos_ingles = ["hello", "hi", "good",
 "greetings", "good morning", "good afternoon", "good evening",
 "how are you", "holi", "holis", "whats up", "how are you",
 "what's up", "what's up", "what's up", "good day", "information"]

cambio_idioma = ['no entiendo', 'no comprendo', 'no capto', 'cambiame', 'cambia', 'español', 'spanish', 'no se hablar', 'no se escribir', 'no sé hablar',
    'no sé escribir', 'idioma', 'lenguaje']

cambio_idioma_ingles = ["I don't understand", "I don't understand", "I don't understand", "change me", "change",
    "english", "ingles","I don't know how to speak", "I don't know how to write", "language"]


cancelaciones = [
    'cancelar', 'cancela', 'atras', 'retrocede', 'no quiero', 'olvida', 'olvidalo', 'llevame',
    'lleveme', 'lleve', 'ir', 'inicio','menu','opciones', 'de nuevo', 'regresar', 'devolverme', 'devolver', 'volver', 'retrocerder'
]

cancelaciones_ingles = [
    "cancel", "cancel", "back", "go back", "I don't want to", "forget", "forget it", "take me",
 "take me", "take me", "go", "home",  "options", "again", "return", "return me", "return", "return"
]

despedidadas = [
    'adios', 'chao', 'bye', 'hasta luego', 'nos vemos', 'hasta pronto', 'gracias', 'agradecido',
    'hablamos luego', 'hablamos despues', 'cumplido', 'cumplir', 'terminar','terminado'
]

despedidas_ingles = ["goodbye", "bye", "bye", "see you later", "see you", "see you soon", "thank you", "grateful",
 "we'll talk later", "we'll talk later", "accomplished", "comply", "finish", "finished"]

def contestar_mensajes_whatsapp(texto: str, name_contact, numero):
    #consulta para tomar el status del usuario cuando ingrese la cedula 
    user_id = get_user_state_identification(numero)
    
    #consulta para tomar el status del usuario en el registro
    user_register = get_user_state(numero)
    
    #consulta para tomar el status del usuario en la solicitud de consulta 
    user_consult = get_user_state_especiality(numero)
    
    #consulta para tomar el status del usuario en la solicitud de consulta 
    user_imaging = get_user_state_imaging(numero)
    
    #consulta para tomar el status del usuario en la solicitud de atencion medica domiciliaria 
    user_team_medic = get_user_state_domiciliary(numero)
    
    #consulta para tomar el status del usuario en la solicitud de laboratorios
    user_lab = get_user_state_lab(numero) 
    
    #consulta para tomar el status del usuario en la solicitud de ambulancias 
    user_ambulance = get_user_state_ambulance(numero)
   
    if user_id["consult"] is None:
      
        get_user_state_identification_register(numero, "INIT")
        user_id = get_user_state_identification(numero)
       
    if user_register["consult"] is None:

        get_user_state_register(numero, "INIT")
        user_register = get_user_state(numero)
    
    if user_consult["consult"] is None:
        update_user_state_especiality(numero, "INIT")
    
    if user_imaging["consult"] is None:
        print("entra en consult none")
        update_user_state_imaging(numero, 'INIT')
    
    if user_lab["consult"] is None:
        update_user_state_lab(numero, "INIT")
    
    if user_ambulance["consult"] is None:
        update_user_state_ambulance(numero, 'INIT')
    
    if user_team_medic["consult"] is None:
        update_user_state_domiciliary(numero, 'INIT')
    
        
    print("pasa el if del user null")
    print("este es el user state: ", user_id)
    print("este es el user register: ", user_register)
    print("este es el user consult: ", user_consult)
    print("este es el user lab: ", user_lab)
    print("este es el user ambulance: ", user_ambulance)
    print("este es el user team medic: ", user_team_medic)
    print("este es el user imaging: ", user_imaging)
    
    
    texto = texto.lower()
    with engine.connect() as conn:    
        if any(re.search(r'\b' + saludo + r'\b', texto) for saludo in saludos_ingles):
            conn.execute(user_state_register.update().where(user_state_register.c.numero==numero).values(language=True))
            conn.commit()
            principal_message(numero)
            return True
        elif any(re.search(r'\b' + cancelar + r'\b', texto) for cancelar in cancelaciones_ingles):
            conn.execute(user_state_register.update().where(user_state_register.c.numero==numero).values(language=True))
            conn.commit()
            cancel_button(numero)
            return True
        elif any(re.search(r'\b' + despedir + r'\b', texto) for despedir in despedidas_ingles):
            conn.execute(user_state_register.update().where(user_state_register.c.numero==numero).values(language=True))
            conn.commit()
            goodbye_message(numero)
            return True
        #cambio de idiomas pedidos por el usuario 
        elif any(re.search(r'\b' + cambio_esp + r'\b', texto) for cambio_esp in cambio_idioma):
            conn.execute(user_state_register.update().where(user_state_register.c.numero==numero).values(language=False))
            conn.commit()
            change_spanish(numero)
            return True
        elif any(re.search(r'\b' + cambio_eng + r'\b', texto) for cambio_eng in cambio_idioma_ingles):
            conn.execute(user_state_register.update().where(user_state_register.c.numero==numero).values(language=True))
            conn.commit()
            change_english(numero)
            return True
#-------------------------------------valida primero el idvolver por si algun proceso no fue completado----------------------------------
    
    if "idvolver" in texto:
        return_button(numero)
        return True
    
    #----------------------------seleccion de las primeras opciones de servicios o planes --------------------------------------------------
    elif "idservicios" in texto:
        print("entra en seleccion de servicios")
        get_services(numero)
        return True
    
    elif "idplanes" in texto:
        print("entra en planes")
        get_list_plan(numero)
        return True
    
    elif "idconfirmplan" in texto:
        print("entra en idconfirmplan")
        send_name_affiliate(numero)
        return True

#---------------------------------VALIDANDO LOS BOTONES ---------------------------------------------------------------------
    with engine.connect() as conn:    
        if any(re.search(r'\b' + saludo + r'\b', texto) for saludo in saludos):
            conn.execute(user_state_register.update().where(user_state_register.c.numero==numero).values(language=False))
            conn.commit()
            print("entra en el mensaje principal")
            principal_message(numero)
            return True
        elif any(re.search(r'\b' + cancelar + r'\b', texto) for cancelar in cancelaciones):
            conn.execute(user_state_register.update().where(user_state_register.c.numero==numero).values(language=False))
            conn.commit()
            print("entra en las cancelaciones")
            cancel_button(numero)
            return True
        
        elif any(re.search(r'\b' + despedir + r'\b', texto) for despedir in despedidadas):
            conn.execute(user_state_register.update().where(user_state_register.c.numero==numero).values(language=False))
            conn.commit()
            print("entra en las despedidas")
            goodbye_message(numero)
            return True
#-------------------------------------validamos los status de las variables --------------------------------------------------------------
    #status del registro
    if user_register["state"] == 'WAITING_FOR_PLAN':
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
    

    
    #status para la solicitud de planes
    elif user_register["state"] == "WAITING_FOR_SERVICE_PLAN" or texto == "idplanes":
        print("entra en ver los planes")
        send_info_plan(numero, texto)
        return True
    
    #status al pedir la cedula de identidad 
    #para la atencion medica inmediata
    elif user_id["state"] == "WAITING_FOR_ID":
        print("entra en recibir cedula")
        get_information_for_identification(numero, texto)
        return True
    
    
    #para telemedicina
    elif user_id["state"] == "WAITING_FOR_ID_TELEMEDICINE" and not "idregistrar" in texto:
        print("entra para mostrar la respuesta de telemedina")
        send_information_for_telemedicine(numero,texto)   
        return True
   
    #para atencion medica domiciliaria 
    elif user_team_medic["state"] == "WAITING_FOR_MUNICIPALITI_DOMI":
        confirm_service(numero, texto)
        return True    
    
    
    #para las solicitudes de consultas 
    elif user_consult["state"] == "WAITING_FOR_SPECIALITY":
        get_names_especialitys(numero, texto)
    elif user_consult["state"] == "WAITING_FOR_NAME_ESP":
        save_appointment(numero, texto)
        return True
    
    #para las solicitudes de imagenologia 
    elif user_imaging["state"] == "WAITING_FOR_IMAGING":
        print("entra en send_tip_imaging")
        send_tip_imaging(numero, texto)
    elif user_imaging["state"] == "WAITING_FOR_SEND_IMAGING":
        print("entra en verify_imaging")
        verify_imaging(numero, texto)
        return True
    elif user_imaging["state"] == "WAITING_FOR_SELECT_IMAGING":
        print("entra en question_visit_lab")
        question_visit_lab(numero,texto)
        return True
    
    #LABORATORIOS
    elif user_lab["state"] == "WAITING_FOR_TEST":
        print("entra para seleccionar la prueba")
        get_list_service_lab(numero, texto)
        return True
    elif user_lab["state"] == "WAITING_FOR_SELECT_TEST":
        print("entra para enviar send_service_location")
        send_service_location(numero, texto)
        return True
    
    elif user_lab["state"] == "WAITING_FOR_LOCATION":
        print("entra en selec service lab")
        select_service_lab(numero, texto)
        return True   
    
    #AMBULANCIAS 
    elif user_ambulance["state"] == "WAITING_FOR_MUNICIPALITI":
        select_municipalities(numero, texto)
        return True
    
#---------------------------respuestas a selecciones de los servicios-------------------------

    #para la ejecucion de registros 
    elif "idregistrar" in texto:
        print("entra en la primera fase de escoger plan para registrarse")
        get_plan(numero)
        return True
      
#-------------------------------------------ATENCION MEDICA INMEDIATA--------------------------------------------------------------------
    #para afiliados
    elif "idatenmedicpri" in texto:
        print("entra en primaria para preguntar si es afiliado o no")
        question_affilate(numero)
        return True
    elif "idconfirmaffiliate" in texto:
        print("entra en que si es afiliado")
        get_info_identification_attention_primary(numero)
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
#------------------------------------------------TELEMEDICINA---------------------------------------------------------------------------
    
    elif "idtelemed" in texto:
        print("entra en la telemedicina")
        get_info_identification_telemedicine(numero)
        return True
 
    

#-----------------------------------------ATENCION MEDICA DOMICILIARIA------------------------------------------------------------------
    
    elif "idatenmeddomi" in texto:
        print("entra en atencion medica domiciliaria")
        get_municipality(numero)
        return True
    elif "idconfirmdomiciliary" in texto:
        print("entra en confirmar domicilio")
        accept_domiciliary(numero)
        return True
    elif "iddeclinedomiciliary" in texto: 
        print("cancelar domicilio")
        decline_domiciliary(numero)
        return True
#------------------------------------------------CONSULTAS MEDICAS-----------------------------------------------------------------------
    elif "idconmed" in texto:
        print("entra en consultas medicas")
        get_list_speciality(numero)
        return True
    elif "idconfirmconsult" in texto:
        confirm_consult(numero, name_contact)
        return True
    elif "iddeclineconsult" in texto:
        cancel_consult(numero)
        return True

#------------------------------------------------IMAGENOLOGIA----------------------------------------------------------------------- 
    elif "idimagenologia" in texto:
        print("entra en idimaginologia")
        get_eco_or_rx(numero)
        return True
   
    elif "idconfirmvisitimag" in texto:
        confirm_visit_imag(numero)
        return True
    elif "idcancelvisitimag" in texto:
        cancel_test(numero)
        return True
  
#------------------------------------------------LLAMAR UN OPERADOR-----------------------------------------------------------------------
    
    elif "idcalloper" in texto:
        question_operator(numero)
        return True
    elif "idconfirmoper" in texto:
        confirm_oper(numero, name_contact)
        return True
    elif "idcanceloper" in texto:
        cancel_oper(numero)
        return True
            
    
        
#------------------------------------------------LABORATORIOS----------------------------------------------------------------------------
    elif "idlabori" in texto:
        get_service_lab(numero)
        return True
    elif "idconfirmvisit" in texto:
        print("entra en que confirma la visita al laboratorio")
        confirm_visit_lab(numero)
        return True
    elif "idcancelvisit" in texto:
        print("entra en que cancela la visita al laboratorio")
        cancel_visit_lab(numero)
        return True
    elif "idconfirmequip" in texto:
        print("entra en que confirma el domicilio del laboratorio")
        confirm_domiciliary_lab(numero)
        return True
    elif "idcancelequip" in texto:
        print("entra en que cancela el domicilio del laboratorio")
        cancel_domiciliary_lab(numero)
        return True
    elif "idbuscarprueba" in texto:
        print("entra en que quiere otra prueba")
        update_user_state_lab(numero, 'INIT')
        get_service_lab(numero)
        return True
    
#------------------------------------------------AMBULANCIAS----------------------------------------------------------------------------
    elif "idambula" in texto:
        print("entra en idambula")
        get_list_municipalities(numero)
        return True
    elif "idconfirmambulance" in texto:
        confirm_ambulance(numero)
        return True
    
    elif "idcancelambulance" in texto:
        cancel_ambulance(numero)
        return True
    
    else:
        print("entra en el else final donde no entiende ningun mensaje ")
        message_not_found(numero)
        return True    
  