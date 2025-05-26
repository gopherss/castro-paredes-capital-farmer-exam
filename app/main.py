from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uuid
import re
from contextlib import asynccontextmanager

from app.database import create_tables, SessionLocal
from app.models import Cotizacion

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

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
    # Validaciones
    if len(nombre) < 3 or len(nombre) > 50:
        raise HTTPException(status_code=400, detail="El nombre debe tener entre 3 y 50 caracteres.")

    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="El email no es válido.")

    precios = {"empresa": 1500, "laboral": 2000, "tributaria": 800}
    tipo = {
        "empresa": "Constitución de empresa",
        "laboral": "Defensa laboral",
        "tributaria": "Consultoría tributaria"
    }

    if servicio not in precios:
        raise HTTPException(status_code=400, detail="Servicio no válido.")

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
