from fastapi import FastAPI, Request, HTTPException, status, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, DateTime, Text
from database.connection import engine
from models.log import log

from models.roles import roles
from models.usuarios import usuarios
from models.user_roles import user_roles
from models.user_state_register import user_state_register
from models.data_aten_med_domi import data_aten_med_domi
from models.data_consultas import data_consultas
from models.data_imagenologia import data_imagenologia
from config.chatbot import chatbot

from routes.data.data import data

app = FastAPI()
app.title = "Documentacion Medic plus"

app.include_router(chatbot, tags=["Webhook Whatsapp"])
app.include_router(data, tags=["data user"])
