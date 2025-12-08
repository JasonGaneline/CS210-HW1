# test2.py
import mysql.connector
from music_db import (
    clear_database, load_users, load_single_songs, load_albums, load_song_ratings,
    get_most_prolific_individual_artists, get_artists_last_single_in_year,
    get_top_song_genres, get_album_and_single_artists, get_most_rated_songs,
    get_most_engaged_users
)

# --- Configuration ---
DB_CONFIG = {
    'unix_socket': '/run/mysqld/mysqld.sock', # Adjust as needed
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

def load_initial_dump_data(mydb):
    """
    Loads data directly derived from the SQL dump INSERT statements
    using your implemented load_* functions.
    """
    
    print("\n--- Loading Data from SQL Dump Inserts ---")
    
    # 1. USERS
    initial_users = ['alice', 'bob', 'charlie', 'diana']
    load_users(mydb, initial_users)

    # 2. SINGLES (Requires manual mapping from dump, where album_id is NULL and is_single=1)
    # 8: ('Everything In Its Right Place', 1, NULL, '2000-05-15', 1) -> Genre 5 (R&B)
    # 9: ('HUMBLE.', 2, NULL, '2017-03-30', 1) -> Genre 5 (R&B)
    # 10: ('Get Lucky', 3, NULL, '2013-04-19', 1) -> Genre 5 (R&B)
    # 11: ('N95', 2, NULL, '2022-04-14', 1) -> Genre 2 (Pop)
    # 12: ('Loose Single', 5, NULL, '2023-01-20', 1) -> Genre 2 (Pop)
    singles = [
        ('Everything In Its Right Place', ('R&B',), 'Radiohead', '2000-05-15'),
        ('HUMBLE.', ('R&B',), 'Kendrick Lamar', '2017-03-30'),
        ('Get Lucky', ('R&B',), 'Daft Punk', '2013-04-19'),
        ('N95', ('Pop',), 'Kendrick Lamar', '2022-04-14'),
        ('Loose Single', ('Pop',), 'Coldplay', '2023-01-20'),
    ]
    load_single_songs(mydb, singles)
    
    # 3. ALBUMS (Note: Album songs inherit the album's single genre)
    # 1: ('OK Computer', 1, 1, '1997-06-16', 1(Rock)) -> Songs: Paranoid Android, Karma Police
    # 2: ('Lemonade', 4, 4, '2016-04-23', 5(R&B)) -> Songs: Formation, Sorry, Hold Up
    # 3: ('A Head Full of Dreams', 5, 5, '2015-12-04', 2(Pop)) -> Songs: Adventure of a Lifetime, Hymn for the Weekend
    albums = [
        ('OK Computer', 'Rock', 'Radiohead', '1997-06-16', 
         ['Paranoid Android', 'Karma Police']),
        ('Lemonade', 'R&B', 'Beyoncé', '2016-04-23', 
         ['Formation', 'Sorry', 'Hold Up']),
        ('A Head Full of Dreams', 'Pop', 'Coldplay', '2015-12-04', 
         ['Adventure of a Lifetime', 'Hymn for the Weekend']),
    ]
    load_albums(mydb, albums)
    
    # 4. RATINGS (Requires mapping song/artist names to the specific IDs)
    # (user_id, song_id, rating, date)
    # U1(alice): S1(P.A., R), S2(K.P., R)
    # U2(bob): S3(Formation, B), S8(Everything..., R)
    # U3(charlie): S11(N95, K.L.)
    # U4(diana): S4(Sorry, B), S5(Hold Up, B)
    ratings = [
        ('alice', ('Radiohead', 'Paranoid Android'), 5, '2023-01-10'),
        ('alice', ('Radiohead', 'Karma Police'), 4, '2023-01-11'),
        ('bob', ('Beyoncé', 'Formation'), 5, '2023-01-12'),
        ('bob', ('Radiohead', 'Everything In Its Right Place'), 3, '2023-01-12'),
        ('charlie', ('Kendrick Lamar', 'N95'), 4, '2023-01-15'),
        ('diana', ('Beyoncé', 'Sorry'), 5, '2023-02-01'),
        ('diana', ('Beyoncé', 'Hold Up'), 2, '2023-02-02'),
    ]
    load_song_ratings(mydb, ratings)
    
    print("--- Data Loading Complete ---")


def run_verification_tests():
    print("--- Starting Full-Cycle Verification Tests ---")
    
    try:
        mydb = mysql.connector.connect(**DB_CONFIG)
        print("Connected to the database!")

        # 0. SETUP
        clear_database(mydb)
        load_initial_dump_data(mydb)
        
        # ----------------------------------------------------
        # 1. Test get_most_prolific_individual_artists
        # ----------------------------------------------------
        # Count (2010-2024):
        # R: 0 (1997, 2000)
        # KL: 2 (HUMBLE. 2017, N95 2022)
        # DP: 1 (Get Lucky 2013)
        # B: 3 (Formation, Sorry, Hold Up 2016)
        # C: 3 (Adventure, Hymn 2015, Loose Single 2023)
        # Expected: B(3), C(3), KL(2)
        actual_prolific = get_most_prolific_individual_artists(mydb, 3, (2010, 2024))
        expected_prolific = [('Beyoncé', 3), ('Coldplay', 3), ('Kendrick Lamar', 2)]
        print_comparison("1. get_most_prolific_individual_artists (2010-2024)", expected_prolific, actual_prolific)

        # ----------------------------------------------------
        # 2. Test get_artists_last_single_in_year
        # ----------------------------------------------------
        # Last Singles: R(2000), KL(2022), DP(2013), B(None), C(2023)
        # Test Year 2022: Should only get KL
        actual_artists_2022 = get_artists_last_single_in_year(mydb, 2022)
        expected_artists_2022 = {'Kendrick Lamar'}
        print_comparison("2. get_artists_last_single_in_year (2022)", expected_artists_2022, actual_artists_2022)

        # ----------------------------------------------------
        # 3. Test get_top_song_genres
        # ----------------------------------------------------
        # R&B: 3 (Album B) + 3 (Singles R, KL, DP) = 6
        # Pop: 2 (Album C) + 2 (Singles KL, C) = 4
        # Rock: 2 (Album R) = 2
        # Expected: R&B(6), Pop(4), Rock(2)
        actual_top_genres = get_top_song_genres(mydb, 3)
        expected_top_genres = [('R&B', 6), ('Pop', 4), ('Rock', 2)]
        print_comparison("3. get_top_song_genres", expected_top_genres, actual_top_genres)

        # ----------------------------------------------------
        # 4. Test get_album_and_single_artists
        # ----------------------------------------------------
        # R: Album + Single -> BOTH
        # KL: Single Only
        # DP: Single Only
        # B: Album Only
        # C: Album + Single -> BOTH
        actual_both = get_album_and_single_artists(mydb)
        expected_both = {'Radiohead', 'Coldplay'}
        print_comparison("4. get_album_and_single_artists", expected_both, actual_both)

        # ----------------------------------------------------
        # 5. Test get_most_rated_songs (by SONG RELEASE DATE)
        # ----------------------------------------------------
        # n=2, year_range=(1995, 2020)
        # All 7 rated songs have 1 rating. Filter by song release year:
        # P.A. (1997), K.P. (1997), Formation (2016), E.I.I.R.P. (2000), Sorry (2016), Hold Up (2016) -> All IN RANGE
        # N95 (2022) -> OUT OF RANGE
        # Tie-breaker (Title ASC): 1. Everything..., 2. Formation
        actual_rated = get_most_rated_songs(mydb, (1995, 2020), 2)
        expected_rated = [
            ('Everything In Its Right Place', 'Radiohead', 1),
            ('Formation', 'Beyoncé', 1)
        ]
        print_comparison("5. get_most_rated_songs (Release Date Filter)", expected_rated, actual_rated)
        
        # ----------------------------------------------------
        # 6. Test get_most_engaged_users (by RATING DATE)
        # ----------------------------------------------------
        # n=2, year_range=(2023, 2023)
        # All ratings are in 2023. Counts: alice(2), bob(2), charlie(1), diana(2)
        # Ranks: 1. alice(2), 2. bob(2) [Tied, A before B, D]
        actual_engaged = get_most_engaged_users(mydb, (2023, 2023), 2)
        expected_engaged = [('alice', 2), ('bob', 2)]
        print_comparison("6. get_most_engaged_users (Rating Date Filter)", expected_engaged, actual_engaged)

        mydb.close()
        print("\n--- Verification Complete ---")

    except mysql.connector.Error as err:
        print(f"\n[MYSQL ERROR] Something went wrong: {err}")
        print("Please ensure your database is running and the credentials in DB_CONFIG are correct.")
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

if __name__ == "__main__":
    run_verification_tests()