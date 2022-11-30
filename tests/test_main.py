from swapi.main import app
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session
from sqlmodel.pool import StaticPool
from swapi.db import populate_all_tables
from unittest.mock import patch
import pytest


client = TestClient(app)


@pytest.fixture
def single_planet():
    return {
            "name": "new_planet",
            "rotation_period": "253",
            "orbital_period": "34",
            "diameter": "105",
            "climate": "tropical",
            "gravity": "1",
            "terrain": "planice",
            "surface_water": "1",
            "population": "2012300",
        }



def get_session_override():

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    populate_all_tables(session)

    return session


def test_get_all_planets():

    with patch("swapi.main.get_session", get_session_override):

        response = client.get('/api/planets')
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 60


def test_planet_post_route(single_planet):

    with patch("swapi.main.get_session", get_session_override):

        response = client.post('/api/planets/', json=single_planet)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 61


def test_search_planet_with_no_parameters():
    with patch("swapi.main.get_session", get_session_override):

        response = client.get('/api/planets/search')
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 60

def test_search_planet_with_name_parameter():
    with patch("swapi.main.get_session", get_session_override):

        response = client.get('/api/planets/search?name=Hoth')
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
    


def test_search_planet_with_gravity_parameter():
    with patch("swapi.main.get_session", get_session_override):

        response = client.get('/api/planets/search?gravity=unknown')
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 15


def test_search_planet_with_both_parameters():
    with patch("swapi.main.get_session", get_session_override):

        response = client.get('/api/planets/search?gravity=unknown&name=Hoth')
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0

def test_get_planet_by_id():
    with patch("swapi.main.get_session", get_session_override):

        response = client.get('/api/planets/1')
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Tatooine"