from flask import Flask
from models import db, Movie, User, Rating
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_recommender.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# MongoDB connection
MONGO_URI = f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_CLUSTER')}/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
mongodb = client[os.getenv('MONGO_DB_NAME')]

def convert_to_json_serializable(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

def import_data():
    with app.app_context():
        try:
            # Import Movies
            print("Importing movies...")
            movies_collection = mongodb['movies']
            movies = Movie.query.all()
            for movie in movies:
                movie_dict = {
                    '_id': movie.id,
                    'title': movie.title,
                    'genres': movie.genres.split('|') if movie.genres else [],
                    'release_date': movie.release_date,
                    'imdb_id': movie.imdb_id,
                    'tmdb_id': movie.tmdb_id
                }
                movies_collection.update_one(
                    {'_id': movie.id},
                    {'$set': movie_dict},
                    upsert=True
                )
            print(f"Imported {len(movies)} movies")

            # Import Users
            print("Importing users...")
            users_collection = mongodb['users']
            users = User.query.all()
            for user in users:
                user_dict = {
                    '_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'password': user.password  # This is already hashed
                }
                users_collection.update_one(
                    {'_id': user.id},
                    {'$set': user_dict},
                    upsert=True
                )
            print(f"Imported {len(users)} users")

            # Import Ratings
            print("Importing ratings...")
            ratings_collection = mongodb['ratings']
            ratings = Rating.query.all()
            for rating in ratings:
                rating_dict = {
                    'user_id': rating.user_id,
                    'movie_id': rating.movie_id,
                    'rating': rating.rating
                }
                ratings_collection.update_one(
                    {
                        'user_id': rating.user_id,
                        'movie_id': rating.movie_id
                    },
                    {'$set': rating_dict},
                    upsert=True
                )
            print(f"Imported {len(ratings)} ratings")

            print("Data import completed successfully!")

        except Exception as e:
            print(f"Error during import: {e}")
            client.close()
            return False

        client.close()
        return True

if __name__ == '__main__':
    success = import_data()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!") 