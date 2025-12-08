#!/usr/bin/env python3
"""
Movie Recommendation System

A Python program that provides movie recommendations based on:
- Movie popularity (top n movies by average ratings)
- Movie popularity in genre (top n movies in a genre)
- Genre popularity (top n genres by average ratings)
- User preference for genre (most preferred genre by user)
- Movie recommendations (3 most popular movies from user's top genre)

Author: Generated with AI assistance
Python Version: 3.12+
"""

import os
import sys
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class MovieRecommender:
    """
    A class to handle movie recommendations based on ratings and genres.
    """
    
    def __init__(self):
        """Initialize the MovieRecommender with empty data structures."""
        self.movies = {}  # movie_id -> (genre, movie_name)
        self.ratings = defaultdict(list)  # movie_name -> [(rating, user_id), ...]
        self.user_ratings = defaultdict(list)  # user_id -> [(movie_name, rating), ...]
        self.data_loaded = False
    
    def load_movies(self, filename: str) -> bool:
        """
        Load movie data from a file.
        
        Args:
            filename (str): Path to the movies file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(filename):
                print(f"Error: File '{filename}' not found.")
                return False
                
            with open(filename, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split('|')
                    if len(parts) != 3:
                        print(f"Warning: Skipping malformed line {line_num}: {line}")
                        continue
                    
                    genre, movie_id, movie_name = parts
                    self.movies[movie_id] = (genre.strip(), movie_name.strip())
            
            print(f"Successfully loaded {len(self.movies)} movies from '{filename}'")
            return True
            
        except Exception as e:
            print(f"Error loading movies from '{filename}': {e}")
            return False
    
    def load_ratings(self, filename: str) -> bool:
        """
        Load ratings data from a file.
        
        Args:
            filename (str): Path to the ratings file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(filename):
                print(f"Error: File '{filename}' not found.")
                return False
                
            with open(filename, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split('|')
                    if len(parts) != 3:
                        print(f"Warning: Skipping malformed line {line_num}: {line}")
                        continue
                    
                    movie_name, rating_str, user_id = parts
                    movie_name = movie_name.strip()
                    user_id = user_id.strip()
                    
                    try:
                        rating = float(rating_str.strip())
                        if not (0 <= rating <= 5):
                            print(f"Warning: Invalid rating {rating} on line {line_num}, skipping")
                            continue
                    except ValueError:
                        print(f"Warning: Non-numeric rating '{rating_str}' on line {line_num}, skipping")
                        continue
                    
                    # Check for duplicate ratings
                    if (rating, user_id) not in self.ratings[movie_name]:
                        self.ratings[movie_name].append((rating, user_id))
                        self.user_ratings[user_id].append((movie_name, rating))
                    else:
                        print(f"Warning: Duplicate rating for movie '{movie_name}' by user '{user_id}' on line {line_num}")
            
            print(f"Successfully loaded ratings for {len(self.ratings)} movies from '{filename}'")
            self.data_loaded = True
            return True
            
        except Exception as e:
            print(f"Error loading ratings from '{filename}': {e}")
            return False
    
    def get_top_movies(self, n: int) -> List[Tuple[str, float]]:
        """
        Get top n movies ranked by average ratings.
        
        Args:
            n (int): Number of top movies to return
            
        Returns:
            List[Tuple[str, float]]: List of (movie_name, average_rating) tuples
        """
        if not self.data_loaded:
            print("Error: No data loaded. Please load movies and ratings first.")
            return []
        
        movie_averages = []
        for movie_name, rating_list in self.ratings.items():
            if rating_list:
                avg_rating = sum(rating for rating, _ in rating_list) / len(rating_list)
                movie_averages.append((movie_name, avg_rating))
        
        # Sort by average rating (descending), then by movie name (ascending) for ties
        movie_averages.sort(key=lambda x: (-x[1], x[0]))
        
        return movie_averages[:n]
    
    def get_top_movies_in_genre(self, genre: str, n: int) -> List[Tuple[str, float]]:
        """
        Get top n movies in a specific genre ranked by average ratings.
        
        Args:
            genre (str): The genre to filter by
            n (int): Number of top movies to return
            
        Returns:
            List[Tuple[str, float]]: List of (movie_name, average_rating) tuples
        """
        if not self.data_loaded:
            print("Error: No data loaded. Please load movies and ratings first.")
            return []
        
        # Find movies in the specified genre
        genre_movies = set()
        for movie_id, (movie_genre, movie_name) in self.movies.items():
            if movie_genre.lower() == genre.lower():
                genre_movies.add(movie_name)
        
        if not genre_movies:
            print(f"No movies found in genre '{genre}'")
            return []
        
        movie_averages = []
        for movie_name in genre_movies:
            if movie_name in self.ratings and self.ratings[movie_name]:
                avg_rating = sum(rating for rating, _ in self.ratings[movie_name]) / len(self.ratings[movie_name])
                movie_averages.append((movie_name, avg_rating))
        
        # Sort by average rating (descending), then by movie name (ascending) for ties
        movie_averages.sort(key=lambda x: (-x[1], x[0]))
        
        return movie_averages[:n]
    
    def get_top_genres(self, n: int) -> List[Tuple[str, float]]:
        """
        Get top n genres ranked by average of average ratings of movies in genre.
        
        Args:
            n (int): Number of top genres to return
            
        Returns:
            List[Tuple[str, float]]: List of (genre, average_rating) tuples
        """
        if not self.data_loaded:
            print("Error: No data loaded. Please load movies and ratings first.")
            return []
        
        genre_stats = defaultdict(list)
        
        # Calculate average rating for each movie
        movie_averages = {}
        for movie_name, rating_list in self.ratings.items():
            if rating_list:
                avg_rating = sum(rating for rating, _ in rating_list) / len(rating_list)
                movie_averages[movie_name] = avg_rating
        
        # Group movies by genre and collect their average ratings
        for movie_id, (genre, movie_name) in self.movies.items():
            if movie_name in movie_averages:
                genre_stats[genre].append(movie_averages[movie_name])
        
        # Calculate average of averages for each genre
        genre_averages = []
        for genre, ratings_list in genre_stats.items():
            if ratings_list:
                avg_genre_rating = sum(ratings_list) / len(ratings_list)
                genre_averages.append((genre, avg_genre_rating))
        
        # Sort by average rating (descending), then by genre name (ascending) for ties
        genre_averages.sort(key=lambda x: (-x[1], x[0]))
        
        return genre_averages[:n]
    
    def get_user_preferred_genre(self, user_id: str) -> Optional[str]:
        """
        Get the genre most preferred by a user based on average ratings.
        
        Args:
            user_id (str): The user ID to analyze
            
        Returns:
            Optional[str]: The most preferred genre, or None if user not found
        """
        if not self.data_loaded:
            print("Error: No data loaded. Please load movies and ratings first.")
            return None
        
        if user_id not in self.user_ratings:
            print(f"User '{user_id}' not found in ratings data.")
            return None
        
        # Group user's ratings by genre
        genre_ratings = defaultdict(list)
        
        for movie_name, rating in self.user_ratings[user_id]:
            # Find the genre for this movie
            for movie_id, (genre, name) in self.movies.items():
                if name == movie_name:
                    genre_ratings[genre].append(rating)
                    break
        
        if not genre_ratings:
            print(f"No genre information found for user '{user_id}'")
            return None
        
        # Calculate average rating for each genre
        genre_averages = []
        for genre, ratings_list in genre_ratings.items():
            avg_rating = sum(ratings_list) / len(ratings_list)
            genre_averages.append((genre, avg_rating))
        
        # Sort by average rating (descending), then by genre name (ascending) for ties
        genre_averages.sort(key=lambda x: (-x[1], x[0]))
        
        return genre_averages[0][0] if genre_averages else None
    
    def recommend_movies(self, user_id: str, n: int = 3) -> List[str]:
        """
        Recommend n most popular movies from user's top genre that the user has not rated.
        
        Args:
            user_id (str): The user ID to recommend movies for
            n (int): Number of movies to recommend (default: 3)
            
        Returns:
            List[str]: List of recommended movie names
        """
        if not self.data_loaded:
            print("Error: No data loaded. Please load movies and ratings first.")
            return []
        
        # Get user's preferred genre
        preferred_genre = self.get_user_preferred_genre(user_id)
        if not preferred_genre:
            print(f"Cannot recommend movies for user '{user_id}' - no preferred genre found.")
            return []
        
        # Get movies user has already rated
        user_rated_movies = set()
        if user_id in self.user_ratings:
            user_rated_movies = {movie_name for movie_name, _ in self.user_ratings[user_id]}
        
        # Get top movies in preferred genre
        top_genre_movies = self.get_top_movies_in_genre(preferred_genre, len(self.movies))
        
        # Filter out movies user has already rated
        recommendations = []
        for movie_name, _ in top_genre_movies:
            if movie_name not in user_rated_movies:
                recommendations.append(movie_name)
                if len(recommendations) >= n:
                    break
        
        return recommendations


def display_menu():
    """Display the main menu options."""
    print("\n" + "="*50)
    print("MOVIE RECOMMENDATION SYSTEM")
    print("="*50)
    print("1. Load movies file")
    print("2. Load ratings file")
    print("3. Get top N movies")
    print("4. Get top N movies in genre")
    print("5. Get top N genres")
    print("6. Get user's preferred genre")
    print("7. Recommend movies for user")
    print("8. Display loaded data summary")
    print("9. Exit")
    print("="*50)


def main():
    """Main function to run the movie recommendation system."""
    recommender = MovieRecommender()
    
    print("Welcome to the Movie Recommendation System!")
    print("This program helps you discover movies based on ratings and genres.")
    
    while True:
        display_menu()
        
        try:
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == '1':
                filename = input("Enter movies filename: ").strip()
                recommender.load_movies(filename)
                
            elif choice == '2':
                filename = input("Enter ratings filename: ").strip()
                recommender.load_ratings(filename)
                
            elif choice == '3':
                if not recommender.data_loaded:
                    print("Error: Please load movies and ratings data first.")
                    continue
                try:
                    n = int(input("Enter number of top movies to display: "))
                    if n <= 0:
                        print("Error: Number must be positive.")
                        continue
                    results = recommender.get_top_movies(n)
                    print(f"\nTop {n} movies by average rating:")
                    print("-" * 40)
                    for i, (movie, rating) in enumerate(results, 1):
                        print(f"{i}. {movie} - {rating:.2f}")
                except ValueError:
                    print("Error: Please enter a valid number.")
                    
            elif choice == '4':
                if not recommender.data_loaded:
                    print("Error: Please load movies and ratings data first.")
                    continue
                genre = input("Enter genre name: ").strip()
                try:
                    n = int(input("Enter number of top movies to display: "))
                    if n <= 0:
                        print("Error: Number must be positive.")
                        continue
                    results = recommender.get_top_movies_in_genre(genre, n)
                    if results:
                        print(f"\nTop {n} movies in genre '{genre}':")
                        print("-" * 40)
                        for i, (movie, rating) in enumerate(results, 1):
                            print(f"{i}. {movie} - {rating:.2f}")
                except ValueError:
                    print("Error: Please enter a valid number.")
                    
            elif choice == '5':
                if not recommender.data_loaded:
                    print("Error: Please load movies and ratings data first.")
                    continue
                try:
                    n = int(input("Enter number of top genres to display: "))
                    if n <= 0:
                        print("Error: Number must be positive.")
                        continue
                    results = recommender.get_top_genres(n)
                    print(f"\nTop {n} genres by average rating:")
                    print("-" * 40)
                    for i, (genre, rating) in enumerate(results, 1):
                        print(f"{i}. {genre} - {rating:.2f}")
                except ValueError:
                    print("Error: Please enter a valid number.")
                    
            elif choice == '6':
                if not recommender.data_loaded:
                    print("Error: Please load movies and ratings data first.")
                    continue
                user_id = input("Enter user ID: ").strip()
                preferred_genre = recommender.get_user_preferred_genre(user_id)
                if preferred_genre:
                    print(f"\nUser '{user_id}' prefers genre: {preferred_genre}")
                else:
                    print(f"\nCould not determine preferred genre for user '{user_id}'")
                    
            elif choice == '7':
                if not recommender.data_loaded:
                    print("Error: Please load movies and ratings data first.")
                    continue
                user_id = input("Enter user ID: ").strip()
                try:
                    n = int(input("Enter number of movies to recommend (default 3): ") or "3")
                    if n <= 0:
                        print("Error: Number must be positive.")
                        continue
                    recommendations = recommender.recommend_movies(user_id, n)
                    if recommendations:
                        print(f"\nRecommended movies for user '{user_id}':")
                        print("-" * 40)
                        for i, movie in enumerate(recommendations, 1):
                            print(f"{i}. {movie}")
                    else:
                        print(f"\nNo recommendations available for user '{user_id}'")
                except ValueError:
                    print("Error: Please enter a valid number.")
                    
            elif choice == '8':
                print(f"\nData Summary:")
                print(f"- Movies loaded: {len(recommender.movies)}")
                print(f"- Movies with ratings: {len(recommender.ratings)}")
                print(f"- Users with ratings: {len(recommender.user_ratings)}")
                print(f"- Data loaded: {recommender.data_loaded}")
                
            elif choice == '9':
                print("\nThank you for using the Movie Recommendation System!")
                break
                
            else:
                print("Invalid choice. Please enter a number between 1 and 9.")
                
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
