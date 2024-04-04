import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import configparser

from Brite import app  # Import your FastAPI app
from DB_Handler import DataHandler  # Import DataHandler for mocking

config = configparser.ConfigParser()
config.read('File/config.ini')

auth_config = config['Auth']
username = auth_config.get('username')
password = auth_config.get('password')

@pytest.fixture
def test_client():
    client = TestClient(app)
    # Override DataHandler with a mock object for testing
    app.dependency_overrides[DataHandler] = MockDataHandler()
    yield client

class MockDataHandler:
    # Implement mock methods for DataHandler's interactions
    def json_file_exists(self, filename):
        return True  # Assume file exists for testing

    def load_from_file_json(self, filename):
        # Return mock data for testing movie list
        return [
            {"Title": "The Shawshank Redemption", "Year": "1994", "imdbID": "tt0111161"},
            {"Title": "The Godfather", "Year": "1972", "imdbID": "tt0068646"},
        ]


def test_get_movies_check_default_pagination(test_client):
    response = test_client.get("/movies")
    assert response.status_code == 200
    assert len(response.json()) == 10  # Assuming mock data returns 2 movies

    response = test_client.get("/movies?skip=1&limit=1")
    assert len(response.json()) == 1

def test_get_movies_order(test_client):
    response = test_client.get("/movies?limit=50").json()
    is_sorted = all(response[i]["Title"] <= response[i+1]["Title"] for i in range(len(response)-1))
    assert is_sorted == True

def test_get_movie_by_title_exist(test_client):
    title = "A Silent Voice: The Movie"  # Replace with a valid title in your dataset
    response = test_client.get(f"/movies/{title}")
    assert response.status_code == 200
    assert response.json()["Title"] == title

def test_get_movie_by_title_not_exist(test_client):
    title = "The God Father"  # Replace with a valid title in your dataset
    response = test_client.get(f"/movies/{title}")
    assert response.status_code == 404

@patch("requests.get")
def test_create_movie(mock_get,test_client):
    mock_response = {
    "Title": "The Dark Knight",
    "Year": "2008",
    "imdbID": "tt0468569",
    "Type": "movie",
    "Poster": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg"
}
    mock_get.return_value.json.return_value = mock_response
    
    response = test_client.post("movies?Title=The Dark Knight&imdbID=tt0468569&Year=2008&auto_fill=True&Type=movie&Poster=https://example.com/poster.jpg")
    assert response.status_code == 200
    assert response.json() == mock_response
    
@patch("requests.get")
def test_create_movie_duplicate(mock_get,test_client):
    mock_response = {
'detail': 'Movie already exists in the database'
}
    mock_get.return_value.json.return_value = mock_response
    
    response = test_client.post("movies?Title=The Dark Knight&imdbID=tt0468569&Year=2008&auto_fill=True&Type=movie&Poster=https://example.com/poster.jpg")
    assert response.status_code == 400
    assert response.json() == {
   'detail': 'Movie already exists in the database'
}
    
    
@patch("requests.get")
def test_create_movie_without_title(mock_get,test_client):
    mock_response = {
'detail': 'Movie already exists in the database'
}
    mock_get.return_value.json.return_value = mock_response
    
    response = test_client.post("movies?imdbID=tt0468569&Year=2008&auto_fill=True&Type=movie&Poster=https://example.com/poster.jpg")
    assert response.status_code == 422
    assert response.json() == {
    "detail": [
        {
            "type": "missing",
            "loc": [    
                "query",
                "Title"
            ],
            "msg": "Field required",
            "input": None,
            "url": "https://errors.pydantic.dev/2.6/v/missing"
        }
    ]
}

def test_delete_existing_movie(test_client):
    # Attempt to delete a movie that doesn't exist
    response = test_client.delete("/movies/tt0468569",auth=(username,password))
    assert response.status_code == 200
    assert response.json()["detail"] == "Movie deleted"


def test_delete_non_existing_movie(test_client):
    # Attempt to delete a movie that doesn't exist
    response = test_client.delete("/movies/tt04685691",auth=(username,password))
    assert response.status_code == 404
    assert response.json()["detail"] == "Movie not found in the database"

def test_delete_without_auth(test_client):
    # Attempt to delete a movie that doesn't exist
    response = test_client.delete("/movies/tt04685691")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_delete_wrong_auth(test_client):
    # Attempt to delete a movie that doesn't exist
    response = test_client.delete("/movies/tt04685691",auth=("admin2","admin2"))
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
