import os
import io
import sys
import tempfile
from statistics import mean
import movie_recommender as mr


def create_test_files():
    """Generate valid, invalid, and edge-case test files for movies and ratings."""
    test_dir = tempfile.mkdtemp(prefix="movie_recommender_test_")

    # ✅ Normal movies file (genre|id|title)
    movies_normal = os.path.join(test_dir, "movies_normal.txt")
    with open(movies_normal, "w", encoding="utf-8") as f:
        f.write("action|1|The Matrix\n")
        f.write("romance|2|Titanic\n")
        f.write("sci-fi|3|Inception\n")

    # ⚠️ Abnormal movies file (bad lines)
    movies_bad = os.path.join(test_dir, "movies_bad.txt")
    with open(movies_bad, "w", encoding="utf-8") as f:
        f.write("action|notnum|The Matrix\n")  # bad ID
        f.write("sci-fi|3\n")                  # missing title
        f.write("badformatline\n")             # bad format

    # 🧩 Duplicate movie titles
    movies_dup = os.path.join(test_dir, "movies_dup.txt")
    with open(movies_dup, "w", encoding="utf-8") as f:
        f.write("action|1|The Matrix\n")
        f.write("romance|2|The Matrix\n")  # duplicate title

    # 🧩 Empty movies file
    movies_empty = os.path.join(test_dir, "movies_empty.txt")
    open(movies_empty, "w").close()

    # ✅ Normal ratings file (movie|rating|user)
    ratings_normal = os.path.join(test_dir, "ratings_normal.txt")
    with open(ratings_normal, "w", encoding="utf-8") as f:
        f.write("The Matrix|5|1\n")
        f.write("Titanic|3.5|1\n")
        f.write("Inception|4|2\n")
        f.write("Inception|5|3\n")
        f.write("Titanic|2|2\n")

    # ⚠️ Abnormal ratings file
    ratings_bad = os.path.join(test_dir, "ratings_bad.txt")
    with open(ratings_bad, "w", encoding="utf-8") as f:
        f.write("The Matrix|6|1\n")  # invalid rating
        f.write("Titanic|3.5|\n")    # missing user ID
        f.write("bad|data|line\n")   # bad numeric format

    # 🧩 Negative ratings test
    ratings_negative = os.path.join(test_dir, "ratings_negative.txt")
    with open(ratings_negative, "w", encoding="utf-8") as f:
        f.write("Titanic|-1|3\n")  # invalid (negative)
        f.write("Inception|5|2\n")  # valid

    # 🧩 Empty ratings file
    ratings_empty = os.path.join(test_dir, "ratings_empty.txt")
    open(ratings_empty, "w").close()

    return {
        "movies_normal": movies_normal,
        "movies_bad": movies_bad,
        "movies_dup": movies_dup,
        "movies_empty": movies_empty,
        "ratings_normal": ratings_normal,
        "ratings_bad": ratings_bad,
        "ratings_negative": ratings_negative,
        "ratings_empty": ratings_empty,
    }


def capture_output(func, *args, **kwargs):
    """Capture printed output from a function call."""
    buffer = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"[Exception Raised] {e}")
    finally:
        sys.stdout = sys_stdout
    return buffer.getvalue().strip()

def silent_call(func, *args, **kwargs):
    """Run a function silently by discarding printed output."""
    buffer = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer
    try:
        return func(*args, **kwargs)
    finally:
        sys.stdout = sys_stdout

def print_result(test_name, actual, expected):
    """Pretty print test comparison."""
    print(f"\n🔹 {test_name}")
    print(f"   Expected: {expected}")
    print(f"   Actual:   {actual}")
    if actual == expected or (isinstance(expected, (list, dict, set)) and actual == expected):
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL")


def run_tests():
    print("🎬 Running automated tests for movie_recommender.py...\n")
    files = create_test_files()

    # --- Test 1: load_movies_file (normal) ---
    movies = silent_call(mr.load_movies_file, files["movies_normal"])
    print_result("load_movies_file (normal)", len(movies), 3)

    # --- Test 2: load_movies_file (bad input) ---
    movies_bad = silent_call(mr.load_movies_file, files["movies_bad"])
    print_result("load_movies_file (bad input)", len(movies_bad), 0)

    # --- Test 3: duplicate titles ---
    movies_dup = silent_call(mr.load_movies_file, files["movies_dup"])
    print_result("duplicate titles", len(movies_dup), 1)

    # --- Test 4: empty movies file ---
    movies_empty = silent_call(mr.load_movies_file, files["movies_empty"])
    print_result("empty movies file", movies_empty, {})

    # --- Test 5: load_ratings_file (normal) ---
    ratings, user_ratings = silent_call(mr.load_ratings_file, files["ratings_normal"])
    print_result("load_ratings_file (normal) - movies rated", len(ratings), 3)
    print_result("load_ratings_file (normal) - users found", len(user_ratings), 3)

    # --- Test 6: load_ratings_file (bad) ---
    ratings_bad, _ = silent_call(mr.load_ratings_file, files["ratings_bad"])
    print_result("load_ratings_file (bad input)", len(ratings_bad), 0)

    # --- Test 7: negative ratings ---
    ratings_neg, _ = silent_call(mr.load_ratings_file, files["ratings_negative"])
    print_result("negative ratings - valid entries", list(ratings_neg.keys()), ["Inception"])

    # --- Test 8: empty ratings file ---
    ratings_empty, user_ratings_empty = silent_call(mr.load_ratings_file, files["ratings_empty"])
    print_result("empty ratings file - ratings", ratings_empty, {})
    print_result("empty ratings file - user ratings", user_ratings_empty, {})

    # --- Test 9: top_n_movies ---
    output = capture_output(mr.top_n_movies, movies, ratings, 2)
    print_result("top_n_movies (print check)", "Top 2 Movies" in output, True)

    # --- Test 10: top_n_movies_in_genre ---
    output = capture_output(mr.top_n_movies_in_genre, movies, ratings, "Action", 1)
    print_result("top_n_movies_in_genre (print check)", "Action" in output, True)

    # --- Test 11: unrated movie exclusion ---
    movies_extra = dict(movies)
    movies_extra["Ghost Movie"] = {"id": 9, "genre": "action"}
    output = capture_output(mr.top_n_movies_in_genre, movies_extra, ratings, "Action", 5)
    print_result("unrated movie exclusion", "Ghost Movie" in output, False)

    # --- Test 12: top_n_genres ---
    output = capture_output(mr.top_n_genres, movies, ratings, 3)
    print_result("top_n_genres (print check)", "Top 3 Genres" in output, True)

    # --- Test 13: user_favorite_genre ---
    fav = silent_call(mr.user_favorite_genre, 1, movies, user_ratings)
    print_result("user_favorite_genre (user 1)", fav in ("action", "romance"), True)

    # --- Test 14: user_favorite_genre with unknown movie ---
    fake_user_ratings = {1: {"Unknown Movie": 4.0}}
    fav = silent_call(mr.user_favorite_genre, 1, movies, fake_user_ratings)
    print_result("user_favorite_genre (unknown movie)", fav, None)

    # --- Test 15: recommend_movies ---
    output = capture_output(mr.recommend_movies, movies, ratings, user_ratings, 1)
    print_result("recommend_movies (user 1)", "Recommended" in output or "No available" in output, True)

    # --- Test 16: recommend_movies (unknown user) ---
    output = capture_output(mr.recommend_movies, movies, ratings, user_ratings, 999)
    print_result("recommend_movies (unknown user)", "Could not determine" in output, True)

    # --- Test 17: check_data_loaded ---
    print_result("check_data_loaded (valid)", silent_call(mr.check_data_loaded, movies, ratings), True)
    print_result("check_data_loaded (missing movies)", silent_call(mr.check_data_loaded, {}, ratings), False)
    print_result("check_data_loaded (missing ratings)", silent_call(mr.check_data_loaded, movies, {}), False)
    print_result("check_data_loaded (missing both)", silent_call(mr.check_data_loaded, {}, {}), False)

    # --- Test 18: FileNotFoundError handling ---
    output = capture_output(mr.load_movies_file, "nonexistent_file.txt")
    print_result("FileNotFoundError handling", "not found" in output.lower(), True)

    print("\n🎉 ALL TESTS FINISHED 🎉")

if __name__ == "__main__":
    run_tests()