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
ratings = {}      # movie_name -> list of ratings
user_ratings = {} # user_id -> dict of movie_name -> rating


# ------------------------------
# File loading functions
# ------------------------------
def load_movies_file(filename):
    movies = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                parts = line.split('|')
                if len(parts) != 3:
                    print(f"Skipping line {line_num}: wrong number of fields -> {line}")
                    continue

                try:
                    genre = parts[0].strip().lower()
                    movie_id = int(parts[1])
                    title = parts[2].strip().title()

                    if title in movies:
                        print(f"Skipping line {line_num}: duplicate movie title '{title}'")
                        continue

                    movies[title] = {"id": movie_id, "genre": genre}

                except ValueError:
                    print(f"Skipping line {line_num}: invalid movie ID -> {line}")
                    continue
    except FileNotFoundError:
        print(f"Error: Movies file '{filename}' not found.")
    except Exception as e:
        print(f"Unexpected error while loading movies: {e}")
    return movies


def load_ratings_file(filename):
    ratings = {}
    user_ratings = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue  # skip blank lines

                parts = line.split('|')
                if len(parts) != 3:
                    print(f"Skipping line {line_num}: wrong number of fields -> {line}")
                    continue

                try:
                    movie_name = parts[0].strip().title()
                    rating = float(parts[1])
                    user_id = int(parts[2])

                    # Validate rating range
                    if not (0 <= rating <= 5):
                        print(f"Skipping line {line_num}: invalid rating '{rating}' -> {line}")
                        continue

                    # Add to movie ratings
                    ratings.setdefault(movie_name, []).append(rating)

                    # Add to user ratings
                    user_ratings.setdefault(user_id, {})[movie_name] = rating

                except ValueError:
                    print(f"Skipping line {line_num}: invalid numeric value -> {line}")
                    continue

    except FileNotFoundError:
        print(f"Error: Ratings file '{filename}' not found.")
    except Exception as e:
        print(f"Unexpected error while loading ratings: {e}")

    return ratings, user_ratings


# ------------------------------
# Helper functions 
# ------------------------------
def average_rating_for_movie(movie_name):
    """Compute the average rating for a single movie."""
    if movie_name not in ratings or len(ratings[movie_name]) == 0:
        return 0.0
    return mean(ratings[movie_name])


def movie_average_map():
    """Return a dict mapping movie_name -> average_rating."""
    return {m: average_rating_for_movie(m) for m in ratings}


# ------------------------------
# Program features
# ------------------------------
def top_n_movies(movies, ratings, n):
    """Display top N movies by average rating."""
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
    genre = genre.lower()

    # Filter movies in that genre that have ratings
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
    if not ratings:
        print("No ratings data available.")
        return

    genre_movies = {}
    for movie_name, data in movies.items():
        genre = data["genre"].lower()
        if movie_name in ratings:
            genre_movies.setdefault(genre, []).append(mean(ratings[movie_name]))

    genre_avg = {g: mean(vals) for g, vals in genre_movies.items()}
    sorted_genres = sorted(genre_avg.items(), key=lambda x: x[1], reverse=True)

    print(f"\n🏆 Top {n} Genres by Average Rating:")
    for i, (genre, avg) in enumerate(sorted_genres[:n], 1):
        print(f"{i}. {genre.title()} — {avg:.2f}")


def user_favorite_genre(user_id, movies, user_ratings):
    """Determine the user's most preferred genre based on their ratings."""
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

    genre_avg = {g: mean(vals) for g, vals in genre_scores.items()}
    return max(genre_avg, key=genre_avg.get)


def recommend_movies(movies, ratings, user_ratings, user_id):
    """Recommend top 3 movies from user's favorite genre."""
    favorite_genre = user_favorite_genre(user_id, movies, user_ratings)
    if not favorite_genre:
        print(f"\nCould not determine a favorite genre for user {user_id}.")
        return

    genre_movies = [m for m, d in movies.items() if d["genre"] == favorite_genre]
    rated = user_ratings.get(user_id, {})
    unrated = [m for m in genre_movies if m not in rated]

    rated_avg = [(m, mean(ratings[m])) for m in unrated if m in ratings and ratings[m]]
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
            path = input("Enter the path to your movies file: ").strip()
            movies = load_movies_file(path)
            if movies:
                print(f"📁 Movies file loaded successfully. ({len(movies)} movies)")
            else:
                print("⚠️  No movies loaded. Please check the file path or file format.")

        elif choice == "2":
            path = input("Enter the path to your ratings file: ").strip()
            ratings, user_ratings = load_ratings_file(path)
            if ratings and user_ratings:
                print(f"📁 Ratings file loaded successfully. ({len(ratings)} movies rated)")
            else:
                print("⚠️  No ratings loaded. Please check the file path or file format.")

        elif choice == "3":
            if not check_data_loaded(movies, ratings):
                continue
            try:
                n = int(input("Enter number of top movies to display: "))
                top_n_movies(movies, ratings, n)
            except ValueError:
                print("❌ Please enter a valid number.")

        elif choice == "4":
            if not check_data_loaded(movies, ratings):
                continue
            genre = input("Enter genre name: ").strip()
            try:
                n = int(input("Enter number of top movies to display: "))
                top_n_movies_in_genre(movies, ratings, genre, n)
            except ValueError:
                print("❌ Please enter a valid number.")

        elif choice == "5":
            if not check_data_loaded(movies, ratings):
                continue
            unique_genres = set(data["genre"] for data in movies.values())
            max_genres = len(unique_genres)
            try:
                n = int(input(f"Enter number of top genres to display (max {max_genres}): "))
                if n <= 0:
                    print("❌ Please enter a positive integer.")
                    continue
                if n > max_genres:
                    print(f"⚠️ You requested more genres than available. Showing top {max_genres} genres instead.")
                    n = max_genres
                top_n_genres(movies, ratings, n)
            except ValueError:
                print("❌ Please enter a valid number.")

        elif choice == "6":
            if not check_data_loaded(movies, ratings):
                continue
            try:
                uid = int(input("Enter user ID: "))
                fav = user_favorite_genre(uid, movies, user_ratings)
                if fav:
                    print(f"🎭 User {uid}'s favorite genre is: {fav.title()}")
            except ValueError:
                print("❌ Please enter a valid user ID (number).")

        elif choice == "7":
            if not check_data_loaded(movies, ratings):
                continue
            try:
                uid = int(input("Enter user ID: "))
                recommend_movies(movies, ratings, user_ratings, uid)
            except ValueError:
                print("❌ Please enter a valid user ID (number).")

        elif choice == "8":
            print("🍿 Thank you for using Movie Recommender!")
            break

        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()