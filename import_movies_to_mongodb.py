import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_CLUSTER')}/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client[os.getenv('MONGO_DB_NAME')]

def import_movies():
    try:
        # Import movies from CSV
        print("Importing movies from CSV...")
        movies_df = pd.read_csv('data/movies.csv')
        movies_collection = db['movies']

        # Convert DataFrame to list of dictionaries
        movies_data = movies_df.to_dict('records')
        for movie in movies_data:
            # Convert genres string to list
            if 'genres' in movie and isinstance(movie['genres'], str):
                movie['genres'] = movie['genres'].split('|')
            
            # Add timestamp
            movie['created_at'] = datetime.now()
            
            # Use movie_id as _id
            if 'movieId' in movie:
                movie['_id'] = movie['movieId']
                del movie['movieId']

        # Insert movies in bulk
        if movies_data:
            movies_collection.insert_many(movies_data, ordered=False)
        print(f"Imported {len(movies_data)} movies")

        # Import ratings from CSV
        print("Importing ratings from CSV...")
        ratings_df = pd.read_csv('data/ratings.csv')
        ratings_collection = db['ratings']

        # Convert DataFrame to list of dictionaries
        ratings_data = ratings_df.to_dict('records')
        for rating in ratings_data:
            rating['created_at'] = datetime.now()
            if 'movieId' in rating:
                rating['movie_id'] = rating['movieId']
                del rating['movieId']
            if 'userId' in rating:
                rating['user_id'] = rating['userId']
                del rating['userId']

        # Insert ratings in bulk
        if ratings_data:
            ratings_collection.insert_many(ratings_data, ordered=False)
        print(f"Imported {len(ratings_data)} ratings")

        print("Data import completed successfully!")
        return True

    except Exception as e:
        print(f"Error during import: {e}")
        return False

    finally:
        client.close()

if __name__ == '__main__':
    success = import_movies()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!") 