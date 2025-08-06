"""
Fallback data generator for Hugging Face Spaces
Creates dummy movie data when real datasets are not available
"""
import pandas as pd
import numpy as np
import random
from typing import Tuple

def generate_sample_movies(num_movies: int = 1000) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Generate sample movie data for testing when real data is not available
    
    Args:
        num_movies: Number of sample movies to generate
        
    Returns:
        Tuple of (DataFrame with movie data, numpy array with embeddings)
    """
    # Sample movie titles and genres
    sample_titles = [
        "The Matrix", "Inception", "The Dark Knight", "Pulp Fiction", "The Godfather",
        "Interstellar", "Fight Club", "The Lord of the Rings", "Star Wars", "Avatar",
        "Titanic", "The Shawshank Redemption", "Forrest Gump", "The Lion King", "Jurassic Park",
        "Avengers: Endgame", "Spider-Man", "Iron Man", "Black Panther", "Wonder Woman",
        "Joker", "Parasite", "La La Land", "Moonlight", "1917", "Once Upon a Time in Hollywood",
        "Mad Max: Fury Road", "Blade Runner 2049", "Dune", "The Social Network",
        "Guardians of the Galaxy", "Thor", "Captain America", "Doctor Strange", "Ant-Man",
        "The Incredibles", "Finding Nemo", "Toy Story", "Monsters, Inc.", "Cars",
        "Frozen", "Moana", "Zootopia", "Big Hero 6", "Wreck-It Ralph",
        "The Fast and the Furious", "Mission: Impossible", "James Bond", "John Wick", "Taken",
        "Die Hard", "Terminator", "Alien", "Predator", "RoboCop"
    ]
    
    sample_genres = [
        "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
        "Drama", "Family", "Fantasy", "Horror", "Music", "Mystery", "Romance",
        "Science Fiction", "Thriller", "War", "Western"
    ]
    
    sample_overviews = [
        "A thrilling adventure that takes you on an epic journey.",
        "A heartwarming story about friendship and courage.",
        "An action-packed blockbuster with stunning visual effects.",
        "A romantic comedy that will make you laugh and cry.",
        "A gripping thriller that keeps you on the edge of your seat.",
        "A dramatic tale of love, loss, and redemption.",
        "An animated adventure perfect for the whole family.",
        "A sci-fi epic that explores the future of humanity.",
        "A crime drama that delves into the dark side of society.",
        "A fantasy adventure in a magical world."
    ]
    
    # Generate sample data
    movies = []
    for i in range(num_movies):
        # Create variations of titles
        base_title = random.choice(sample_titles)
        if random.random() < 0.3:  # 30% chance to add variation
            variations = [
                f"{base_title} Returns",
                f"{base_title} 2",
                f"{base_title}: The Sequel",
                f"{base_title} Reloaded",
                f"Return to {base_title}",
                f"{base_title}: Origins"
            ]
            title = random.choice(variations)
        else:
            title = base_title
        
        # Random genres (1-3 genres per movie)
        num_genres = random.randint(1, 3)
        movie_genres = random.sample(sample_genres, num_genres)
        genres_str = "|".join(movie_genres)
        
        # Create movie entry
        movie = {
            'id': i + 1,
            'title': title,
            'genres': genres_str,
            'overview': random.choice(sample_overviews),
            'release_date': f"{random.randint(1990, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            'poster_path': f"/sample_poster_{i}.jpg",
            'vote_count': random.randint(100, 10000)
        }
        movies.append(movie)
    
    # Create DataFrame
    df = pd.DataFrame(movies)
    
    # Generate random embeddings (384 dimensions to match sentence transformer model)
    embeddings = np.random.rand(num_movies, 384).astype('float32')
    # Normalize embeddings
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    print(f"✅ Generated {num_movies} sample movies for testing")
    return df, embeddings

def create_minimal_test_data() -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Create minimal test data for very resource-constrained environments
    """
    return generate_sample_movies(num_movies=100)
