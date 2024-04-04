from omdb_api import OMDBAPI
from DB_Handler import DataHandler


import configparser
from fastapi import FastAPI, HTTPException, Depends
from typing import List
from pydantic import BaseModel
import requests
import sqlite3
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.models import HTTPBase
from fastapi import status
import secrets
import string
import random


# Load configurations
config = configparser.ConfigParser()
config.read('File/config.ini')

# Extract configuration values
omdb_config = config['OMDB']
file_config = config['File']
auth_config = config['Auth']

# Extract values from configurations
api_key = omdb_config.get('api_key')
movies_json = file_config.get('movies_json')
movies_db = file_config.get('movies_db')
username = auth_config.get('username')
password = auth_config.get('password')

# Initialize FastAPI app and security
app = FastAPI()
security = HTTPBasic()

# Initialize OMDB API and DataHandler
omdb = OMDBAPI(api_key)
db_handler = DataHandler()

# Check if movies JSON file exists, fetch and save if it doesn't
if not db_handler.json_file_exists(movies_json):
    movies = omdb.fetch_movies_v2()  # Fetch list of 100 movies
    db_handler.save_to_file_json(movies, movies_json)
else:
    movies = db_handler.load_from_file_json(movies_json)

# Initialize database if it's empty
if db_handler.is_database_empty(movies_db):
    db_handler.initialize_database(movies, movies_db)

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, username)
    correct_password = secrets.compare_digest(credentials.password, password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/movies", response_model=List[dict])
def get_movies(skip: int = 0, limit: int = 10, db: sqlite3.Connection = Depends(db_handler.get_db)):
    movies = db.execute("SELECT Title, Year, imdbID, Type, Poster FROM movies ORDER BY title LIMIT ? OFFSET ?", (limit, skip)).fetchall()
    return [{"Title": title, "Year": year, "imdbID": imdbID, "Type": type_, "Poster": poster} for title, year, imdbID, type_, poster in movies]

@app.get("/movies/{title}", response_model=dict)
def get_movie(title: str, db: sqlite3.Connection = Depends(db_handler.get_db)):
    movie = db.execute("SELECT Title, Year, imdbID, Type, Poster FROM movies WHERE title = ?", (title,)).fetchone()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    title, year, imdbID, type_, poster = movie
    return {"Title": title, "Year": year, "imdbID": imdbID, "Type": type_, "Poster": poster}


@app.post("/movies", response_model=dict)
def create_movie(Title: str, auto_fill: bool = True, Year: str = None, imdbID: str = 0
                 ,Type: str = 'movie',Poster: str = None , db: sqlite3.Connection = Depends(db_handler.get_db)):
    
    existing_movie = db.execute("SELECT * FROM movies WHERE Title = ?", (Title,)).fetchone()
    if existing_movie:
        raise HTTPException(status_code=400, detail="Movie already exists in the database")
    if auto_fill:
        response = requests.get(f"http://www.omdbapi.com/?t={Title}&apikey={api_key}")
        data = response.json()
        if "Error" in data:
            raise HTTPException(status_code=404, detail="Movie not found in OMDB")
        
        movie_data = {
        "Title": data.get("Title"),
        "Year": data.get("Year"),
        "imdbID": data.get("imdbID"),
        "Type": data.get("Type"),
        "Poster": data.get("Poster")
        }
    else:       
        if imdbID == None:
            imdbID = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=10))
        movie_data = {
        "Title": Title,
        "Year": Year,
        "imdbID": imdbID,
        "Type": Type,
        "Poster": Poster
        }

    
    existing_movie = db.execute("SELECT * FROM movies WHERE imdbID = ?", (movie_data["imdbID"],)).fetchone()
    if existing_movie:
        raise HTTPException(status_code=400, detail="Movie already exists in the database")

    cursor = db.cursor()
    cursor.execute("INSERT INTO movies (Title, Year, imdbID, Type, Poster) VALUES (?, ?, ?, ?, ?)",
                   (movie_data["Title"], movie_data["Year"], movie_data["imdbID"], movie_data["Type"], movie_data["Poster"]))
    db.commit()
    return {
        "Title": movie_data["Title"],
        "Year": movie_data["Year"],
        "imdbID": movie_data["imdbID"],
        "Type": movie_data["Type"],
        "Poster": movie_data["Poster"]
    }


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: str, db: sqlite3.Connection = Depends(db_handler.get_db), username: str = Depends(get_current_username)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM movies WHERE imdbID = ?", (movie_id,))
    rows_deleted = cursor.rowcount
    db.commit()

    if rows_deleted == 0:
        raise HTTPException(status_code=404, detail="Movie not found in the database")

    return {"detail": "Movie deleted"}
