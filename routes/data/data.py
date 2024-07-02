from fastapi import Request, HTTPException, status, Query, APIRouter
from fastapi.responses import JSONResponse

from database.connection import engine

from models.log import log
from models.usuarios import usuarios
from models.data_aten_med_domi import data_aten_med_domi
from models.data_consultas import data_consultas
from models.data_imagenologia import data_imagenologia
from models.data_laboratorios import data_laboratorios
from models.data_planes import data_planes

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
        "INSERT INTO data_consultas(id, tip_con, pre_con) VALUES (16, 'CONSULTA UROLOGIA', 30);"
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
        "INSERT INTO data_imagenologia (id, tip_con, des_pru, pre_pru) VALUES (143, 'RX', 'VERTEBRAS LUMBO SACRAS Y PELVIS', 37);"
    ]
    
    query_lab = [
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (1, 'AC ANTI GLIADINA DEAMINADA IGA', 24);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (2, 'AC ANTI GLIADINA DEAMINADA IGG', 24);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (3, 'AC ANTI TRANSGLUTAMINASA IGA', 22);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (4, 'AC ANTI TRANSGLUTAMINASA IGG', 22);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (5, 'AC ANTI-BETA 2 GLICOPROTEINA IGG', 17);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (6, 'AC ANTI-BETA 2 GLICOPROTEINA IGM', 17);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (7, 'AC ANTI-FOSFOLIPIDOS IGG', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (8, 'AC ANTI-FOSFOLIPIDOS IGM', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (9, 'AC ANTI-MUSCULO LISO (ANTI-ASMA)', 25);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (10, 'ACIDO FOLICO (FOLATO)', 17);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (11, 'ACIDO URICO EN ORINA', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (12, 'ACIDO URICO EN ORINA DE 24H', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (13, 'ACIDO URICO EN ORINA PARCIAL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (14, 'ACIDO URICO SERICO', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (15, 'ACIDO VALPROICO', 28);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (16, 'ADA (ADENOSINADEAMINASA) LCR', 30);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (17, 'ADA (ADENOSINADEAMINASA) SUERO', 30);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (18, 'ALBUMINA', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (19, 'ALFAFETOPROTEINA (AFP)', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (20, 'ALFAFETOPROTEINA EN LCR', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (21, 'AMILASA EN ORINA 24H', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (22, 'AMILASA EN ORINA PARCIAL', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (23, 'AMILASA SERICA', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (24, 'ANCA MPO', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (25, 'ANCA PR3', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (26, 'ANTI CCP', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (27, 'ANTI TPO', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (28, 'ANTICUERPOS ANTICARDIOLIPINA IGG-IGM', 26);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (29, 'ANTICUERPOS ANTI-CARDIOLIPINAS IGA', 26);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (30, 'ANTICUERPOS ANTIFOSFOLIPIDOS IGG-IGM', 24);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (31, 'ANTICUERPOS ANTINUCLEARES (ANA)', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (32, 'ANTICUERPOS ANTITIROIDEOS', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (33, 'ANTI-DNA', 27);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (34, 'ANTIESTREPTOLISINA O (ASTO)', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (35, 'ANTIGENO CARCINOEMBRIONARIO (CEA)', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (36, 'ANTIGENO DE SUPERFICIE AGHBS', 7);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (37, 'ANTIGENO PROSTATICO LIBRE (PSA LIBRE)', 9);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (38, 'ANTIGENO PROSTATICO TOTAL (PSA TOTAL)', 9);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (39, 'ANTI-PEPTIDO CITRULINADO CICLICO', 28);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (40, 'APOLIPOPROTEINA A-1 (APO-A1)', 62);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (41, 'AZUCARES REDUCTORES', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (42, 'BETA 2 MICROGLOBULINA EN ORINA 24 H', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (43, 'BILIRRUBINA FRACCIONADA', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (44, 'BILIRRUBINA TOTAL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (45, 'BILIRRUBINA TOTAL-FRACC.', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (46, 'BK DE ESPUTO', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (47, 'BK DIRECTO COLORACION ZIEHL NEELSEN', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (48, 'BK SERIADO', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (49, 'BNP PEPTIDO NATRIURETICO', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (50, 'CA 125 LCR', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (51, 'CA 15-3', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (52, 'CA 15-3 LCR', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (53, 'CA 19-9', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (54, 'CA-125', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (55, 'CALCIO EN ORINA DE 24H', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (56, 'CALCIO EN ORINA PARCIAL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (57, 'CALCIO EN SANGRE', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (58, 'CAP. FIJACION DE HIERRO', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (59, 'CARGA DE GLICOLAB', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (60, 'CEA EN LCR', 24);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (61, 'CELULAS L.E.', 8);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (62, 'CH50 COMPLEMENTO HEMOLITICO', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (63, 'CHAGAS (MACHADO GUERRERO)', 13);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (64, 'CHLAMYDIA PNEUMONIAE IGG', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (65, 'CHLAMYDIA PNEUMONIE IGM', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (66, 'CHLAMYDIA TRACHOMATIS IGA', 11);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (67, 'CHLAMYDIA TRACHOMATIS IGG', 11);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (68, 'CHLAMYDIA TRACHOMATIS IGM', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (69, 'CISTICERCO EN LCR', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (70, 'CISTICESCO EN SUERO', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (71, 'CITOMEGALOVIRUS IGG', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (72, 'CITOMEGALOVIRUS IGM', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (73, 'CK', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (74, 'CK-MB', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (75, 'CLORO', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (76, 'CLORO EN ORINA', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (77, 'COCAINA', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (78, 'COLERA INVESTIGACION EN HECES', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (79, 'COLESTEROL HDL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (80, 'COLESTEROL LDL', 1);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (81, 'COLESTEROL TOTAL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (82, 'COLESTEROL TOTAL Y FRACCIONADO', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (83, 'COLESTEROL VLDL', 1);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (84, 'COMPLEMENTO C3', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (85, 'COMPLEMENTO C4', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (86, 'COMPLEMENTO CH 50', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (87, 'COMPLEMENTO CH 50 LCR', 52);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (88, 'CONTAJE MANUAL DE PLAQUETAS', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (89, 'COOMBS DIRECTO', 8);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (90, 'COOMBS INDIRECTO', 8);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (91, 'COPROCULTIVO', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (92, 'CORTISOL (AM)', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (93, 'CORTISOL (PM)', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (94, 'COVID 19. SARS-COV-2 IGG/IGM', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (95, 'COVID 19. SARS-COV-2 NASOFARINGEO', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (96, 'CREATININA', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (97, 'CREATININA EN ORINA DE 24 H.', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (98, 'CREATININA EN ORINA PARCIAL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (99, 'CRYPTOSPORIDIUM INVESTIGACION EN HECES', 18);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (100, 'CULTIVO DE ABSCESO', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (101, 'CULTIVO DE ESPUTO', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (102, 'CULTIVO DE EXUDADO FARINGEO', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (103, 'CULTIVO DE HONGOS', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (104, 'CULTIVO DE LIQUIDOS', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (105, 'CULTIVO DE PUNTA DE CATETER', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (106, 'CULTIVO DE SECRECION DE HERIDAS', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (107, 'CULTIVO DE SECRECION DE MAMA', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (108, 'CULTIVO DE SECRECION DE ULCERAS', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (109, 'CULTIVO DE SECRECION URETRAL', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (110, 'CULTIVO DE SECRECION VAGINAL', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (111, 'CULTIVO DE SECRECIONES OTRAS', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (112, 'CULTIVO DE TEJIDOS Y PARTES BLANDAS', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (113, 'CULTIVO SECRECION OCULAR', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (114, 'CULTIVO SECRECION OTICA', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (115, 'CULTURETE', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (116, 'DEHIDREPIANDOSTERONA (DHEA)', 16);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (117, 'DEHIDREPIANDOSTERONA S (DHEAS)', 16);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (118, 'DENGUE IGG/IGM', 8);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (119, 'DIGOXINA', 18);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (120, 'DIMERO D', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (121, 'ELECTROLITOS EN ORINA', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (122, 'ELECTROLITOS SERICOS', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (123, 'EPAMIN (FENITOINA)', 30);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (124, 'EPSTEIN BARR VIRUS IGG', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (125, 'EPSTEIN BARR VIRUS IGM', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (126, 'ESPERMATOGRAMA', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (127, 'ESPERMOCULTIVO (1ERA, 2DA ORINA Y SEMEN)', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (128, 'ESTRADIOL', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (129, 'ESTRIOL', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (130, 'EXUDADO FARINGEO', 13);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (131, 'FERRITINA', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (132, 'FIBRINOGENO', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (133, 'FOSFATASA ALCALINA', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (134, 'FOSFORO EN ORINA DE 24H', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (135, 'FOSFORO EN ORINA PARCIAL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (136, 'FOSFORO SERICO', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (137, 'FROTIS DE SANGRE PERIFERICA', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (138, 'FTA ABS', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (139, 'FTA LCR', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (140, 'GAMMA GLUTAMIL TRANSFERASA (GGT)', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (141, 'GASES ARTERIALES', 55);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (142, 'GASES VENOSOS', 55);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (143, 'GLICEMIA 120 MINUTOS', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (144, 'GLICEMIA 180 MINUTOS', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (145, 'GLICEMIA 240 MINUTOS', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (146, 'GLICEMIA 30 MINUTOS', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (147, 'GLICEMIA 60 MINUTOS', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (148, 'GLICEMIA 90 MINUTOS', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (149, 'GLICEMIA BASAL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (150, 'GLICEMIA POSTCARGA', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (151, 'GLICEMIA POST-PRANDIAL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (152, 'GRUPO SANGUINEO', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (153, 'HCG CUANTIFICADA', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (154, 'HECES', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (155, 'HECES AZUCARES REDUCTORES', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (156, 'HELICOBACTER PYLORI EN HECES', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (157, 'HELICOBACTER PYLORI IGG', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (158, 'HELICOBACTER PYLORI IGM', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (159, 'HEMATOLOGIA COMPLETA', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (160, 'HEMOCULTIVO', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (161, 'HEMOGLOBINA GLICOSILADA A1C', 14);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (162, 'HEMOGLOBINA-HEMATOCRITOS', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (163, 'HEPATITIS A IGG', 6);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (164, 'HEPATITIS A IGM', 6);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (165, 'HEPATITIS B ANTICORE TOTAL', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (166, 'HEPATITIS B ANTIGENO SUPERFICIE', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (167, 'HEPATITITS C', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (168, 'HERPES I IGG', 14);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (169, 'HERPES I IGG LCR', 30);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (170, 'HERPES I IGM', 14);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (171, 'HERPES I IGM LCR', 30);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (172, 'HERPES II IGG', 14);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (173, 'HERPES II IGG EN LCR', 30);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (174, 'HERPES II IGM', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (175, 'HERPES II IGM EN LCR', 30);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (176, 'HIERRO SERICO', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (177, 'HIV', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (178, 'HIV CUARTA GENERACION', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (179, 'HIV LCR', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (180, 'HORMONA DE CRECIMIENTO 20 MINUTOS', 26);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (181, 'HORMONA DE CRECIMIENTO 40 MINUTOS', 26);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (182, 'HORMONA FOLICULO ESTIMULANTE (FSH) (FEMENINO) IMF', 9);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (183, 'HORMONA LUTEINIZANTE (LH) (FEMENINO) IMF', 9);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (184, 'IGE (INMONOGLOBULINA E)', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (185, 'INMUNOGLOBULINA G LCR', 35);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (186, 'INSULINA 180 MINUTOS', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (187, 'INSULINA 240 MINUTOS', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (188, 'INSULINA 30 MINUTOS', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (189, 'INSULINA 60 MINUTOS', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (190, 'INSULINA 90 MINUTOS', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (191, 'INSULINA BASAL', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (192, 'INSULINA POST PRANDIAL', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (193, 'INSULINA POSTCARGA 75GR', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (194, 'KIT CULTURETTE', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (195, 'KIT MEDIO DE HEMOCULTIVO', 7);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (196, 'KIT TOMA DE MUESTRA', 1);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (197, 'LACTATO DESHIDROGENOSA (LDH)', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (198, 'LEUCOGRAMA FECAL', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (199, 'LIPASA', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (200, 'LITIO', 30);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (201, 'MAGNESIO', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (202, 'MARIHUANA', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (203, 'MICROALBUMINURIA EN ORINA 24 H.', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (204, 'MICROALBUMINURIA EN ORINA PARCIAL', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (205, 'MONO TEST RAPID TEST', 6);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (206, 'MYCOPLASMA PNEUMONIAE IGG', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (207, 'MYCOPLASMA PNEUMONIE IGM', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (208, 'NIVELES DE CARBAMAZEPINA', 33);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (209, 'NIVELES DE FENOBARBITAL', 33);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (210, 'ORINA COMPLETA', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (211, 'PANEL ALERGICO ALIMENTOS', 74);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (212, 'PANEL ALERGICO INHALANTES', 74);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (213, 'PARATHORMONA (PTH)', 25);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (214, 'PEPTIDO C', 13);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (215, 'PEPTIDO C POST PANDRIAL', 13);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (216, 'PERFIL 20', 18);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (217, 'PERFIL CERTIFICADO DE SALUD', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (218, 'PERFIL COVID', 40);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (219, 'PERFIL HELLP', 25);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (220, 'PERFIL HEPÁTICO', 17);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (221, 'PERFIL HORMONAL FEMENINO', 50);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (222, 'PERFIL HORMONAL MASCULINO', 50);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (223, 'PERFIL LIPIDICO', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (224, 'PERFIL NIÑO SANO', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (225, 'PERFIL OBSTRETICO', 25);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (226, 'PERFIL PEDIATRICO', 18);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (227, 'PERFIL POST-VACACIONAL', 8);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (228, 'PERFIL PRE-EMPLEO (F)', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (229, 'PERFIL PRE-EMPLEO (M)', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (230, 'PERFIL PREOPERATORIO/QUIRURGICO', 25);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (231, 'PERFIL PRE-VACACIONAL', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (232, 'PERFIL PROSTATICO', 18);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (233, 'PERFIL RENAL I', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (234, 'PERFIL REUMATICO', 25);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (235, 'PERFIL TIROIDEO (T3 - T4- TSH)', 24);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (236, 'POTASIO', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (237, 'PROCALCITONINA', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (238, 'PROGESTERONA', 9);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (239, 'PROLACTINA (HOMBRE)', 9);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (240, 'PROTEINAS C REACTIVAS (PCR)', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (241, 'PROTEINAS TOTALES', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (242, 'PROTEINAS TOTALES Y FRACC', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (243, 'PROTENURIA EN ORINA DE 24 HORAS', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (244, 'PRUEBA DE EMBARAZO', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (245, 'PT TIEMPO DE PROTROMBINA', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (246, 'PTT TIEMPO DE TROMBOPLASTINA', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (247, 'QUIMICA 1', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (248, 'QUIMICA 2', 7);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (249, 'RA TEST', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (250, 'RA-TEST CUANTITATIVO', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (251, 'RELACION AC. URICO/CREAT ORINA 24H', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (252, 'RELACION CALCIO / CREATININA', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (253, 'RELACION CALCIO CREATININA ORINA PARCIAL', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (254, 'RELACION CALCIO/CREATININA O/24H', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (255, 'RELACION FOSFORO/CREATININA ORINA PARCIAL', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (256, 'RELACION UREA/CREATININA O/24H', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (257, 'RUBEOLA IGG', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (258, 'RUBEOLA IGM', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (259, 'SANGRE OCULTA EN HECES', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (260, 'SARAMPION IGG', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (261, 'SARAMPION IGM', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (262, 'SARS-COV-2 IGG/IGM', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (263, 'SARS-COV-2 NASOFARINGEO', 25);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (264, 'SEROLOGIA DE HONGOS', 46);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (265, 'SEROLOGIA IGG', 14);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (266, 'SEROLOGIA IGM', 14);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (267, 'SODIO', 4);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (268, 'SOMATOMEDINA C (IGF-1)', 24);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (269, 'SUERO PARA PLASMA ( MAX. 10 CC)', 5);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (270, 'T3 LIBRE', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (271, 'T4 LIBRE', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (272, 'TESTOSTERONA LIBRE', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (273, 'TESTOSTERONA TOTAL', 12);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (274, 'TIROGLOBULINA', 11);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (275, 'TOXOPLASMA IGG', 8);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (276, 'TOXOPLASMA IGM', 8);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (277, 'TRANSAMINASA AXALOACETICA (TGO) AST', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (278, 'TRANSAMINASA PIRUVICA (TGP) ALT', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (279, 'TRANSFERRINA', 8);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (280, 'TRIGLICERIDOS', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (281, 'TROPONINA CUALITATIVA', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (282, 'TROPONINA CUANTIFICADA', 15);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (283, 'TSH', 10);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (284, 'UREA', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (285, 'UROCULTIVO', 14);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (286, 'VDRL', 2);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (287, 'VITAMINA B12', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (288, 'VITAMINA D', 20);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (289, 'VSG (VELOCIDAD SEDIMENTACION GLOBULAR)', 3);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (290, 'TOMA DE MUESTRA A DOMICILIO EXTRA URBANO', 40);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (291, 'TOMA DE MUESTRA A DOMICILIO FORANEO', 50);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (292, 'TOMA DE MUESTRA A DOMICILIO SUB URBANO', 30);",
        "INSERT INTO data_laboratorios (id, tip_pru, pre_pru) VALUES (293, 'TOMA DE MUESTRA A DOMICILIO URBANO', 25);"




    ]
    
    query_domi = [
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (1, True, 'ANTOLIN', 70);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (2, False, 'ANTOLIN', 80);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (3, True, 'ARISMENDI', 60);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (4, False, 'ARISMENDI', 70);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (5, True, 'DIAZ', 70);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (6, False, 'DIAZ', 80);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (7, True, 'GARCIA', 60);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (8, False, 'GARCIA', 70);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (9, True, 'GOMEZ', 70);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (10, False, 'GOMEZ', 80);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (11, True, 'MANEIRO', 55);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (12, False, 'MANEIRO', 60);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (13, True, 'MARCANO', 70);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (14, False, 'MARCANO', 80);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (15, True, 'MARIÑO', 50);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (16, False, 'MARIÑO', 55);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (17, True, 'PENINSULA DE MACANAO', 80);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (18, False, 'PENINSULA DE MACANAO', 90);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (19, True, 'TUBORES', 80);",
        "insert into data_aten_med_domi (id, dom_diu, loc_dom, pre_dom) values (20, False, 'TUBORES', 90);"
    ]
    
    with engine.connect() as conn:
        data1 = conn.execute(data_aten_med_domi.select()).fetchall()
        data2 = conn.execute(data_consultas.select()).fetchall()
        data3 = conn.execute(data_imagenologia.select()).fetchall()
        data4 = conn.execute(data_laboratorios.select()).fetchall()
        data5 =  conn.execute(data_aten_med_domi.select()).fetchall()
        
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
        if len(data4) < 1:
            print("entra en el if 4")
            try:
                for query in query_lab:
                    conn.execute(text(query))
                    conn.commit()
                print("ingresa los terceros datos")
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
        if len(data5) < 1:
            print("entra en el if 5")
            try:
                for query in query_domi:
                    conn.execute(text(query))
                    conn.commit()
                print("ingresa los terceros datos")
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
        
        
    return JSONResponse(content={"message": "datos insertados"}, status_code=status.HTTP_201_CREATED)

@data.post("/api/insert-planes/")
async def insert_planes():
    query_plan = [
        """insert into data_planes(id, tip_pla, des_pla) values(1,'Telemedicina','Reinventando el sistema médico de margarita.\nSin citas previas, sin largas esperas.\n\n ¿Qué es telemedicina?\nLa telemedicina es la prestación de servicios de salud utilizando la tecnología que permite la comunicación interactiva en tiempo real entre el paciente, y el médico a distancia.\n En otras palabras, nuestra plataforma te permite realizar una video-consulta con un médico de turno desde donde quiera que estés, sin sacar citas previas. Recibe en tu correo el informe médico y tu receta electrónica al finalizar la consulta.\n\n¡Ingresa desde tu celular, Tablet o computadora, solo con tu número de cedula si eres afiliado!\nServicio disponible gratuito para los afiliados de Medicplus.\nServicio disponible para empresas.\nBeneficios:\n- Video llamada con un médico desde cualquier parte del mundo al instante (SIN CITAS Y SIN LARGAS ESPERAS).\n- Contar con una asistencia médica al instante acompañándolo en todo momento.\n- Video consultas médicas ilimitadas los 365 días del año, sin costo.\n- Recibir a tu correo, recetas electrónicas, ordenes de laboratorio\n- Botón de pánico por chat bot para solicitar atención inmediata por emergencias médicas\n- Chat bot para solicitar y programar servicios adicionales o traslados.');""",
        """insert into data_planes(id, tip_pla, des_pla) values(2, 'Familiar', 'Beneficios Incluidos:\n- Atención médica pre-hospitalaria de emergencia y urgencia.\n- Consulta Médica a domicilio para casos menores.\n- Orientación Médica por video llamada.\n- Consulta Médica Telefónica, a nivel nacional, 24 horas.\n- Auto protegido en casos de accidentes de tránsito, para todos los ocupantes del vehículo.\n- Insumos, medicamentos, equipos y maniobras utilizados en la atención.\n- Traslado del paciente a un centro hospitalario producto de la atención sin costo adicional.\n- Equipo humano profesional completo a bordo de las unidades, equipos e instrumentos médicos de última generación. (Médicos, Técnicos en urgencias médicas, Operadores de Vehículo de Emergencia).\n- Amplio radio de cobertura. Isla de margarita.\n- Sin exámenes médicos de ingreso. Sin límites de edad.\n- Sin límite de atenciones.\n\n En términos simples:\nServicio que protege a toda tu familia 24 horas del día, 7 dias a la semana, 365 días al año. En el caso de una emergencia o urgencia se despacha al lugar donde esté el paciente (dentro del radio de cobertura) una Ambulancia o una Unidad de Avanzada. En casos menores de consulta médica el afiliado puede hacer una video llamada con un médico o solicitar una consulta médica a domicilio (dentro del radio de cobertura) para el diagnóstico y tratamiento. \nTodo el material y los medicamentos que se utilicen en la atención de emergencia y urgencia no llevan costo adicional y en caso de necesitarse el traslado a un hospital producto de la atención este tampoco lleva costo.');""",
        """insert into data_planes(id, tip_pla, des_pla) values(3, 'Area Protegida', 'Nuestro servicio de Área Protegida consiste en la asistencia médica inmediata para toda persona que se encuentre dentro del área de cobertura. Este servicio está especialmente diseñado para su empresa, comercio o institución.\nIncluye la atención ante Emergencias y Urgencias médicas, además del traslado del paciente en caso de ser necesario. Asimismo, contamos con planes diseñados para cada necesidad.\n\n- SERVICIOS ADICIONALES\n- CURSOS DE CAPACITACIÓN CON CERTIFICACIÓN\n- PLAN ESPECIAL PARA EMPLEADOS\n- SERVICIO DE TELEMEDICINA\n- MEDICINA LABORAL\n- COBERTURA DE EVENTOS\n- PROVISIÓN DE CONSULTORIOS MÉDICOS Y/O ENFERMERÍAS\n- SERVICIO EMERGENCIAS A INSTITUCIONES EDUCATIVAS\n\n SERVICIO DIFERENCIAL\n\nPARA INSTITUCIONES EDUCATIVAS\nEste servicio cuenta con móviles exclusivos para la atención de Emergencias y Urgencias a INSTITUCIONES EDUCATIVAS. Unidades de rápida respuesta especialmente equipadas.\n\nMEDICINA LABORAL\nDesde MEDICPLUS buscamos ser aliados estratégicos de las organizaciones y generar vínculos a largo plazo, satisfaciendo las necesidades de las mismas a través de la calidad de nuestro servicio.\nEs por ello que trabajamos a la par de todas las gerencias de Recursos Humanos con nuestro servicio de control de ausentismo. El mismo consiste en la visita médica a domicilio del colaborador para evaluar al mismo.\n\nPLAN ESPECIAL PARA EMPLEADOS\n\nEste servicio le brinda la posibilidad a su empresa, comercio o institución, de proteger a sus empleados también fuera del ámbito del domicilio laboral.');""",
        """insert into data_planes(id, tip_pla, des_pla) values(4, 'Cobertura de Eventos', 'Cobertura médica total para staff, participantes y asistentes de tu evento.\nCubrimos todo tipo de evento, amoldamos nuestro servicio en base a las necesidades del cliente. Cubrimos el evento, montaje y desmontaje. Varias modalidades desde paramédico en sitio + ambulancia por llamado hasta ambulancia en sitio exclusiva Y INSTALACIÓN TIENDAS DE CAMPAÑA para el evento tales como:\n\n- Conciertos\n- Espectáculos\n- Eventos Masivos\n- Lanzamientos\n- Congresos\n- Ferias\n- Bodas\n- Cumpleaños\n- Circuitos de Maratón\n- Rides de Bicicleta\n- Carreras (Auto, moto, offroad, karting) \n\n- Entre otros...');""",
        """insert into data_planes(id, tip_pla, des_pla) values(5, 'Clinica Empresarial', 'Diseño, suministro y manejo de consultorio médico en sus oficinas.\nOfrecemos la organización y manejo completo de la Clínica Empresarial desde los expedientes de historial médico, jornadas de control y seguimiento, hasta la atención de consultas y emergencias médicas en los predios de la empresa.\nBeneficios:\n\n- Equipamiento y adecuación del espacio destinado para la clínica. (Sin costos iniciales)\n- Suministro de insumos, medicamentos, material descartable, necesarios para el tratamiento de pacientes sin costo adicional.\n- Atención de situaciones que se presenten dentro de la empresa que requieran atención médica. \n- Atención personalizada en servicio de consulta médica.\n- Dar seguimiento al funcionamiento de la clínica.\n- Dar seguimiento a la salud y seguridad de todos los colaboradores de la empresa.\n- Creación de Comités de Salud, Seguridad e Higiene en el trabajo.\n- Orientación en prevención de enfermedades laborales.\n- Exámenes de ingreso para el personal y rutinarios.\n- Garantizar 100% la presencia del personal durante las horas establecidas\n\nEntre otros beneficios detallados en la propuesta.');"""
    ]
    with engine.connect() as conn:
        data = conn.execute(data_planes.select()).fetchall()        
        if len(data) < 1:   
            print("entra en el if 1")
            try:
                for query in query_plan:
                    conn.execute(text(query))
                    conn.commit()
                print("inserta los  datos")
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
        return JSONResponse(content={"message": "datos insertados"}, status_code=status.HTTP_201_CREATED)