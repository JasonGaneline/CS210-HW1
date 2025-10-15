"""
movie_recommender.py
--------------------
A command-line movie recommendation system.

This program loads movie and rating data from text files and provides
a CLI menu to explore movie statistics and generate recommendations.

Author: Jason Ganeline
Due Date: 10/17/25
"""
import sys
from statistics import mean


# Data storage
movies = {}       # movie_name -> {"id": id, "genre": genre}
ratings = {}      # movie_name -> list of (user_id, rating)
user_ratings = {} # user_id -> dict of movie_name -> rating

# File loading functions
def load_movies_file(filename):
    movies = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            genre, movie_id, title = line.strip().split('|')
            movies[title] = {"id": int(movie_id), "genre": genre}
    return movies

def load_ratings_file(filename):
    ratings = {}
    user_ratings = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            movie_name, rating, user_id = line.strip().split('|')
            rating = float(rating)
            user_id = int(user_id)

            # Add to movie ratings
            ratings.setdefault(movie_name, []).append(rating)

            # Add to user ratings
            user_ratings.setdefault(user_id, {})[movie_name] = rating

    return ratings, user_ratings

# Helper functions 
def average_rating_for_movie(movie_name):
    """Compute the average rating for a single movie."""
    if movie_name not in ratings or len(ratings[movie_name]) == 0:
        return 0.0
    return mean(r for _, r in ratings[movie_name])

def movie_average_map():
    """Return a dict mapping movie_name -> average_rating."""
    return {m: average_rating_for_movie(m) for m in ratings}


# ------------------------------
# Program features
# ------------------------------

# NEED TO UPDATE ALL 5 FEATURES TO PRINT OUT RESULTS - REFER TO CHATGPT RECENT MESSAGES
# 1. Movie Popularity - Top n movies (ranked on avg ratings)
def top_n_movies(movies, ratings, n):
    """
    Display top N movies by average rating.

    Args:
        movies (dict): Movie info dictionary.
        ratings (dict): Ratings dictionary (movie_name -> list of ratings).
        n (int): Number of top movies to display.
    """
    from statistics import mean

    if not ratings:
        print("No ratings data available.")
        return

    movie_avg = {movie: mean(rlist) for movie, rlist in ratings.items()}
    sorted_movies = sorted(movie_avg.items(), key=lambda x: x[1], reverse=True)

    print(f"\n🏆 Top {n} Movies by Average Rating:")
    for i, (movie, avg) in enumerate(sorted_movies[:n], 1):
        print(f"{i}. {movie} — {avg:.2f}")

# 2. Movie Popularity in Genre - Top n movies in a genre (ranked on avg ratings)
def top_n_movies_in_genre(movies, ratings, genre, n):
    """
    Display top N movies in a specific genre by average rating.
    """
    from statistics import mean

    genre_movies = {name: ratings[name] for name, data in movies.items() if data["genre"] == genre and name in ratings}
    if not genre_movies:
        print(f"No movies found for genre '{genre}'.")
        return

    movie_avg = {name: mean(rlist) for name, rlist in genre_movies.items()}
    sorted_movies = sorted(movie_avg.items(), key=lambda x: x[1], reverse=True)

    print(f"\n🏆 Top {n} Movies in Genre '{genre}':")
    for i, (movie, avg) in enumerate(sorted_movies[:n], 1):
        print(f"{i}. {movie} — {avg:.2f}")

# 3. Genre Popularity - Top n genres (ranked on average of average ratings of movies in genre)
def top_n_genres(movies, ratings, n):
    """
    Display top N genres ranked by the average of average movie ratings.

    Args:
        movies (dict): Movie info dictionary.
        ratings (dict): Ratings dictionary (movie_name -> list of ratings).
        n (int): Number of top genres to display.
    """
    from statistics import mean

    if not ratings:
        print("No ratings data available.")
        return

    genre_avg_list = {}
    genre_movies = {}

    # Collect ratings per genre
    for movie_name, data in movies.items():
        genre = data["genre"]
        if movie_name in ratings:
            genre_movies.setdefault(genre, []).append(mean(ratings[movie_name]))

    # Compute average rating per genre
    for genre, avg_list in genre_movies.items():
        genre_avg_list[genre] = mean(avg_list)

    sorted_genres = sorted(genre_avg_list.items(), key=lambda x: x[1], reverse=True)

    print(f"\n🏆 Top {n} Genres by Average Rating:")
    for i, (genre, avg) in enumerate(sorted_genres[:n], 1):
        print(f"{i}. {genre} — {avg:.2f}")

# 4. User Preference for Genre
#   Genre most preferred by user (average of average ratings by user of movies in genre)
def user_favorite_genre(user_id, movies, user_ratings):
    """
    Determine the user's most preferred genre based on their ratings.

    Args:
        user_id (int): User ID.
        movies (dict): Movie info dictionary.
        user_ratings (dict): User ratings dictionary (user_id -> {movie_name: rating}).

    Returns:
        str: Favorite genre, or None if no ratings.
    """
    from statistics import mean

    if user_id not in user_ratings:
        print(f"User {user_id} not found.")
        return None

    genre_scores = {}
    for movie_name, rating in user_ratings[user_id].items():
        if movie_name not in movies:
            continue
        genre = movies[movie_name]["genre"]
        genre_scores.setdefault(genre, []).append(rating)

    if not genre_scores:
        return None

    genre_avg = {g: mean(rlist) for g, rlist in genre_scores.items()}
    favorite = max(genre_avg, key=genre_avg.get)
    return favorite

# 5. Recommend Movies
#   3 most popular movies from user's top genre that the user has not yet rated
def recommend_movies(movies, ratings, user_ratings, user_id):
    # Step 1: Find the user's favorite genre
    favorite_genre = user_favorite_genre(user_id, movies, user_ratings)
    if not favorite_genre:
        print(f"\nCould not determine a favorite genre for user {user_id}.")
        return

    # Step 2: Find all movies in that genre
    genre_movies = [movie for movie, genres in movies.items() if favorite_genre in genres]

    # Step 3: Remove movies already rated by the user
    rated_movies = user_ratings.get(user_id, {})
    unrated_movies = [movie for movie in genre_movies if movie not in rated_movies]

    # Step 4: Sort remaining movies by average rating (descending)
    rated_avg = []
    for movie in unrated_movies:
        if movie in ratings and len(ratings[movie]) > 0:
            avg_rating = sum(ratings[movie]) / len(ratings[movie])
            rated_avg.append((movie, avg_rating))

    rated_avg.sort(key=lambda x: x[1], reverse=True)

    # Step 5: Display top N recommendations
    if rated_avg:
        print(f"\nTop 3 recommended movies for user {user_id} (genre: {favorite_genre}):")
        for i, (movie, avg) in enumerate(rated_avg[:3], start=1):
            print(f"{i}. {movie} — {avg:.2f}")
    else:
        print(f"No available recommendations for user {user_id}'s favorite genre: {favorite_genre}.")

# Function to make sure both datasets are inputted before proceeding
def check_data_loaded(movies, ratings):
    """
    Check if the movies and ratings data are loaded, and provide
    clear feedback only when something is missing.

    Args:
        movies (dict): Dictionary containing movie information.
        ratings (dict): Dictionary containing user ratings.

    Returns:
        bool: True if both datasets are loaded, False otherwise.
    """
    missing = []

    if not movies:
        missing.append("movies file")
    if not ratings:
        missing.append("ratings file")

    if missing:
        if len(missing) == 2:
            print("⚠️  Both movies and ratings files are not loaded.")
        else:
            print(f"⚠️  The {missing[0]} is not loaded.")
        print("👉 Please load the missing file(s) before using this feature.\n")
        return False

    return True

# CLI Menu
def main_menu():
    """
    Command-line interface for the Movie Recommender System.
    Allows the user to load data files and run analysis features.
    """
    movies = {}
    ratings = {}
    user_ratings = {}

    while True:
        print("\n🎬 Movie Recommender Menu")
        print("1. Load movies file")
        print("2. Load ratings file")
        print("3. Show top N movies (by average rating)")
        print("4. Show top N movies in a genre")
        print("5. Show top N genres")
        print("6. Show user’s favorite genre")
        print("7. Recommend movies for a user")
        print("8. Exit")

        choice = input("Enter your choice: ").strip()

        # --- Load movies file ---
        if choice == "1":
            path = input("Enter the path to your movies file: ").strip()
            try:
                movies = load_movies_file(path)
                print("📁 Movies file loaded successfully.")
                if movies and ratings:
                    print("✅ All data files are loaded. You can use all features.\n")
            except FileNotFoundError:
                print("❌ File not found. Please check your path and try again.")

        # --- Load ratings file ---
        elif choice == "2":
            path = input("Enter the path to your ratings file: ").strip()
            try:
                ratings, user_ratings = load_ratings_file(path)
                print("📁 Ratings file loaded successfully.")
                if movies and ratings:
                    print("✅ All data files are loaded. You can use all features.\n")
            except FileNotFoundError:
                print("❌ File not found. Please check your path and try again.")

        # --- Top N movies ---
        elif choice == "3":
            if not check_data_loaded(movies, ratings):
                continue
            try:
                n = int(input("Enter number of top movies to display: "))
                top_n_movies(movies, ratings, n)
            except ValueError:
                print("❌ Invalid input. Please enter a valid number.") 

        # --- Top N movies in genre ---
        elif choice == "4":
            if not check_data_loaded(movies, ratings):
                continue
            genre = input("Enter genre name: ").strip()
            n = int(input("Enter number of top movies to display: "))
            top_n_movies_in_genre(movies, ratings, genre, n)

        # --- Top N genres ---
        elif choice == "5":
            if not check_data_loaded(movies, ratings):
                continue
            n = int(input("Enter number of top genres to display: "))
            top_n_genres(movies, ratings, n)

        # --- User’s favorite genre ---
        elif choice == "6":
            if not check_data_loaded(movies, ratings):
                continue
            uid = int(input("Enter user ID: "))
            favorite = user_favorite_genre(uid, movies, user_ratings)
            print(f"🎭 User {uid}'s favorite genre is: {favorite}")

        # --- Recommend movies ---
        elif choice == "7":
            if not check_data_loaded(movies, ratings):
                continue
            try:
                user_id = int(input("Enter the user ID: "))
                recommend_movies(movies, ratings, user_ratings, user_id)
            except ValueError:
                print("Invalid user ID. Please enter a valid number.")

        # --- Exit program ---
        elif choice == "8":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()