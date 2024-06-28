from fastapi import Request, HTTPException, status, Query, APIRouter
from fastapi.responses import JSONResponse

from database.connection import engine

from models.log import log
from models.usuarios import usuarios
from models.data_aten_med_domi import data_aten_med_domi
from models.data_consultas import data_consultas
from models.data_imagenologia import data_imagenologia

from sqlalchemy import text, select, insert

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
    
@data.post("/api/insert-baremo/")
async def insert_baremo():
    
    queries_domiciliary = [
        "INSERT INTO data_aten_med_domi  (id, hor_diu, des_dom, pre_amd) VALUES (1, TRUE, 'ANTOLIN', 70);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (2, FALSE, 'ANTOLIN', 80);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (3, TRUE, 'ARISMENDI', 60);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (4, FALSE, 'ARISMENDI', 70);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (5, TRUE, 'DIAZ', 70);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (6, FALSE, 'DIAZ', 80);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (7, TRUE, 'GARCIA', 60);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (8, FALSE, 'GARCIA', 70);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (9, TRUE, 'GOMEZ', 70);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (10, FALSE, 'GOMEZ', 80);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (11, TRUE, 'MANEIRO', 55);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (12, FALSE, 'MANEIRO', 60);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (13, TRUE, 'MARCANO', 70);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (14, FALSE, 'MARCANO', 80);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (15, TRUE, 'MARIÑO', 50);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (16, FALSE, 'MARIÑO', 55);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (17, TRUE, 'PENINSULA DE MACANAO', 80);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (18, FALSE, 'PENINSULA DE MACANAO', 90);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (19, TRUE, 'TUBORES', 80);",
        "INSERT INTO data_aten_med_domi (id, hor_diu, des_dom, pre_amd) VALUES (20, FALSE, 'TUBORES', 90);"
    ]
    
    query_consult =[
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (1, 'CONSULTA CARDIOLOGIA', 25);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (2, 'CONSULTA CIRUGIA GENERAL', 30);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (3, 'CONSULTA DERMATOLOGIA', 40);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (4, 'CONSULTA GASTROENTEROLOGIA', 30);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (5, 'CONSULTA GINECOLOGIA', 25);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (6, 'CONSULTA GINEOBSTETRICIA', 25);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (7, 'CONSULTA MASTOLOGIA', 50);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (8, 'CONSULTA MEDICINA GENERAL', 15);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (9, 'CONSULTA MEDICINA INTERNA', 25);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (10, 'CONSULTA NEFROLOGIA', 30);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (11, 'CONSULTA NUTRICIONISTA', 30);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (12, 'CONSULTA OFTALMOLOGIA', 30);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (13, 'CONSULTA OTORRINOLARINGOLOGIA', 40);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (14, 'CONSULTA PEDIATRIA', 25);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (15, 'CONSULTA TRAUMATOLOGIA', 30);",
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (16, 'CONSULTA UROLOGIA', 30);",
    ]
    
    query_imagenologia = [
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (1, 'DOPPLER', 'ABDOMINAL', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (2, 'DOPPLER', 'ARTERIAL (1 EXTREMIDAD)', 50);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (3, 'DOPPLER', 'ARTERIAL (2 EXTREMIDADES)', 100);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (4, 'DOPPLER', 'ARTERIAL Y VENOSO (1 EXTREMIDAD)', 50);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (5, 'DOPPLER', 'ARTERIAL Y VENOSO (2 EXTREMIDADES)', 100);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (6, 'DOPPLER', 'CAROTÍDEO', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (7, 'DOPPLER', 'DE PENE', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (8, 'DOPPLER', 'HEPATICO', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (9, 'DOPPLER', 'PARTES BLANDAS', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (10, 'DOPPLER', 'PELVICO', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (11, 'DOPPLER', 'RENAL', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (12, 'DOPPLER', 'TESTICULAR', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (13, 'DOPPLER', 'TIROIDES', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (14, 'DOPPLER', 'TRANSVAGINAL', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (15, 'DOPPLER', 'VENOSO (1 EXTREMIDAD)', 50);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (16, 'DOPPLER', 'VENOSO (2 EXTREMIDADES)', 100);",        
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (17, 'ECO PARTES BLANDAS', 'PARTES BLANDAS', 20);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (18, 'ECOCARDIOGRAMA', 'ECOCARDIOGRAMA', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (19, 'ECOSOGRAMA', 'RENALES Y PELVICOS', 45);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (20, 'ECOSONOGRAMA', 'ABDOMINAL', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (21, 'ECOSONOGRAMA', 'ABDOMINO PELVICO', 50);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (22, 'ECOSONOGRAMA', 'MAMARIO', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (23, 'ECOSONOGRAMA', 'MIEMBRO INFERIOR', 60);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (24, 'ECOSONOGRAMA', 'MIEMBRO SUPERIOR', 60);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (25, 'ECOSONOGRAMA', 'OBSTETRICO', 20);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (26, 'ECOSONOGRAMA', 'PELVICO', 20);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (27, 'ECOSONOGRAMA', 'RENAL', 20);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (28, 'ECOSONOGRAMA', 'RENAL PROSTATICO', 50);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (29, 'ECOSONOGRAMA', 'RENAL VESICAL', 50);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (30, 'ECOSONOGRAMA', 'TESTICULAR', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (31, 'ECOSONOGRAMA', 'TIROIDEO', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (32, 'ECOSONOGRAMA', 'TRANSVAGINAL', 35);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (33, 'RX', 'ABDOMEN SIMPLE 1P', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (34, 'RX', 'ABDOMEN SIMPLE 1P BALON GASTRICO', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (35, 'RX', 'ABDOMEN SIMPLE 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (36, 'RX', 'ABDOMEN SIMPLE DE PIE O ACOSTADO', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (37, 'RX', 'ANTEBRAZO DERECHO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (38, 'RX', 'ANTEBRAZO IZQUIERDO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (39, 'RX', 'ART COXOFEMORAL CADERA DERECHA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (40, 'RX', 'ART COXOFEMORAL CADERA IZQUIERDA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (41, 'RX', 'ART SACROILIACAS', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (42, 'RX', 'ART TEMPOROMAXILAR (AMBAS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (43, 'RX', 'ARTICULACIÓN TEMPOROMANDIBULAR IZQUIERDA, 1 PROYECCIÓN BA, 1 PROYECCIÓN BC', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (44, 'RX', 'CADERA AP Y RANA (AMBAS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (45, 'RX', 'CALCANEO 2P (AMBOS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (46, 'RX', 'CALCANEO DERECHO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (47, 'RX', 'CALCANEO DERECHO LAT Y AXIAL', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (48, 'RX', 'CALCANEO IZQUIERDO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (49, 'RX', 'CALCANEO IZQUIERDO LAT Y AXIAL', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (50, 'RX', 'CALCANEO LAT Y AXIAL (AMBOS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (51, 'RX', 'CERVICAL 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (52, 'RX', 'CLAVICULA 1P (AMBAS)', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (53, 'RX', 'CLAVICULA DERECHA 1P', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (54, 'RX', 'CLAVICULA IZQUIERDA 1P', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (55, 'RX', 'CODO DERECHO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (56, 'RX', 'CODO IZQUIERDO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (57, 'RX', 'COLUMNA CERVICAL 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (58, 'RX', 'COLUMNA CERVICAL 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (59, 'RX', 'COLUMNA CERVICAL 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (60, 'RX', 'COLUMNA CERVICAL AP· LAT Y ODONTOIDES', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (61, 'RX', 'COLUMNA DORSAL 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (62, 'RX', 'COLUMNA DORSAL 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (63, 'RX', 'COLUMNA LUMBAR 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (64, 'RX', 'COLUMNA LUMBAR 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (65, 'RX', 'COLUMNA LUMBAR SACRA 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (66, 'RX', 'COLUMNA LUMBO SACRA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (67, 'RX', 'COLUMNA SACRO COCCIGEA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (68, 'RX', 'CRANEO 2P: AP Y LATERAL', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (69, 'RX', 'CRANEO 3P: AP, LATERAL Y TOWN', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (70, 'RX', 'CRANEO 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (71, 'RX', 'CRANEO ORBITA DERECHA 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (72, 'RX', 'CRANEO ORBITA IZQUIERDA 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (73, 'RX', 'DE ARTICULACIÓN TEMPOROMANDIBULAR DERECHA 1 PROYECCIÓN BA Y UNA BC', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (74, 'RX', 'DEDO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (75, 'RX', 'ESCAFOIDES 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (76, 'RX', 'ESCAPULA (AMBAS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (77, 'RX', 'ESCAPULA DERECHA 1P', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (78, 'RX', 'ESCAPULA IZQUIERDA 1P', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (79, 'RX', 'ESTERNON 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (80, 'RX', 'FEMUR 2P (AMBOS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (81, 'RX', 'FEMUR DERECHO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (82, 'RX', 'FEMUR IZQUIERDO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (83, 'RX', 'HOMBRO 1P (AMBOS)', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (84, 'RX', 'HOMBRO 2P (AMBOS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (85, 'RX', 'HOMBRO AXIAL (AMBOS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (86, 'RX', 'HOMBRO AXIAL 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (87, 'RX', 'HOMBRO DERECHO 1P', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (88, 'RX', 'HOMBRO DERECHO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (89, 'RX', 'HOMBRO DERECHO 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (90, 'RX', 'HOMBRO DERECHO 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (91, 'RX', 'HOMBRO IZQUIERDO 1P', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (92, 'RX', 'HOMBRO IZQUIERDO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (93, 'RX', 'HOMBRO IZQUIERDO 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (94, 'RX', 'HOMBRO IZQUIERDO 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (95, 'RX', 'HOMBRO TRES PROYECCIONES (AMBOS)', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (96, 'RX', 'HUESOS PROPIOS NASALES 3P: WATER, LATERAL DERECHA Y LATERAL IZQUIERDA', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (97, 'RX', 'HUMERO DERECHO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (98, 'RX', 'HUMERO IZQUIERDO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (99, 'RX', 'MANO 2P (AMBAS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (100, 'RX', 'MANO AP-OBLICUA', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (101, 'RX', 'MANO AP-OBLICUA (AMBAS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (102, 'RX', 'MANO DERECHA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (103, 'RX', 'MANO DERECHA 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (104, 'RX', 'MANO IZQUIERDA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (105, 'RX', 'MANO IZQUIERDA 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (106, 'RX', 'MASTOIDES', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (107, 'RX', 'MAXILAR INFERIOR (MANDIBULA)', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (108, 'RX', 'MUNECA DERECHA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (109, 'RX', 'MUNECA IZQUIERDA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (110, 'RX', 'PELVIS 1P PANORAMICA', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (111, 'RX', 'PIE 2P (AMBOS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (112, 'RX', 'PIE 3P (AMBOS)', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (113, 'RX', 'PIE CON APOYO 2P (AMBOS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (114, 'RX', 'PIE DERECHO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (115, 'RX', 'PIE DERECHO 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (116, 'RX', 'PIE DERECHO CON APOYO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (117, 'RX', 'PIE IZQUIERDO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (118, 'RX', 'PIE IZQUIERDO 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (119, 'RX', 'PIE IZQUIERDO CON APOYO 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (120, 'RX', 'RINOFARINGE 2P: LATERALES BOCA ABIERTA Y BOCA CERRADA', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (121, 'RX', 'RODILLA 2P CON APOYO', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (122, 'RX', 'RODILLA 2P CON APOYO (AMBAS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (123, 'RX', 'RODILLA 2P (AMBAS)', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (124, 'RX', 'RODILLA DERECHA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (125, 'RX', 'RODILLA DERECHA 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (126, 'RX', 'RODILLA DERECHA AXIAL', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (127, 'RX', 'RODILLA IZQUIERDA 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (128, 'RX', 'RODILLA IZQUIERDA 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (129, 'RX', 'RODILLA IZQUIERDA AXIAL', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (130, 'RX', 'SENOS PARANASALES 3P: WATERS, CAULDWELL Y LATERAL', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (131, 'RX', 'SENOS PARANASALES 4P: WATERS, CAULDWELL, LATERAL Y NASO FRONTAL', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (132, 'RX', 'SENOS PARANASALES WATER-LATERAL', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (133, 'RX', 'TORAX ABDOMEN Y PELVIS', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (134, 'RX', 'TORAX 1P', 16);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (135, 'RX', 'TORAX 2P', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (136, 'RX', 'TORAX 3P', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (137, 'RX', 'TORAX 4P', 37);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (138, 'RX', 'TORAX EMBARAZADA', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (139, 'RX', 'TORAX INSPIRACION ESPIRACION', 24);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (140, 'RX', 'TORAX Y COSTILLA (AMBAS)', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (141, 'RX', 'TORAX Y COSTILLA DERECHA', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (142, 'RX', 'TORAX Y COSTILLA IZQUIERDA', 30);",
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (143, 'RX', 'VERTEBRAS LUMBO SACRAS Y PELVIS', 37);",
    ]
    
    with engine.connect() as conn:
        data1 = conn.execute(data_aten_med_domi.select()).fetchall()
        data2 = conn.execute(data_consultas.select()).fetchall()
        data3 = conn.execute(data_imagenologia.select()).fetchall()
       
        if len(data1) < 1:   
            print("entra en el if 1")
            try:
                for query in queries_domiciliary:
                    conn.execute(text(query))
                    conn.commit()
                print("ingresa los primeros datos")
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
       
        if len(data2) < 1:
            print("entra en el if 2")
            try:
                for query in query_consult:
                    conn.execute(text(query))
                    conn.commit()
                print("ingresa los segundos datos")
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
        if len(data3) < 1:
            print("entra en el if 3")
            try:
                for query in query_imagenologia:
                    conn.execute(text(query))
                    conn.commit()
                print("ingresa los terceros datos")
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
        
    return JSONResponse(content={"message": "datos insertados"}, status_code=status.HTTP_201_CREATED)