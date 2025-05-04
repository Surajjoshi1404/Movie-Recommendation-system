import pandas as pd
from app import app, db, Movie, User, Rating
import os

def import_links_and_ratings():
    try:
        with app.app_context():
            print("Starting links and ratings import...")
            
            # Load data files
            links_df = pd.read_csv('data/links.csv')
            ratings_df = pd.read_csv('data/ratings.csv')
            print(f"Found {len(links_df)} links and {len(ratings_df)} ratings")
            
            # Update movies with links
            print("Updating movies with links...")
            total_updated = 0
            for _, row in links_df.iterrows():
                movie = Movie.query.get(int(row['movieId']))
                if movie:
                    movie.imdb_id = f"tt{str(row['imdbId']).zfill(7)}" if pd.notna(row['imdbId']) else None
                    movie.tmdb_id = str(row['tmdbId']) if pd.notna(row['tmdbId']) else None
                    total_updated += 1
                    if total_updated % 100 == 0:
                        db.session.commit()
                        print(f"Updated {total_updated} movies with links...")
            
            db.session.commit()
            print(f"Updated {total_updated} movies with links")
            
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
            
            print("Links and ratings import completed successfully!")
                
    except Exception as e:
        print(f"Error during import: {e}")
        db.session.rollback()

if __name__ == '__main__':
    import_links_and_ratings()