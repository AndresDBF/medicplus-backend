from fastapi import FastAPI, Request, HTTPException, status, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, DateTime, Text
from database.connection import engine
from models.log import log
from models.roles import roles
from models.user_roles import user_roles
from models.usuarios import usuarios

from routes.webhook import chatbot

app = FastAPI()

app.include_router(chatbot, tags=["Webhook Whatsapp"])
