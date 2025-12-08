# test_music_db_expanded.py (CORRECTED EXPECTED VALUES)
from mysql.connector import connect, Error
from music_db import (
    clear_database, load_single_songs, load_albums, load_users, load_song_ratings,
    get_most_prolific_individual_artists, get_artists_last_single_in_year,
    get_top_song_genres, get_album_and_single_artists, get_most_rated_songs,
    get_most_engaged_users
)

# --- Configuration ---
DB_CONFIG = {
    'unix_socket': '/run/mysqld/mysqld.sock', 
    'database': 'jgg114_musicdb',            
}
# ---------------------

def print_comparison(description, expected, actual):
    """Prints the expected and actual results for easy comparison."""
    is_match = expected == actual
    status = "PASS" if is_match else "FAIL"
    print(f"\n--- {description} ({status}) ---")
    print("Expected:", expected)
    print("Actual  :", actual)

def main():
    try:
        mydb = connect(**DB_CONFIG)
        print("Connected to the database!")

        # ----------------------------------------------------
        # 0. SETUP: Clear DB
        # ----------------------------------------------------
        clear_database(mydb)
        # ... (Loading functions remain the same as the data is correct)

        # ----------------------------
        # Load Users
        # ----------------------------
        users_to_load = ['alice', 'bob', 'charlie', 'diana', 'emily', 'frank']
        load_users(mydb, users_to_load)
        new_users = ['bob', 'greg', 'diana']
        actual_user_rejects = load_users(mydb, new_users)
        expected_user_rejects = {'bob', 'diana'}
        print_comparison("1. load_users rejects (Duplicate Check)", expected_user_rejects, actual_user_rejects)

        # ----------------------------
        # Load Singles
        # ----------------------------
        singles = [
            ('Shake It Off', ('Pop',), 'Taylor Swift', '2014-08-18'),
            ('Bad Blood', ('Pop', 'Hip-Hop'), 'Taylor Swift', '2015-05-17'),
            ('Blank Space', ('Pop',), 'Taylor Swift', '2014-11-10'),
            ('Shape of You', ('Pop',), 'Ed Sheeran', '2017-01-06'),
            ('Perfect', ('Pop',), 'Ed Sheeran', '2017-09-29'),
            ('Hello', ('Pop', 'Soul'), 'Adele', '2015-10-23'),
            ('Skyfall', ('Jazz',), 'Adele', '2012-10-05'),
            ('Digital Love', ('Electronic',), 'Ed Sheeran', '2023-01-01'),
            ('Enter Sandman', ('Rock',), 'Metallica', '1991-07-29'),
            ('The Unforgiven', ('Rock',), 'Metallica', '1991-10-28'),
            ('No Genre Single', (), 'Taylor Swift', '2020-01-01'),
            ('Perfect', ('Rock',), 'Ed Sheeran', '2018-01-01'),
        ]
        actual_singles_rejects = load_single_songs(mydb, singles)
        expected_singles_rejects = {('No Genre Single', 'Taylor Swift'), ('Perfect', 'Ed Sheeran')}
        print_comparison("2. load_single_songs rejects", expected_singles_rejects, actual_singles_rejects)

        # ----------------------------
        # Load Albums
        # ----------------------------
        albums = [
            ('Discovery', 'Electronic', 'Daft Punk', '2001-03-13',
             ['One More Time', 'Digital Love', 'Aerodynamic']),
            ('25', 'Soul', 'Adele', '2015-11-20',
             ['When We Were Young', 'Water Under The Bridge', 'Hello']),
            ('Discovery', 'Rock', 'Daft Punk', '2005-01-01', ['New Song']),
            ('Dookie', 'Rock', 'Green Day', '1994-02-01', 
             ['Basket Case', 'When I Come Around']),
        ]
        actual_albums_rejects = load_albums(mydb, albums)
        expected_albums_rejects = {('Discovery', 'Daft Punk')}
        print_comparison("3. load_albums rejects", expected_albums_rejects, actual_albums_rejects)
        
        cur = mydb.cursor(buffered=True)
        cur.execute("SELECT COUNT(song_id) FROM songs s JOIN artists a ON s.artist_id = a.artist_id WHERE a.name = 'Adele' AND s.album_id IS NOT NULL")
        actual_adele_album_songs = cur.fetchone()[0]
        cur.close()
        print_comparison("3. load_albums song skip check", 2, actual_adele_album_songs)

        # ----------------------------
        # Load Ratings
        # ----------------------------
        ratings = [
            ('alice', ('Taylor Swift', 'Bad Blood'), 5, '2024-03-01'), 
            ('bob', ('Taylor Swift', 'Bad Blood'), 4, '2024-04-01'),
            ('charlie', ('Taylor Swift', 'Bad Blood'), 3, '2024-05-01'),
            ('diana', ('Daft Punk', 'Aerodynamic'), 5, '2025-01-01'),
            ('emily', ('tAyLoR sWiFt', 'bAd BlOoD'), 4, '2024-06-01'),
            ('unknown', ('Taylor Swift', 'Shake It Off'), 3, '2024-01-01'), 
            ('alice', ('Metallica', 'Fade To Black'), 3, '2024-02-01'), 
            ('alice', ('Taylor Swift', 'Bad Blood'), 1, '2024-03-02'), 
            ('frank', ('Ed Sheeran', 'Perfect'), 0, '2024-07-01'), 
            ('greg', ('Ed Sheeran', 'Shape of You'), 6, '2024-08-01'),
        ]
        actual_rating_rejects = load_song_ratings(mydb, ratings)
        expected_rating_rejects = {
            ('unknown', 'Taylor Swift', 'Shake It Off'),
            ('alice', 'Metallica', 'Fade To Black'),
            ('alice', 'Taylor Swift', 'Bad Blood'),
            ('frank', 'Ed Sheeran', 'Perfect'),
            ('greg', 'Ed Sheeran', 'Shape of You'),
        }
        print_comparison("4. load_song_ratings rejects (4 Types)", expected_rating_rejects, actual_rating_rejects)

        # ----------------------------
        # 5. QUERY TESTS
        # ----------------------------

        # 5a. get_most_prolific_individual_artists (n=3, year_range=(2010, 2020))
        # CORRECTED: Adele (4) > TS (3) > ES (2).
        actual_prolific = get_most_prolific_individual_artists(mydb, 3, (2010, 2020))
        expected_prolific = [('Adele', 4), ('Taylor Swift', 3), ('Ed Sheeran', 2)]
        print_comparison("5a. get_most_prolific_individual_artists", expected_prolific, actual_prolific)

        # 5b. get_artists_last_single_in_year (year=2015)
        actual_artists_2015 = get_artists_last_single_in_year(mydb, 2015)
        expected_artists_2015 = {'Adele', 'Taylor Swift'}
        print_comparison("5b. get_artists_last_single_in_year (2015)", expected_artists_2015, actual_artists_2015)

        # 5c. get_top_song_genres (n=4)
        # CORRECTED: Pop count is 6.
        actual_top_genres = get_top_song_genres(mydb, 4)
        expected_top_genres = [('Pop', 6), ('Electronic', 4), ('Rock', 4), ('Soul', 3)]
        print_comparison("5c. get_top_song_genres", expected_top_genres, actual_top_genres)

        # 5d. get_album_and_single_artists
        actual_both_artists = get_album_and_single_artists(mydb)
        expected_both_artists = {'Adele'}
        print_comparison("5d. get_album_and_single_artists", expected_both_artists, actual_both_artists)

        # 5e. get_most_rated_songs (n=2, year_range=(2014, 2017))
        actual_most_rated = get_most_rated_songs(mydb, (2014, 2017), 2)
        expected_most_rated = [('Bad Blood', 'Taylor Swift', 4)]
        print_comparison("5e. get_most_rated_songs (Release Date Filter)", expected_most_rated, actual_most_rated)
        
        # 5f. get_most_engaged_users (n=3, year_range=(2024, 2024))
        # CORRECTED: Alice only has 1 valid 2024 rating.
        actual_engaged_users = get_most_engaged_users(mydb, (2024, 2024), 3)
        expected_engaged_users = [('alice', 1), ('bob', 1), ('charlie', 1)]
        print_comparison("5f. get_most_engaged_users (Rating Date Filter)", expected_engaged_users, actual_engaged_users)

        mydb.close()
        print("\n--- All Tests Executed ---")

    except Error as e:
        print(f"\n[DATABASE ERROR] Connection or Query failed: {e}")


if __name__ == "__main__":
    main()