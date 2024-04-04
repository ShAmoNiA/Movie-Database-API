import json
import sqlite3
import os

import configparser

config = configparser.ConfigParser()
config.read('File/config.ini')
movies_db = config.get('File', 'movies_db')

class DataHandler:
    @staticmethod
    def json_file_exists(file_path):
        return os.path.exists(file_path) and os.path.isfile(file_path) and file_path.endswith('.json')

    def save_to_file_json(self, data_list, filename):
        with open(filename, 'w') as file:
            json.dump(data_list, file)

    def load_from_file_json(self, filename):
        with open(filename, 'r') as file:
            data_list = json.load(file)
        return data_list

    @staticmethod
    def initialize_database(initial_data,movies_db):
        
        conn = sqlite3.connect(movies_db)
        cursor = conn.cursor()

        #
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies
            (imdbID TEXT PRIMARY KEY, Title TEXT, Year TEXT, Type TEXT, Poster TEXT)
        """)

    
        rows_to_insert = [(row['imdbID'], row['Title'], row['Year'], row['Type'], row['Poster']) for row in initial_data]
        cursor.executemany("INSERT INTO movies (imdbID, Title, Year, Type, Poster) VALUES (?, ?, ?, ?, ?)", rows_to_insert)

        conn.commit()
        conn.close()

    # Function to get database connection
    @staticmethod
    def get_db():
        conn = sqlite3.connect(movies_db)
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def is_database_empty(database_path):
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
            row_count = cursor.fetchone()[0]
            if row_count > 0:
                conn.close()
                return False
        
        conn.close()
        return True