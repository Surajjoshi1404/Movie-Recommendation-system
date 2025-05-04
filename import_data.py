import pandas as pd
from app import app, db, Movie, User, Rating
from werkzeug.security import generate_password_hash
import os

def import_movies():
    try:
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            
            if Movie.query.first() is None:
                print("Starting data import...")
                
                # Load all data files
                movies_df = pd.read_csv('data/movies.csv')
                links_df = pd.read_csv('data/links.csv')
                ratings_df = pd.read_csv('data/ratings.csv')
                
                # Merge movies and links
                movies_with_links = pd.merge(movies_df, links_df, on='movieId', how='left')
                print(f"Found {len(movies_with_links)} movies and {len(ratings_df)} ratings")
                
                # Import movies with links
                batch_size = 100
                total_imported = 0
                
                for i in range(0, len(movies_with_links), batch_size):
                    batch = movies_with_links.iloc[i:i+batch_size]
                    for _, row in batch.iterrows():
                        try:
                            movie = Movie(
                                id=int(row['movieId']),
                                title=str(row['title']),
                                genres=str(row['genres']),
                                imdb_id=f"tt{str(row['imdbId']).zfill(7)}" if pd.notna(row['imdbId']) else None,
                                tmdb_id=str(row['tmdbId']) if pd.notna(row['tmdbId']) else None
                            )
                            db.session.add(movie)
                            total_imported += 1
                        except Exception as e:
                            print(f"Error importing movie {row['movieId']}: {e}")
                    db.session.commit()
                    print(f"Imported {total_imported} movies so far...")
                
                # Import ratings
                print("Starting ratings import...")
                batch_size = 1000
                total_ratings = 0
                
                for i in range(0, len(ratings_df), batch_size):
                    batch = ratings_df.iloc[i:i+batch_size]
                    for _, row in batch.iterrows():
                        try:
                            rating = Rating(
                                user_id=1,  # Assign to admin user
                                movie_id=int(row['movieId']),
                                rating=float(row['rating'])
                            )
                            db.session.add(rating)
                            total_ratings += 1
                        except Exception as e:
                            print(f"Error importing rating: {e}")
                    db.session.commit()
                    print(f"Imported {total_ratings} ratings so far...")
                
                # Create admin user
                if User.query.filter_by(username='admin').first() is None:
                    admin = User(
                        username='admin',
                        email='admin@example.com',
                        password=generate_password_hash('admin123'),
                        is_active=True
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("Admin user created")
                
                print("All data imported successfully!")
            else:
                print("Database already contains data!")
                
    except Exception as e:
        print(f"Error during import: {e}")
        db.session.rollback()

if __name__ == '__main__':
    db_path = 'movie_database.db'
    if not os.path.exists(db_path):
        open(db_path, 'a').close()
        print(f"Created database file at {os.path.abspath(db_path)}")
    
    import_movies()