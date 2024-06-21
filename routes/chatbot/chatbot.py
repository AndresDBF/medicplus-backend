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
    try:
        texto_str = json.dumps(texto)
        print("asi queda el texto antes de insertar en el log: ", texto_str)
        print("y este es el tipo de dato: ", type(texto_str))
        with engine.connect() as conn:
            conn.execute(log.insert().values(texto=texto_str, fecha_y_hora=datetime.utcnow()))
            conn.commit()
        print("Mensaje guardado en el log:", texto)
    except Exception as e:
        print(f"Error al guardar el mensaje en el log: {e}")

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

def enviar_mensajes_whatsapp (data):
    
    data = json.dumps(data)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAOJtyjmw9EBOyAEc9G5t2L0OpAwMMrGKgOMyZAFxZAxagGQxZC4qwIOZBVxdVMLafbM84V3Va8IOTexfJK3wP2JDubvyNeVZAjaFZBVQRfo8fzJhmdtJXe3qQsFE5YwzVjVZAfgC4qgoyOZBj4LfkgBNkkGnlduqd3TtwMYcWIhcZCSHpAkgu2fZAodR5ndKcKVvVtDwSdrhtnwtjatklOdUZD"
    }
    
    connection = http.client.HTTPSConnection("graph.facebook.com")
    
    try:
        connection.request("POST", "/v19.0/330743666794546/messages", data, headers)
        response = connection.getresponse()
        response_data = response.read().decode()
        print("se enviaron los mensajes")
        print("este fue el response al enviar el mensaje: ", response.status, response.reason, response_data)
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
    if user["consult"] is None:
        print("entra en user none")
        get_user_state_register(numero, 'INIT')
        user = get_user_state(numero) #para actualizar user 
    print("este es el user state: ", user["state"])
    
    if user["state"] == 'INIT':
        print("entra en user init")
        #para mostrar el mensaje de inicio al recibir un saludo
        if any(re.search(r'\b' + saludo + r'\b', texto) for saludo in saludos):
            print("pasa las expresiones regulares")
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
            print("envia el mensaje principal")
            enviar_mensajes_whatsapp(data)
            return True
        
        #respuesta de botones en caso que sea afiliado o se quiera afiliar 
        elif texto == "si":
            print("entra en que si es afiliado")
            result_json = verify_user(numero)
            #mensajes que seran mostrados cuando el usuario seleccione que es afiliado se verifica si de verdad esta registrado
            #se encontrara un mensaje positivo dando las opciones y otro para pedir registrarse o hacerlo mas tarde
            print("------------saliendo de verify_user-----------------")
            print("esto trae el result_json: ", result_json)
            if result_json["registered"] == False:
                print("entra en el if")
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": numero,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {
                            "text": f"{result_json['text']}"
                        },
                        "action": {
                            "buttons": [
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "tarde",
                                        "title": "Mas tarde"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "no",
                                        "title": "Quiero Registrarme"
                                    }
                                }
                            ]
                        }
                    }
                }
                print("envia el mensaje principal 3")
                enviar_mensajes_whatsapp(data)
                return True
            else:
                print("entra en el else")
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": numero,
                    "type": "text",
                    "text": {
                        "preview_url": False,
                        "body": f"{result_json['text']}"
                    }
                }
                print("envia el mensaje principal 1")
                enviar_mensajes_whatsapp(data)
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": "Atenciones Médicas"
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "atenmedicpri",
                                        "title": "Primaria"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "telemed",
                                        "title": "Telemedicina"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "atenmeddomi",
                                        "title": "Domiciliaria"
                                    }
                                },
                            ]
                        }
                    }
                }
                print("envia el mensaje principal 2")
                enviar_mensajes_whatsapp(data)
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": numero,
                    "type": "interactive",
                    "interactive":{
                        "type": "button",
                        "body": {
                            "text": "Otros Servicios."
                        },
                        "action": {
                            "buttons":[
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "conmed",
                                        "title": "Consultas Médicas"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "labori",
                                        "title": "Laboratorio"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "ambula",
                                        "title": "Ambulancia"
                                    }
                                },
                            ]
                        }
                    }
                }
                
                print("envia el mensaje principal 3")
                enviar_mensajes_whatsapp(data)
                return True
                
        elif texto == 'no':
            print("entra en el boton que no es afiliado")
            
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Para registrarte, Te Guiaré los pasos que deberas seguir para formar parte de nuestros Afiliados en Medic Plus🩺👨🏼‍⚕️\nComenzamos Escogiendo un plan en el que te gustaria pertenecer, puedes escoger alguno escribiendo el numero correspondiente al plan #️⃣\n1. Plan 1.\n2. Plan 2.\n3. Plan 3.\n4. Plan 4.\n5. Plan 5."
                }
            }
            enviar_mensajes_whatsapp(data)
            get_user_state_register(numero, 'WAITING_FOR_PLAN')
            return True
    
    #mensajes de flujo de registro 
    elif user["state"] == 'WAITING_FOR_PLAN':
        print("entra para ingresar el plan")
        result = get_user_state_register(numero, 'WAITING_FOR_NAME', plan=texto)
        if result == True:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Gracias. Por favor envía tus nombres completos:"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
        else:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el numero correspondiente al plan que te he propuesto🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
    elif user["state"] == 'WAITING_FOR_NAME':
        print("entra para ingresar el nombre del usuario")
        get_user_state_register(numero, 'WAITING_FOR_SURNAME', nombre=texto)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Por favor envía tus apellidos completos:"
            }
        }
        enviar_mensajes_whatsapp(data)
        return True

    elif user["state"] == 'WAITING_FOR_SURNAME':
        print("entra para ingresar el apellido del usuario")
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
        return True

    elif user["state"] == 'WAITING_FOR_ID':
        print("entra para ingresar la cedula del usuario")
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
        return True

    elif user["state"] == 'WAITING_FOR_EMAIL':
        print("entra para ingresar el correo del usuario")
        get_user_state_register(numero, 'REGISTERED', email=texto)
        
        # Aquí guarda el usuario en la base de datos
        with engine.connect() as conn:
            conn.execute(usuarios.insert().values(use_nam=user['nombre'].lower(),  email=texto, nom_usu=user['nombre'].title(),ape_usu=user['apellido'].title(), plan=user['plan'], tel_usu=numero))
            conn.commit()
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
        return True    
    
    #para ir al menu luego de registrarse
    elif "volver" in texto:
        print("entra en volver")
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Gracias por formar parte de los afiliados de MedicPlus🩺. ¿En que puedo ayudarte hoy?📝."
            }
        }
        print("envia el mensaje principal 1")
        enviar_mensajes_whatsapp(data)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "Atenciones Médicas"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "atenmedicpri",
                                "title": "Primaria"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "telemed",
                                "title": "Telemedicina"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "atenmeddomi",
                                "title": "Domiciliaria"
                            }
                        },
                    ]
                }
            }
        }
        print("envia el mensaje principal 2")
        enviar_mensajes_whatsapp(data)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "Otros Servicios."
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "conmed",
                                "title": "Consultas Médicas"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "labori",
                                "title": "Laboratorio"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "ambula",
                                "title": "Ambulancia"
                            }
                        },
                    ]
                }
            }
        }
        
        print("envia el mensaje principal 3")
        enviar_mensajes_whatsapp(data)
        return True
    #respuestas para los afiliados 
    
    #atencion medica primaria 
    elif "atenmedicpri" in texto:
        print("-------------------------------------entra en el elif de atenmedicpri------------------------------------------")
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "¿Desea Generar una Alarma para ser llamado?📞 \nsi seleccionas Si☑️ en minutos recibirias una llamadas de uno de nuestros operadores disponibles \nSi seleccionas No❌ daremos por cancelada tu petición. \nPuedes volver a la pantalla principal Presionando el botón Volver al inicio↩️.  "
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "llamar",
                                "title": "Sí"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "nollamar",
                                "title": "No"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "volver",
                                "title": "Volver al inicio"
                            }
                        },
                    ]
                }
            }
        }
        print("envia el mensaje principal")
        enviar_mensajes_whatsapp(data)
    elif "llamar":
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "interactive",
            "interactive":{
                "type": "button",
                "body": {
                    "text": "La alarma ha sido Generada 📢 recibirá una llamada en los proximos minutos📞⌚"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "volver",
                                "title": "Volver al inicio"
                            }
                        },
                    ]
                }
            }
        }
        enviar_mensajes_whatsapp(data)
        return True
    else:
        print("entra en el else final donde no entiende ningun mensaje ")
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": (
                    "No comprendo muy bien tu mensaje, por favor puedes repetirlo nuevamente.\n \nRecuerda Utilizar los botones proporcionados para poderte ayudar🤖"
                )
            }
        }
        enviar_mensajes_whatsapp(data)
        return True
    
