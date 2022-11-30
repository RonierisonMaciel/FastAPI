import os
from fastapi import FastAPI
from sqlmodel import Session, select
from .db import create_db_and_tables, engine, populate_all_tables
from swapi.model import Planet, PlanetCreate, PlanetRead
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    if not os.path.exists("database.sqlite"):
        create_db_and_tables()
        with Session(engine) as session:
            populate_all_tables(session)
    else:
        create_db_and_tables()


def get_session():
    return Session(engine)


def create_response(result):
    return {
        "count": len(result),
        "next": None,
        "previous": None,
        "results": result,
    }


@app.get("/api/planets/", tags=["planets"])
async def list_planets():
    with get_session() as session:
        planets = session.exec(select(Planet)).all()

    return create_response(planets)


@app.post("/api/planets/", status_code=201, tags=["planets"])
async def create_planet(planet: PlanetCreate):

    with get_session() as session:
        db_planet = Planet.from_orm(planet)
        session.add(db_planet)
        session.commit()
        session.refresh(db_planet)
        return db_planet


@app.get("/api/planets/search", tags=["planets"])
async def search_planets(name: str = None, gravity: str = None):
    with get_session() as session:
        if name and not gravity:
            planets = session.exec(select(Planet).where(Planet.name == name)).all()
        elif not name and gravity:
            planets = session.exec(select(Planet).where(Planet.gravity == gravity)).all()
        elif name and gravity:
            planets = session.exec(select(Planet).where(Planet.name == name).where(Planet.gravity == gravity)).all()
        else:
            planets = session.exec(select(Planet)).all()
    
        return create_response(planets)



@app.get("/api/planets/{id}", tags=["planets"], response_model=PlanetRead)
async def list_planet_by_id(id: int):
    with get_session() as session:
        planet = session.exec(select(Planet).where(Planet.id == id)).one()

        return planet