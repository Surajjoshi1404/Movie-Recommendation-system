from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import bcrypt
import webbrowser
import threading
import time
import string
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import Config

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config.from_object(Config)

# Database configuration
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genres = db.Column(db.String(200))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    imdb_id = db.Column(db.String(20))
    tmdb_id = db.Column(db.String(20))
    ratings = db.relationship('Rating', backref='movie', lazy=True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

def open_browser():
    """Function to open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

def get_movie_recommendations(movie_id, n_recommendations=5):
    try:
        # Get all ratings for the target movie
        target_ratings = Rating.query.filter_by(movie_id=movie_id).all()
        
        # If no ratings, return random movies
        if not target_ratings:
            return Movie.query.order_by(db.func.random()).limit(n_recommendations).all()
        
        # Get users who rated this movie
        user_ids = [r.user_id for r in target_ratings]
        
        # Get other movies these users rated highly
        similar_movies = db.session.query(Movie).\
            join(Rating).\
            filter(Rating.user_id.in_(user_ids)).\
            filter(Rating.movie_id != movie_id).\
            group_by(Movie.id).\
            order_by(db.func.avg(Rating.rating).desc()).\
            limit(n_recommendations).\
            all()
        
        return similar_movies
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return Movie.query.limit(n_recommendations).all()

def search_movies(query=None, genre=None, letter=None):
    """Search and filter movies based on various criteria"""
    try:
        # Start with base query
        movies = Movie.query
        
        # Filter by starting letter if provided
        if letter and letter in string.ascii_uppercase:
            movies = movies.filter(Movie.title.like(f'{letter}%'))
        
        # Apply text search if provided
        if query and not query.isspace():
            search = f"%{query}%"
            movies = movies.filter(Movie.title.like(search))
        
        # Apply genre filter if provided
        if genre and not genre.isspace():
            movies = movies.filter(Movie.genres.like(f"%{genre}%"))
        
        # Get results
        results = movies.all()
        
        if not results:
            print("No results found for the given filters")
            return Movie.query.order_by(Movie.year.desc()).limit(10).all()
            
        return results
    except Exception as e:
        print(f"Error searching movies: {e}")
        return Movie.query.limit(10).all()

@app.route('/')
def index():
    try:
        # Get filter parameters
        query = request.args.get('q', '')
        genre = request.args.get('genre', '')
        letter = request.args.get('letter', '')
        
        # Get filtered movies
        if any([query, genre, letter]):
            movies = search_movies(query, genre, letter)
        else:
            # Get latest movies by default
            movies = Movie.query.order_by(Movie.year.desc()).limit(10).all()
        
        # Get alphabet list for letter-based filtering
        alphabet = list(string.ascii_uppercase)
        
        # Get all unique genres
        all_genres = db.session.query(Movie.genres).distinct().all()
        genres = list(set([g for (g,) in all_genres for g in g.split('|') if g]))
        
        return render_template('index.html', 
                            movies=movies,
                            user=session.get('username'),
                            alphabet=alphabet,
                            genres=sorted(genres),
                            current_query=query,
                            current_genre=genre,
                            current_letter=letter)
    except Exception as e:
        print(f"Error in index route: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('index.html', 
                            movies=[],
                            user=session.get('username'),
                            alphabet=list(string.ascii_uppercase),
                            genres=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                # Update last login time
                user.last_login = datetime.now()
                db.session.commit()
                
                session['user_id'] = user.id
                session['username'] = username
                flash('Login successful! Welcome back!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
        
        except Exception as e:
            print(f"Error in login: {e}")
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            # Validate input
            if not username or not email or not password:
                flash('All fields are required', 'error')
                return render_template('signup.html')
            
            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return render_template('signup.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'error')
                return render_template('signup.html')
            
            # Hash password
            hashed = generate_password_hash(password)
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                password=hashed,
                created_at=datetime.now(),
                last_login=datetime.now(),
                is_active=True
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            session['username'] = username
            flash('Account created successfully! Welcome to Movie Recommender!', 'success')
            return redirect(url_for('index'))
                
        except Exception as e:
            print(f"Error in signup: {e}")
            flash('An error occurred during signup. Please try again.', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                user.last_activity = datetime.now()
                db.session.commit()
        
        session.pop('username', None)
        session.pop('user_id', None)
        flash('You have been logged out successfully', 'info')
    except Exception as e:
        print(f"Error in logout: {e}")
        flash('An error occurred during logout', 'error')
    
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to view your profile', 'error')
        return redirect(url_for('login'))
    
    try:
        # Get user data
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            flash('User not found', 'error')
            return redirect(url_for('login'))
        
        # Get user's ratings
        user_ratings = Rating.query.filter_by(user_id=user.id).order_by(Rating.updated_at.desc()).all()
        
        # Get rated movies details
        rated_movies = []
        for rating in user_ratings:
            movie = Movie.query.get(rating.movie_id)
            if movie:
                rated_movies.append({
                    'movie': movie,
                    'rating': rating.rating,
                    'rated_at': rating.updated_at or rating.created_at
                })
        
        return render_template('profile.html',
                           user=user,
                           rated_movies=rated_movies)
                           
    except Exception as e:
        print(f"Error in profile: {e}")
        flash('Error loading profile', 'error')
        return redirect(url_for('index'))

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    recommendations = get_movie_recommendations(movie_id)
    
    # Get average rating
    avg_rating = db.session.query(db.func.avg(Rating.rating)).\
        filter_by(movie_id=movie_id).scalar() or 0
    
    # Get user's rating if logged in
    user_rating = None
    if 'user_id' in session:
        user_rating = Rating.query.filter_by(
            user_id=session['user_id'],
            movie_id=movie_id
        ).first()
    
    return render_template('movie_detail.html', 
                        movie=movie, 
                        recommendations=recommendations,
                        avg_rating=round(avg_rating, 1),
                        user_rating=user_rating.rating if user_rating else None,
                        user=session.get('username'))

@app.route('/rate/<int:movie_id>', methods=['POST'])
def rate_movie(movie_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login to rate movies'}), 401
    
    try:
        rating_value = float(request.form['rating'])
        if not 0 <= rating_value <= 5:
            return jsonify({'error': 'Rating must be between 0 and 5'}), 400
        
        # Update or create rating
        rating = Rating.query.filter_by(
            user_id=session['user_id'],
            movie_id=movie_id
        ).first()
        
        if rating:
            rating.rating = rating_value
        else:
            rating = Rating(
                user_id=session['user_id'],
                movie_id=movie_id,
                rating=rating_value
            )
            db.session.add(rating)
        
        db.session.commit()
        return jsonify({'success': True, 'rating': rating_value})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Create database tables
with app.app_context():
    db.create_all()

# Load movie data
def load_movie_data():
    movies = Movie.query.all()
    return pd.DataFrame([{
        'movieId': movie.id,
        'title': movie.title,
        'genres': movie.genres,
        'year': movie.year,
        'rating': movie.rating
    } for movie in movies])

# Load ratings data
def load_ratings_data():
    ratings = Rating.query.all()
    return pd.DataFrame([{
        'userId': rating.user_id,
        'movieId': rating.movie_id,
        'rating': rating.rating
    } for rating in ratings])

# Calculate movie similarity matrix
def get_movie_similarity():
    ratings_df = load_ratings_data()
    movies_df = load_movie_data()
    
    # Create user-movie matrix
    user_movie_matrix = ratings_df.pivot(
        index='userId',
        columns='movieId',
        values='rating'
    ).fillna(0)
    
    # Calculate cosine similarity
    movie_similarity = cosine_similarity(user_movie_matrix.T)
    movie_similarity_df = pd.DataFrame(
        movie_similarity,
        index=user_movie_matrix.columns,
        columns=user_movie_matrix.columns
    )
    
    return movie_similarity_df

# Get movie recommendations
def get_movie_recommendations(movie_id, n_recommendations=5):
    movie_similarity_df = get_movie_similarity()
    similar_movies = movie_similarity_df[movie_id].sort_values(ascending=False)[1:n_recommendations+1]
    return similar_movies.index.tolist()

if __name__ == '__main__':
    # Only open browser when explicitly running the app
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        threading.Thread(target=open_browser).start()
    
    app.run(debug=True) 