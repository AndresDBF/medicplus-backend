import json
import http
from database.connection import engine
from models.usuarios import usuarios
from models.user_state_register import user_state_register
from models.log import log
from routes.user import get_user_state, get_user_state_register, get_user_state_identification_register
from routes.user import verify_user
from datetime import datetime
from sqlalchemy import insert, select

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
        
def verify_language(numero):
    with engine.connect() as conn:
        result = conn.execute(select(user_state_register.c.language).select_from(user_state_register).where(user_state_register.c.numero==numero)).scalar()
    return result

def get_plan(numero):
    language = verify_language(numero)
    with engine.connect() as conn:
        user =  conn.execute(usuarios.select().where(usuarios.c.tel_usu==numero)).first()
    if language:
        if user is None:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Thank you for deciding to be part of the group of MedicPlus Affiliates. I will guide you through the steps you must follow to be part of our team🩺👨🏼‍⚕️\nWe start by choosing a plan in which you would like to belong, you can choose one by writing the number corresponding to the plan #️⃣\n1. Plan 1.\n2. Plan 2.\n3. Plan 3.\n4. Plan 4.\n5. Plan 5."
                }
            }
            enviar_mensajes_whatsapp(data)
            get_user_state_register(numero, 'WAITING_FOR_PLAN')
            get_user_state_identification_register(numero,'INIT')
            
            return True
        else:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": "We have you registered in our system as a Medic Plus member.👨🏻‍💻 I can provide you with information about our services, help you schedule an appointment or answer general health questions. Select the option you want to consult!"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idservicios",
                                    "title": "Services"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idplanes",
                                    "title": "Plans"
                                }
                            },
                        ]
                    }
                }
            }
            print("envia el mensaje principal 1")
            enviar_mensajes_whatsapp(data)
            get_user_state_identification_register(numero, 'INIT')
            return True
    else:
        if user is None:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Gracias por decidir formar parte del grupo de Afiliados de MedicPlus, Te Guiaré los pasos que deberas seguir para formar parte de nuestro equipo🩺👨🏼‍⚕️\nComenzamos Escogiendo un plan en el que te gustaria pertenecer, puedes escoger alguno escribiendo el número correspondiente al plan #️⃣\n1. Plan 1.\n2. Plan 2.\n3. Plan 3.\n4. Plan 4.\n5. Plan 5."
                }
            }
            enviar_mensajes_whatsapp(data)
            get_user_state_register(numero, 'WAITING_FOR_PLAN')
            get_user_state_identification_register(numero,'INIT')
            
            return True
        else:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": "Contamos con tu registro en nuestro sistema como afiliado de Medic Plus.👨🏻‍💻 Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud. ¡Selecciona la opcion que deseas consultar!"
                    },
                    "action": {
                        "buttons":[
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idservicios",
                                    "title": "Servicios"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idplanes",
                                    "title": "Planes"
                                }
                            },
                        ]
                    }
                }
            }
            print("envia el mensaje principal 1")
            enviar_mensajes_whatsapp(data)
            get_user_state_identification_register(numero, 'INIT')
            return True

#funcion en caso de que quiera pedir los planes y ya se encuentre registrado
def is_affiliate(numero):
    language = verify_language(numero)
    with engine.connect() as conn:
        user = conn.execute(select(usuarios.c.plan).select(usuarios).where(usuarios.c.tel_usu==numero)).first()
    if language:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": f"We have you registered in our system as a Medic Plus member with the plan {user.plan}.👨🏻‍💻 I can provide you with information about our services, help you schedule an appointment or answer general health questions. Select the option you want to consult!"
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
                    "text": "Medical Care"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idatenmedicpri",
                                "title": "Inmediate"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idtelemed",
                                "title": "Telemedicine"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idatenmeddomi",
                                "title": "Domiciliary"
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
                    "text": "Appointments and Studies"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idconmed",
                                "title": "Medical Consultation"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idlabori",
                                "title": "Laboratory"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idimagenologia",
                                "title": "Imaging"
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
                    "text": "Other Services"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idcalloper",
                                "title": "Call an Operator"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "idambula",
                                "title": "Ambulance"
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
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": f"Contamos con tu registro en nuestro sistema como afiliado de Medic Plus con el plan {user.plan}.👨🏻‍💻 Puedo proporcionarte información sobre nuestros servicios, ayudarte a programar una cita o responder preguntas generales de salud. ¡Selecciona la opcion que deseas consultar!"
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
        
def insert_plan(numero, texto):
    language = verify_language(numero)
    result = get_user_state_register(numero, 'WAITING_FOR_NAME', plan=texto)
    if language:
        if result == True:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Thank you. Please send your full names:"
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
                    "body": "I didn't understand your answer very well, remember to only use the number corresponding to the plan that I have proposed to you🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
    else:
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
                    "body": "No comprendí muy bien tu respuesta, recuerda usar solamente el número correspondiente al plan que te he propuesto🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
             
def insert_name(numero, texto):
    language = verify_language(numero)
    result = get_user_state_register(numero, 'WAITING_FOR_SURNAME', nombre=texto)
    if language:
        if result == True:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Please send your full last name:"
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
                    "body": "I didn't understand your answer very well, remember to enter a name longer than 2 characters and using only letters to continue with the process🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True    
    else:
        if result == True:
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
        else:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "No comprendí muy bien tu respuesta, recuerda ingresar un nombre mayor a 2 caracteres y utilizando solamente letras para continuar con el proceso🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True  
           
def insert_last_name(numero, texto):
    language = verify_language(numero)
    result = get_user_state_register(numero, 'WAITING_FOR_ID', apellido=texto)
    if language:
        if result == True:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Please send your identity card:"
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
                    "body": "I didn't understand your answer very well, remember to enter a last name longer than 2 characters and using only letters to continue with the process🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True    
    else:
        if result == True:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Por favor envía tu cédula de identidad:"
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
                    "body": "No comprendí muy bien tu respuesta, recuerda ingresar un apellido mayor a 2 caracteres y utilizando solamente letras para continuar con el proceso🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True    

def insert_identification(numero, texto):
    language = verify_language(numero)
    result = get_user_state_register(numero, 'WAITING_FOR_EMAIL', cedula=texto)
    if language:
        if result == True:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Finally, please send your email:"
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
                    "body": "I didn't understand your answer very well, remember to enter the ID number using only numbers and that they be a minimum of 7 to continue with the process🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
    else:
        if result == True:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "Finalmente, por favor envía tu correo electrónico:"
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
                    "body": "No comprendí muy bien tu respuesta, recuerda ingresar el número de cedula utilizando solamente números y que sean un minimo de 7 para continuar con el proceso🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)
            return True
        
    
def insert_email(numero, texto, user):
    language = verify_language(numero)
    result = get_user_state_register(numero, 'INIT', email=texto)
    if language:
        if result == True:
            # Aquí guarda el usuario en la base de datos
            print(f"el user plan: {user['plan']} y el tipo de dato es {type(user['plan'])}")
            plan = int(user['plan'])
            print(f"asi queda el plan {plan} y este es el tipo de dato {type(plan)}")
            with engine.connect() as conn:
                conn.execute(usuarios.insert().values(use_nam=user['nombre'].lower(),
                                                    email=texto,
                                                    nom_usu=user['nombre'].title(),
                                                    ape_usu=user['apellido'].title(), 
                                                    ced_usu=user['cedula'],
                                                    plan=plan,
                                                    tel_usu=numero))
                conn.commit()
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": "I have successfully processed your information.📝 one of our sales advisors 🧑🏻‍💼👨🏼‍💼 will contact you as soon as possible."
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idvolver",
                                    "title": "Back to top"
                                }
                            }
                        ]
                    }
                }
            }
            with engine.connect() as conn:
                user_affiliate = conn.execute(usuarios.select().where(usuarios.c.tel_usu==numero)).first()

                #enviando un mensaje al operador 
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": "584123175107",
                    "type": "text",
                    "text": {
                        "preview_url": False,
                        "body": f"Hola👋🏼 Soy MedicBot 🤖 asistente virtual de MedicPlus, un nuevo usuario forma parte de nuestro grupo de afiliados de MedicPlus, te he escogido con el fin de cumplir la asesoria☎️ su nombre de afiliado se encuentra registrado como: {user_affiliate.nom_usu} {user_affiliate.ape_usu} y su número de teléfono es: +{numero} \n\nMuchas gracias por tu tiempo✅ "
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
                    "body": "I didn't understand your answer very well, you must enter a valid email address to continue with the process🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)    
            return True 
    else:
        if result == True:
            # Aquí guarda el usuario en la base de datos
            print(f"el user plan: {user['plan']} y el tipo de dato es {type(user['plan'])}")
            plan = int(user['plan'])
            print(f"asi queda el plan {plan} y este es el tipo de dato {type(plan)}")
            with engine.connect() as conn:
                conn.execute(usuarios.insert().values(use_nam=user['nombre'].lower(),
                                                    email=texto,
                                                    nom_usu=user['nombre'].title(),
                                                    ape_usu=user['apellido'].title(), 
                                                    ced_usu=user['cedula'],
                                                    plan=plan,
                                                    tel_usu=numero))
                conn.commit()
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "interactive",
                "interactive":{
                    "type": "button",
                    "body": {
                        "text": "He procesado tu información exitosamente.📝 uno de nuestros asesores de ventas 🧑🏻‍💼👨🏼‍💼 se pondrá en contacto contigo en la brevedad posible."
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "idvolver",
                                    "title": "Volver al Inicio"
                                }
                            }
                        ]
                    }
                }
            }
            with engine.connect() as conn:
                user_affiliate = conn.execute(usuarios.select().where(usuarios.c.tel_usu==numero)).first()

                #enviando un mensaje al operador 
                data = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": "584123175107",
                    "type": "text",
                    "text": {
                        "preview_url": False,
                        "body": f"Hola👋🏼 Soy MedicBot 🤖 asistente virtual de MedicPlus, un nuevo usuario forma parte de nuestro grupo de afiliados de MedicPlus, te he escogido con el fin de cumplir la asesoria☎️ su nombre de afiliado se encuentra registrado como: {user_affiliate.nom_usu} {user_affiliate.ape_usu} y su número de teléfono es: +{numero} \n\nMuchas gracias por tu tiempo✅ "
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
                    "body": "No comprendí muy bien tu respuesta, debes ingresar una direccion de correo válida para continuar con el proceso🤖👨🏻‍💻"
                }
            }
            enviar_mensajes_whatsapp(data)    
            return True 
    