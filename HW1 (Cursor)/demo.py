#!/usr/bin/env python3
"""
Demo script to test the movie recommendation system with the provided sample data
"""

from movie_recommender import MovieRecommender

def demo_with_sample_data():
    """Demonstrate the movie recommendation system with sample data."""
    print("MOVIE RECOMMENDATION SYSTEM DEMO")
    print("=" * 50)
    
    # Create recommender instance
    recommender = MovieRecommender()
    
    # Load the sample data
    print("\n1. Loading sample data...")
    movies_loaded = recommender.load_movies("movies.txt")
    ratings_loaded = recommender.load_ratings("ratings.txt")
    
    if not movies_loaded or not ratings_loaded:
        print("Failed to load data files")
        return
    
    print("+ Data loaded successfully!")
    
    # Test all features
    print("\n2. Testing Movie Popularity (Top 5 movies):")
    top_movies = recommender.get_top_movies(5)
    for i, (movie, rating) in enumerate(top_movies, 1):
        print(f"   {i}. {movie} - {rating:.2f}")
    
    print("\n3. Testing Genre-Specific Movies (Top 3 Action movies):")
    top_action = recommender.get_top_movies_in_genre("Action", 3)
    for i, (movie, rating) in enumerate(top_action, 1):
        print(f"   {i}. {movie} - {rating:.2f}")
    
    print("\n4. Testing Genre Popularity (Top 3 genres):")
    top_genres = recommender.get_top_genres(3)
    for i, (genre, rating) in enumerate(top_genres, 1):
        print(f"   {i}. {genre} - {rating:.2f}")
    
    print("\n5. Testing User Preferences:")
    test_users = ["1", "6", "43"]
    for user_id in test_users:
        preferred_genre = recommender.get_user_preferred_genre(user_id)
        print(f"   User {user_id} prefers: {preferred_genre}")
    
    print("\n6. Testing Movie Recommendations:")
    for user_id in test_users:
        recommendations = recommender.recommend_movies(user_id, 3)
        print(f"   User {user_id} recommendations: {recommendations}")
    
    print("\n7. Data Summary:")
    print(f"   Movies loaded: {len(recommender.movies)}")
    print(f"   Movies with ratings: {len(recommender.ratings)}")
    print(f"   Users with ratings: {len(recommender.user_ratings)}")

if __name__ == "__main__":
    demo_with_sample_data()
