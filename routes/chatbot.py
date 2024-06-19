
from send_messages import enviar_mensajes_whatsapp

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
                                "id":"si",
                                "title":"Afiliado"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"no",
                                "title":"Quiero Ser Afiliado"
                            }
                        }
                    ]
                }
            }
        }
        enviar_mensajes_whatsapp(data)
    #respuestas iniciales 
    elif "si" in texto:
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Por favor nos permites el numero de Cédula y verificaremos tu identidad en el sistema.👨🏻‍💻"
            }
        }
        enviar_mensajes_whatsapp(data)
        
    elif "no" in texto:
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
        enviar_mensajes_whatsapp(data)
    
    #respuestas en caso de ser afiliado
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
        enviar_mensajes_whatsapp(data)
    
   