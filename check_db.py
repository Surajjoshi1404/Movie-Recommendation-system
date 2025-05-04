from app import app, db, Movie, User, Rating

with app.app_context():
    # Check movies
    movie_count = Movie.query.count()
    print(f"Movies in database: {movie_count}")
    
    # Check users
    user_count = User.query.count()
    print(f"Users in database: {user_count}")
    
    # Check ratings
    rating_count = Rating.query.count()
    print(f"Ratings in database: {rating_count}")