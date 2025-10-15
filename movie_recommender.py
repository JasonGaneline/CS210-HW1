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


# ------------------------------
# File loading functions
# ------------------------------
def load_movies_file(filename):
    movies = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            genre, movie_id, title = line.strip().split('|')
            movies[title] = {"id": int(movie_id), "genre": genre.lower()}  # 👇 store genre in lowercase
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


# ------------------------------
# Helper functions 
# ------------------------------
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
def top_n_movies(movies, ratings, n):
    """Display top N movies by average rating."""
    from statistics import mean

    if not ratings:
        print("No ratings data available.")
        return

    movie_avg = {movie: mean(rlist) for movie, rlist in ratings.items()}
    sorted_movies = sorted(movie_avg.items(), key=lambda x: x[1], reverse=True)

    print(f"\n🏆 Top {n} Movies by Average Rating:")
    for i, (movie, avg) in enumerate(sorted_movies[:n], 1):
        print(f"{i}. {movie} — {avg:.2f}")


def top_n_movies_in_genre(movies, ratings, genre, n):
    """Display top N movies in a specific genre by average rating."""
    from statistics import mean

    genre = genre.lower()  # 👇 normalize input genre
    genre_movies = {name: ratings[name] for name, data in movies.items()
                    if data["genre"] == genre and name in ratings}

    if not genre_movies:
        print(f"No movies found for genre '{genre}'.")
        return

    movie_avg = {name: mean(rlist) for name, rlist in genre_movies.items()}
    sorted_movies = sorted(movie_avg.items(), key=lambda x: x[1], reverse=True)

    print(f"\n🏆 Top {n} Movies in Genre '{genre.title()}':")
    for i, (movie, avg) in enumerate(sorted_movies[:n], 1):
        print(f"{i}. {movie} — {avg:.2f}")


def top_n_genres(movies, ratings, n):
    """Display top N genres ranked by the average of average movie ratings."""
    from statistics import mean

    if not ratings:
        print("No ratings data available.")
        return

    genre_avg_list = {}
    genre_movies = {}

    for movie_name, data in movies.items():
        genre = data["genre"].lower()  # 👇 ensure lowercase
        if movie_name in ratings:
            genre_movies.setdefault(genre, []).append(mean(ratings[movie_name]))

    for genre, avg_list in genre_movies.items():
        genre_avg_list[genre] = mean(avg_list)

    sorted_genres = sorted(genre_avg_list.items(), key=lambda x: x[1], reverse=True)

    print(f"\n🏆 Top {n} Genres by Average Rating:")
    for i, (genre, avg) in enumerate(sorted_genres[:n], 1):
        print(f"{i}. {genre.title()} — {avg:.2f}")


def user_favorite_genre(user_id, movies, user_ratings):
    """Determine the user's most preferred genre based on their ratings."""
    from statistics import mean

    if user_id not in user_ratings:
        print(f"User {user_id} not found.")
        return None

    genre_scores = {}
    for movie_name, rating in user_ratings[user_id].items():
        if movie_name not in movies:
            continue
        genre = movies[movie_name]["genre"].lower()  # 👇 store lowercase
        genre_scores.setdefault(genre, []).append(rating)

    if not genre_scores:
        return None

    genre_avg = {g: mean(rlist) for g, rlist in genre_scores.items()}
    favorite = max(genre_avg, key=genre_avg.get)
    return favorite


def recommend_movies(movies, ratings, user_ratings, user_id):
    """Recommend top 3 movies from user's favorite genre."""
    favorite_genre = user_favorite_genre(user_id, movies, user_ratings)
    if not favorite_genre:
        print(f"\nCould not determine a favorite genre for user {user_id}.")
        return

    genre_movies = [movie for movie, data in movies.items()
                    if data["genre"].lower() == favorite_genre.lower()]  # 👇 case-insensitive match

    rated_movies = user_ratings.get(user_id, {})
    unrated_movies = [movie for movie in genre_movies if movie not in rated_movies]

    rated_avg = []
    for movie in unrated_movies:
        if movie in ratings and len(ratings[movie]) > 0:
            avg_rating = sum(ratings[movie]) / len(ratings[movie])
            rated_avg.append((movie, avg_rating))

    rated_avg.sort(key=lambda x: x[1], reverse=True)

    if rated_avg:
        print(f"\nTop 3 Recommended Movies for User {user_id} (genre: {favorite_genre.title()}):")
        for i, (movie, avg) in enumerate(rated_avg[:3], start=1):
            print(f"{i}. {movie} — {avg:.2f}")
    else:
        print(f"No available recommendations for user {user_id}'s favorite genre: {favorite_genre.title()}.")


# ------------------------------
# Data validation and CLI
# ------------------------------
def check_data_loaded(movies, ratings):
    """Ensure both data files are loaded before running features."""
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


def main_menu():
    """Command-line interface for the Movie Recommender System."""
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

        if choice == "1":
            path = input("Enter the path to your movies file (or just the name of the file if it is in folder): ").strip()
            try:
                movies = load_movies_file(path)
                print("📁 Movies file loaded successfully.")
                if movies and ratings:
                    print("✅ All data files are loaded. You can use all features.\n")
            except FileNotFoundError:
                print("❌ File not found. Please check your path and try again.")

        elif choice == "2":
            path = input("Enter the path to your ratings file (or just the name of the file if it is in folder): ").strip()
            try:
                ratings, user_ratings = load_ratings_file(path)
                print("📁 Ratings file loaded successfully.")
                if movies and ratings:
                    print("✅ All data files are loaded. You can use all features.\n")
            except FileNotFoundError:
                print("❌ File not found. Please check your path and try again.")

        elif choice == "3":
            if not check_data_loaded(movies, ratings):
                continue
            try:
                n = int(input("Enter number of top movies to display: "))
                top_n_movies(movies, ratings, n)
            except ValueError:
                print("❌ Invalid input. Please enter a valid number.")

        elif choice == "4":
            if not check_data_loaded(movies, ratings):
                continue
            genre = input("Enter genre name: ").strip().lower()  # 👇 force lowercase
            n = int(input("Enter number of top movies to display: "))
            top_n_movies_in_genre(movies, ratings, genre, n)

        elif choice == "5":
            if not check_data_loaded(movies, ratings):
                continue
            n = int(input("Enter number of top genres to display: "))
            top_n_genres(movies, ratings, n)

        elif choice == "6":
            if not check_data_loaded(movies, ratings):
                continue
            uid = int(input("Enter user ID: "))
            favorite = user_favorite_genre(uid, movies, user_ratings)
            if favorite:
                print(f"🎭 User {uid}'s favorite genre is: {favorite.title()}")

        elif choice == "7":
            if not check_data_loaded(movies, ratings):
                continue
            try:
                user_id = int(input("Enter the user ID: "))
                recommend_movies(movies, ratings, user_ratings, user_id)
            except ValueError:
                print("Invalid user ID. Please enter a valid number.")

        elif choice == "8":
            print("🍿 Thanks for using Movie Recommender!")
            break

        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
