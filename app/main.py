from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uuid
from contextlib import asynccontextmanager

from app.database import create_tables, SessionLocal
from app.models import Cotizacion

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
    precio = precios[servicio]

    db = SessionLocal()
    cotizacion = Cotizacion(
        numero=numero, nombre=nombre, email=email,
        tipo_servicio=tipo[servicio], precio=precio, fecha=fecha,
    )
    db.add(cotizacion)
    db.commit()
    db.refresh(cotizacion)

    return JSONResponse({
        "numero": numero,
        "nombre": nombre,
        "email": email,
        "tipo_servicio": tipo[servicio],
        "precio": precio,
        "fecha": fecha
    })
