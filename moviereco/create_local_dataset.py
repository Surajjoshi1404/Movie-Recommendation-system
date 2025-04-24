import pandas as pd
import random
import os

def create_movies_dataset():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Sample movies data
    movies = [
        {
            'movieId': 1,
            'title': 'RRR',
            'original_title': 'RRR',
            'genres': 'Action|Drama|History',
            'rating': 8.5,
            'poster_path': 'https://m.media-amazon.com/images/M/MV5BODUwNDNjYzctODUxNy00ZTA2LWIyYTEtMDc4Y2QzNTA0OTk4XkEyXkFqcGdeQXVyODE5NzE3OTE@._V1_.jpg',
            'overview': 'A fictitious story about two legendary revolutionaries and their journey away from home before they started fighting for their country in the 1920s.',
            'release_date': '2022-03-25',
            'language': 'hi',
            'country': 'IN',
            'is_latest': True
        },
        {
            'movieId': 2,
            'title': 'KGF: Chapter 2',
            'original_title': 'KGF: Chapter 2',
            'genres': 'Action|Drama|Thriller',
            'rating': 8.2,
            'poster_path': 'https://m.media-amazon.com/images/M/MV5BMjMwMDgyOGQtMWZjNC00MDUwLTllZDYtZWM3NDBmN2YzNGZmXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_.jpg',
            'overview': 'Rocky takes control of the Kolar Gold Fields and his newfound power makes the government as well as his enemies jittery. However, he still has to confront Ramika Sen.',
            'release_date': '2022-04-14',
            'language': 'hi',
            'country': 'IN',
            'is_latest': True
        },
        {
            'movieId': 3,
            'title': 'Avengers: Endgame',
            'original_title': 'Avengers: Endgame',
            'genres': 'Action|Adventure|Sci-Fi',
            'rating': 8.4,
            'poster_path': 'https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_.jpg',
            'overview': 'After the devastating events of Avengers: Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more in order to reverse Thanos actions and restore balance to the universe.',
            'release_date': '2019-04-26',
            'language': 'en',
            'country': 'US',
            'is_latest': False
        },
        {
            'movieId': 4,
            'title': 'Demon Slayer: Mugen Train',
            'original_title': '劇場版「鬼滅の刃」無限列車編',
            'genres': 'Animation|Action|Adventure',
            'rating': 8.3,
            'poster_path': 'https://m.media-amazon.com/images/M/MV5BODI2NjdlYWItMTE1ZC00YzI2LTlhZGQtNzE3NzA4MWM0ODYzXkEyXkFqcGdeQXVyNjU1OTg4OTM@._V1_.jpg',
            'overview': 'Tanjiro and his comrades embark on a new mission aboard the Mugen Train, on track to despair.',
            'release_date': '2020-10-16',
            'language': 'ja',
            'country': 'JP',
            'is_latest': False
        },
        {
            'movieId': 5,
            'title': 'Parasite',
            'original_title': '기생충',
            'genres': 'Comedy|Drama|Thriller',
            'rating': 8.6,
            'poster_path': 'https://m.media-amazon.com/images/M/MV5BYWZjMjk3ZTItODQ2ZC00NTY5LWE0ZDYtZTI3MjcwN2Q5NTVkXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1_.jpg',
            'overview': 'Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.',
            'release_date': '2019-05-30',
            'language': 'ko',
            'country': 'KR',
            'is_latest': False
        }
    ]
    
    # Generate more sample movies
    for i in range(6, 1001):
        languages = ['hi', 'en', 'ja', 'ko']
        countries = ['IN', 'US', 'JP', 'KR']
        genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 'Sci-Fi', 'Thriller']
        
        movie = {
            'movieId': i,
            'title': f'Movie {i}',
            'original_title': f'Movie {i}',
            'genres': '|'.join(random.sample(genres, random.randint(1, 3))),
            'rating': round(random.uniform(5, 9), 1),
            'poster_path': f'https://example.com/poster_{i}.jpg',
            'overview': f'This is a sample overview for Movie {i}',
            'release_date': f'202{random.randint(0,3)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
            'language': random.choice(languages),
            'country': random.choice(countries),
            'is_latest': random.choice([True, False])
        }
        movies.append(movie)
    
    # Create movies DataFrame
    movies_df = pd.DataFrame(movies)
    
    # Generate ratings
    ratings = []
    for user_id in range(1, 1001):
        n_ratings = random.randint(10, 50)
        rated_movies = random.sample(list(movies_df['movieId']), n_ratings)
        
        for movie_id in rated_movies:
            movie = movies_df[movies_df['movieId'] == movie_id].iloc[0]
            base_rating = movie['rating']
            noise = random.gauss(0, 1)
            rating = max(1, min(5, round(base_rating/2 + noise)))
            
            ratings.append({
                'userId': user_id,
                'movieId': movie_id,
                'rating': rating,
                'timestamp': random.randint(1000000000, 2000000000)
            })
    
    # Create ratings DataFrame
    ratings_df = pd.DataFrame(ratings)
    
    # Save datasets
    movies_df.to_csv('data/movies.csv', index=False)
    ratings_df.to_csv('data/ratings.csv', index=False)
    
    print("Dataset creation complete!")
    print(f"Total movies: {len(movies_df)}")
    print(f"Total ratings: {len(ratings_df)}")
    print(f"Total users: {ratings_df['userId'].nunique()}")
    print("\nMovie distribution by language:")
    print(movies_df['language'].value_counts())
    print("\nMovie distribution by country:")
    print(movies_df['country'].value_counts())

if __name__ == "__main__":
    create_movies_dataset() 