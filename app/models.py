from sqlalchemy import Column, Integer, String
from app.database import Base

class Cotizacion(Base):
    __tablename__ = "cotizaciones"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True)
    nombre = Column(String)
    email = Column(String)
    tipo_servicio = Column(String)
    precio = Column(Integer)
    fecha = Column(String)
