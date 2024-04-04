# Movie-Database-API

## Overview:
The project aims to create a Movie Database API using Python, which interacts with the OMDB API to fetch movie data. The API will be deployed on Google Cloud Platform (GCP) to ensure scalability and reliability. The project comprises three main components: fetching data from the OMDB API and storing it in a database, implementing various API endpoints for CRUD operations, and conducting unit tests to ensure robustness.

### Running Command:
```
python -m uvicorn Brite:app --reload
```
### Running Command:
```
python -m pytest test.py
```

## Key Features:

### Data Fetching and Storage:

Fetches 100 movies from the OMDB API.
Saves movies in the database.
Executes data fetching only if the database is empty.
API Implementation:

### List Movies Endpoint:
- Returns a list of movies from the database.
- Allows customization of the number of records returned in a single API response (default: 10).
- Implements pagination.
- Orders data by movie title.
#### Get Single Movie Endpoint:
- Returns details of a single movie based on its title.
Add Movie Endpoint:
- Adds a new movie to the database.
- Requires providing the movie title in the request.
- Fetches all movie details from the OMDB API and saves them in the database.
#### Remove Movie Endpoint:
- Removes a movie from the database based on its ID.
- Protected method, accessible only to authorized users.

### Unit Tests:

Implements unit tests for all API endpoints and cases to ensure functionality and reliability.
Tests cover scenarios like fetching movies, adding movies, removing movies, etc.
### Technologies Used:

- Python for backend development.
- Google Cloud Platform (GCP) for deployment and hosting.
- OMDB API for fetching movie data.
- SQL database for storing movie information.
- FastAPI for creating API endpoints.
- Unit testing frameworks like PyTest for testing.
### Project Workflow:


- Load configurations from the config.ini file, including OMDB API key, file paths, and authentication details.
Data Initialization:

- Initialize instances of OMDBAPI and DataHandler classes for interacting with the OMDB API and managing data, respectively.
Check if the movies JSON file exists; if not, fetch movies from the OMDB API and save them to the file.
Initialize the database if it's empty, using data from the movies JSON file.
Authentication Setup:

- Define a function get_current_username to authenticate users based on HTTP Basic Authentication.
Validate the provided username and password against the configured credentials.
API Endpoint Implementation:

#### Implement various API endpoints using FastAPI:
- /movies: Returns a list of movies from the database, supporting pagination and customizable record limits.
- /movies/{title}: Returns details of a single movie based on its title.
- /movies (POST): Adds a new movie to the database, with an option to autofill details from the OMDB API or provide custom details.
- /movies/{movie_id} (DELETE): Deletes a movie from the database based on its IMDb ID, accessible only to authorized users.
#### Error Handling:

- Handle errors such as movie not found, existing movie in the database, unauthorized access, etc., using HTTPException.
Database Operations:

- Perform database operations for fetching, adding, and deleting movies.
- Execute SQL queries to interact with the SQLite database.
#### Deployment and Security:

- Secure the API using HTTP Basic Authentication to ensure authorized access.
- Deploy the FastAPI application on the chosen platform, possibly Google Cloud Platform (GCP), for public access and scalability.
#### Testing:

- Conduct thorough testing of API endpoints to ensure functionality and reliability.
- Test cases should cover scenarios like fetching movies, adding movies, deleting movies, unauthorized access attempts, etc.
