from fastapi import Request, HTTPException, status, Query, APIRouter
from fastapi.responses import JSONResponse

from database.connection import engine

from models.log import log
from models.usuarios import usuarios

data = APIRouter(tags=["Data User"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@data.post("/api/insert-data/")
async def insert_data_users():
    with engine.connect() as conn:
        try:
            conn.execute(usuarios.insert().values([
                    #calificacion del doctor 
                    {"use_nam": "andresoto", "email": "andres200605@gmail.com", "nom_usu": "Andres David", "ape_usu": "Becerra Flores", "ced_usu": "27815414", "plan": 1, "tel_usu": "584147201892"},
                    {"use_nam": "angel1", "email": "angelprueba@yopmail.com", "nom_usu": "Angel", "ape_usu": "Arias", "ced_usu": "24694899", "plan": 1, "tel_usu": "584147231785"},
                    {"use_nam": "usuario1", "email": "usuarioprueba1@yopmail", "nom_usu": "usuario", "ape_usu": "prueba", "ced_usu": "20427937", "plan": 1, "tel_usu": "584147224455"},
                    {"use_nam": "usuario2", "email": "usuarioprueba2@yopmail", "nom_usu": "usuario2", "ape_usu": "prueba2", "ced_usu": "10173037", "plan": 1, "tel_usu": "584147224451"},
                    {"use_nam": "usuario3", "email": "usuarioprueba3@yopmail", "nom_usu": "usuario3", "ape_usu": "prueba3", "ced_usu": "9227785", "plan": 1, "tel_usu": "584147224450"}]))
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
        
    return JSONResponse(content={
        "message": "datos insertados"
    }, status_code=status.HTTP_201_CREATED)
 
