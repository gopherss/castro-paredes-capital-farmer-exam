from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uuid
from contextlib import asynccontextmanager

from app.database import create_tables, SessionLocal
from app.models import Cotizacion
from app.ia import analizar_con_ia 

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/cotizar")
def cotizar(
    nombre: str = Form(...),
    email: str = Form(...),
    servicio: str = Form(...),
    descripcion: str = Form(...)
):
    precios = {"empresa": 1500, "laboral": 2000, "tributaria": 800}
    tipo = {
        "empresa": "Constitución de empresa",
        "laboral": "Defensa laboral",
        "tributaria": "Consultoría tributaria"
    }

    numero = f"COT-2025-{str(uuid.uuid4())[:8]}"
    fecha = datetime.now().isoformat()
    precio_base = precios[servicio]

    # Llama a la IA para analizar el caso
    resultado_ia = analizar_con_ia(descripcion, tipo[servicio])

    if "error" in resultado_ia:
        return JSONResponse(status_code=500, content={"error": resultado_ia["error"]})

    ajuste = int(resultado_ia.get("ajuste_precio", 0))
    precio_final = int(precio_base * (1 + ajuste / 100))

    # Guarda en la base de datos
    db = SessionLocal()
    cotizacion = Cotizacion(
        numero=numero, nombre=nombre, email=email,
        tipo_servicio=tipo[servicio], precio=precio_final, fecha=fecha
    )
    db.add(cotizacion)
    db.commit()
    db.refresh(cotizacion)

    return JSONResponse({
        "numero": numero,
        "nombre": nombre,
        "email": email,
        "tipo_servicio": tipo[servicio],
        "precio_base": precio_base,
        "ajuste_precio": ajuste,
        "precio_final": precio_final,
        "fecha": fecha,
        "complejidad": resultado_ia.get("complejidad"),
        "servicios_adicionales": resultado_ia.get("servicios_adicionales"),
        "propuesta_texto": resultado_ia.get("propuesta_texto")
    })