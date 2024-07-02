
import json
import http
from database.connection import engine
from models.usuarios import usuarios
from models.data_planes import data_planes
from models.log import log
from models.user_state_register import user_state_register
from routes.user import get_user_state, get_user_state_register, get_user_state_identification_register
from routes.user import verify_user
from datetime import datetime
from sqlalchemy import insert, select, text

def agregar_mensajes_log(texto):
    try:
        texto_str = json.dumps(texto)
     
        with engine.connect() as conn:
            conn.execute(log.insert().values(texto=texto_str, fecha_y_hora=datetime.utcnow()))
            conn.commit()
      
    except Exception as e:
        print(f"Error al guardar el mensaje en el log: {e}")

def enviar_mensajes_whatsapp (data):
    
    data = json.dumps(data)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAOJtyjmw9EBOyJBUw5wn6z8g1uIVktFfdiQUos9qnnRBC78p0xQH6r1UwxuRlYsUqz1mSq3eJI2ZBZAAF37TjWAWUcRuh8EV0xf95oAVlCj29vPqow15SBou9T9ZAIPaA6nP8ZCgYIhKTXeA8tMuVZALiZBnHwo7j9c8fSF2Kvq6PF9QWGpiZBnbnArbTxlwzT"
    }
    
    connection = http.client.HTTPSConnection("graph.facebook.com")
    
    try:
        connection.request("POST", "/v19.0/378961785290654/messages", data, headers)
        response = connection.getresponse()
        response_data = response.read().decode()
        if response.status != 200:
            agregar_mensajes_log(f"Error al enviar mensaje: {response.status} {response.reason} {response_data}")
    except Exception as e:
        print(f"Exception: {e}")
        agregar_mensajes_log(f"Exception al enviar mensaje: {e}")
    finally:
        connection.close()
        
def get_list_plan(numero):
    number = 0
    
    with engine.connect() as conn:
        list_plan = conn.execute(text("select tip_pla from data_planes;")).fetchall()
        print("esto muestra el list imag ", list_plan)
    # Crear un diccionario de mapeo de números a tipos de servicios exactos
    service_map = {}
    data_list = []
    for plan in list_plan:
        number += 1
        service_map[number] = plan.tip_pla  # Mapear número a nombre exacto del servicio
        data_list.append(f"\n{number}. {plan.tip_pla}")
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": f"Puedo proporcionarte la información suficiente sobre nuestros planes para afiliados de MedicPlus🩺👨🏼‍⚕️, escribe el número correspondiente a uno de ellos para poder ayudarte👨🏻‍💻\n{''.join(data_list)}"
        }
    }
    
    enviar_mensajes_whatsapp(data)
    get_user_state_identification_register(numero,'INIT')
    with engine.connect() as conn:
        status_user = conn.execute(user_state_register.select().where(user_state_register.c.numero==numero)).first()
        if status_user.plan != "REGISTERED":
            
            get_user_state_register(numero, 'WAITING_FOR_SERVICE_PLAN')
    
        
    return True

def send_info_plan(numero, plan):
    result = get_user_state_register(numero, 'INIT', plan=plan)
    print("esto trae el result dentro de send info plan: ", result)
    if result == True:
        with engine.connect() as conn:
            get_plan = conn.execute(select(user_state_register.c.plan).select_from(user_state_register).where(user_state_register.c.numero==numero)).scalar()
            info_plan = conn.execute(select(data_planes.c.tip_pla, data_planes.c.des_pla).select_from(data_planes).where(data_planes.c.id==get_plan)).first()
            #en esta linea vendria la consulta para la tabla donde se guardara la informacion de los planes 
        if get_plan == "1":
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "document",
                "document": {
                    "link": "https://amezquimart.online/static/plan/Telemedicina.pdf",
                    "caption": "Plan Telemedicina"
                }
            }
            enviar_mensajes_whatsapp(data)
        
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"Te adjunto un archivo pdf sobre el plan {get_plan}: {info_plan.tip_pla}, finalmente puedes indicarme si deseas formar parte del grupo de Afiliados de MedicPlus y realizariamos en registro en el sistema en base a este plan👨‍💻"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmplan",
                                    "title": "Quiero ser Afiliado"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idplanes",
                                    "title": "Planes"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idvolver",
                                    "title": "Volver al Inicio"
                                }
                            },
                        ]
                    }
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
        if get_plan == "2":
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "document",
                "document": {
                    "link": "https://amezquimart.online/static/plan/Familiar.pdf",
                    "caption": "Plan Familiar"
                }
            }
            enviar_mensajes_whatsapp(data)
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"Te adjunto un archivo pdf sobre el plan {get_plan}: {info_plan.tip_pla}, finalmente puedes indicarme si deseas formar parte del grupo de Afiliados de MedicPlus y realizariamos en registro en el sistema en base a este plan👨‍💻"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmplan",
                                    "title": "Quiero ser Afiliado"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idplanes",
                                    "title": "Planes"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idvolver",
                                    "title": "Volver al Inicio"
                                }
                            },
                        ]
                    }
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
        if get_plan == "3":
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "document",
                "document": {
                    "link": "https://amezquimart.online/static/plan/areaprotegida.pdf",
                    "caption": "Plan Área Protegida"
                }
            }
            enviar_mensajes_whatsapp(data)
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"Te adjunto un archivo pdf sobre el plan {get_plan}: {info_plan.tip_pla}, finalmente puedes indicarme si deseas formar parte del grupo de Afiliados de MedicPlus y realizariamos en registro en el sistema en base a este plan👨‍💻"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmplan",
                                    "title": "Quiero ser Afiliado"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idplanes",
                                    "title": "Planes"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idvolver",
                                    "title": "Volver al Inicio"
                                }
                            },
                        ]
                    }
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
        if get_plan == "4":
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "document",
                "document": {
                    "link": "https://amezquimart.online/static/plan/cobertura_eventos.pdf",
                    "caption": "Plan Cobertura de Eventos"
                }
            }
            enviar_mensajes_whatsapp(data)
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"Te adjunto un archivo pdf sobre el plan {get_plan}: {info_plan.tip_pla}, finalmente puedes indicarme si deseas formar parte del grupo de Afiliados de MedicPlus y realizariamos en registro en el sistema en base a este plan👨‍💻"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmplan",
                                    "title": "Quiero ser Afiliado"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idplanes",
                                    "title": "Planes"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idvolver",
                                    "title": "Volver al Inicio"
                                }
                            },
                        ]
                    }
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
        if get_plan == "5":
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "document",
                "document": {
                    "link": "https://amezquimart.online/static/plan/clinica_empresarial.pdf",
                    "caption": "Plan Clínica Empresarial"
                }
            }
            enviar_mensajes_whatsapp(data)
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": f"Te adjunto un archivo pdf sobre el plan {get_plan}: {info_plan.tip_pla}, finalmente puedes indicarme si deseas formar parte del grupo de Afiliados de MedicPlus y realizariamos en registro en el sistema en base a este plan👨‍💻"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idconfirmplan",
                                    "title": "Quiero ser Afiliado"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idplanes",
                                    "title": "Planes"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idvolver",
                                    "title": "Volver al Inicio"
                                }
                            },
                        ]
                    }
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
                "body": "No comprendí muy bien tu respuesta, recuerda ingresar el número al plan que te he proporcionado para continuar con el proceso🤖👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        get_user_state_register(numero, 'WAITING_FOR_SERVICE_PLAN')
        return True   
    
def send_name_affiliate(numero):
    print("entra en send_name_affiliate")
    with engine.connect() as conn:
        user = conn.execute(select(usuarios.c.plan).select_from(usuarios).where(usuarios.c.tel_usu==numero)).scalar()
        print("este es el user ", user)
    if user:
        with engine.connect() as conn:
            name_plan = conn.execute(select(data_planes.c.tip_pla).select_from(data_planes).where(data_planes.c.id==user)).scalar()
        print("entra en el if")
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": f"Contamos con tu registro en nuestro sistema como afiliado de Medic Plus con el plan {name_plan}.👨🏻‍💻 Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud. ¡Selecciona la opcion que deseas consultar!"
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
                                "id": "idatenmedicpri",
                                "title": "Inmediata"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idtelemed",
                                "title": "Telemedicina"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idatenmeddomi",
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
                    "text": "Citas y Estudios"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconmed",
                                "title": "Consultas Médicas"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idlabori",
                                "title": "Laboratorio"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idimagenologia",
                                "title": "Imagenología"
                            }
                        }
                    ]
                }
            }
        }
                    
        print("envia el mensaje principal 3")
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
                                "id": "idcalloper",
                                "title": "Llamar un Operador"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idambula",
                                "title": "Ambulancia"
                            }
                        },
                    ]
                }
            }
        }
                    
        print("envia el mensaje principal 4")
        enviar_mensajes_whatsapp(data)
        return True
    else:
        print("entra en el else")
        get_user_state_register(numero, 'WAITING_FOR_NAME')

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Comencemos con el registro para afiliados de Medicplus, Por favor envía tus nombres completos:"
            }
        }
        enviar_mensajes_whatsapp(data)
        return True
    