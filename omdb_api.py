import requests
import random

class OMDBAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_movies_v1(self, num_movies):
        movies = []
        for _ in range(num_movies):
            # Generate a random IMDb ID (tt + 7 digits)
            while(True):
                imdb_id = 'tt' + str(random.randint(1000000, 9999999))
                url = f'http://www.omdbapi.com/?i={imdb_id}&apikey={self.api_key}'  
                response = requests.get(url)
                if response.status_code == 200:
                    movie_data = response.json()
                    if (movie_data.get('Response') == 'True') : #  & (movie_data.get('type') == 'movie')
                        movies.append(movie_data)
                        break
        return movies

    def fetch_movies_v2(self):
        return_list = []
        counter = 0
        while(True):
            url = f"http://www.omdbapi.com/?apikey={self.api_key}&s=movie&type=movie&page={counter}&limit=100"
            response = requests.get(url)
            if response.status_code == 200:
                movies_data = response.json().get('Search', [])
                return_list += movies_data
                counter+=1
                if(len(return_list) >= 100):
                    return return_list

