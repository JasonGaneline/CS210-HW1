from mysql.connector import connect, Error
from typing import Set, Tuple, List
from music_db import (
    clear_database, load_single_songs, load_albums, load_users, load_song_ratings,
    get_most_prolific_individual_artists, get_artists_last_single_in_year,
    get_top_song_genres, get_album_and_single_artists, get_most_rated_songs,
    get_most_engaged_users
)

# --- Configuration ---
# IMPORTANT: Update these with your actual database credentials
DB_CONFIG = {
    'unix_socket': '/run/mysqld/mysqld.sock', 
    'database': 'jgg114_musicdb', 
    # Add 'user' and 'password' if you are NOT using a unix socket
    # 'user': 'your_user',
    # 'password': 'your_password',
}
# ---------------------

def print_comparison(description, expected, actual):
    """Prints the expected and actual results for easy comparison."""
    # Handle sets correctly for comparison
    is_match = False
    if isinstance(expected, Set) and isinstance(actual, Set):
        is_match = expected == actual
    elif isinstance(expected, Set) and isinstance(actual, set):
        is_match = expected == actual
    elif isinstance(expected, set) and isinstance(actual, Set):
        is_match = expected == actual
    elif isinstance(expected, list) and isinstance(actual, list):
        is_match = expected == actual
    elif isinstance(expected, tuple) and isinstance(actual, tuple):
        is_match = expected == actual
    # Handles simple types like int/bool/str
    else:
        is_match = expected == actual
        
    status = "PASS" if is_match else "FAIL"
    print(f"\n--- {description} ({status}) ---")
    print("Expected:", expected)
    print("Actual  :", actual)
    return is_match # Return status for overall tally

def main():
    overall_status = []
    
    try:
        # Establish connection using the specified style
        mydb = connect(**DB_CONFIG)
        print("Connected to the database!")

        # ----------------------------------------------------
        # 0. SETUP: Clear DB
        # ----------------------------------------------------
        clear_database(mydb)

        # ----------------------------
        # Load Users (Test 1)
        # ----------------------------
        users_to_load = ['alice', 'bob', 'charlie', 'diana', 'emily', 'frank']
        load_users(mydb, users_to_load)
        new_users = ['bob', 'greg', 'diana']
        actual_user_rejects = load_users(mydb, new_users)
        expected_user_rejects = {'bob', 'diana'}
        status = print_comparison("1. load_users rejects (Duplicate Check)", expected_user_rejects, actual_user_rejects)
        overall_status.append(status)

        # ----------------------------
        # Load Singles (Test 2)
        # ----------------------------
        singles = [
            ('Shake It Off', ('Pop',), 'Taylor Swift', '2014-08-18'),
            ('Bad Blood', ('Pop', 'Hip-Hop'), 'Taylor Swift', '2015-05-17'),
            ('Blank Space', ('Pop',), 'Taylor Swift', '2014-11-10'),
            ('Shape of You', ('Pop',), 'Ed Sheeran', '2017-01-06'), # Used for Cross-Artist Reject Test
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
        status = print_comparison("2. load_single_songs rejects", expected_singles_rejects, actual_singles_rejects)
        overall_status.append(status)

        # ----------------------------
        # Load Albums (Test 3, 4, and 5)
        # ----------------------------
        albums = [
            # 1. Base Album (Daft Punk)
            ('Discovery', 'Electronic', 'Daft Punk', '2001-03-13',
             ['One More Time', 'Digital Love', 'Aerodynamic']),
             
            # 2. Setup Album: Makes 'Blank Space' an ALBUM TRACK (Setup for Test 5)
            # This also promotes 'Bad Blood' and 'Shake It Off' is left as a single.
            ('1989', 'Pop', 'Taylor Swift', '2014-10-27',
             ['Blank Space', 'Bad Blood', 'Style', 'Out of the Woods']), 
             
            # 3. Promotion Test: 'Hello' gets promoted (Test 4 Scenario)
            ('25', 'Soul', 'Adele', '2015-11-20',
             ['When We Were Young', 'Water Under The Bridge', 'Hello']),
             
            # 4. Rejection Test: Duplicate Album (Test 3)
            ('Discovery', 'Rock', 'Daft Punk', '2005-01-01', ['New Song']), 
            
            # 5. REJECTION TEST: Duplicates EXISTING ALBUM TRACK 'Blank Space' (Test 5 Failure)
            ('Fake Album Rejected - Album Track', 'Pop', 'Taylor Swift', '2020-01-01', 
             ['Blank Space', 'New Track 2']), 
             
            # 6. REJECTION TEST: Duplicates single 'Shape of You' but by WRONG artist (Test 4 variant)
            ('Fake Album Rejected - Cross Artist', 'Pop', 'Taylor Swift', '2020-01-02', 
             ['Shape of You', 'New Track 3']),
             
            # 7. New Album
            ('Dookie', 'Rock', 'Green Day', '1994-02-01', 
             ['Basket Case', 'When I Come Around']), 
        ]
        
        actual_albums_rejects = load_albums(mydb, albums)
        
        # Expected rejects now includes the duplicate album, the album track conflict (Test 5), 
        # and the cross-artist conflict (Test 4 edge case).
        expected_albums_rejects = {
            ('Discovery', 'Daft Punk'), 
            ('Fake Album Rejected - Album Track', 'Taylor Swift'),
            ('Fake Album Rejected - Cross Artist', 'Taylor Swift') 
        }
        
        status = print_comparison("3. load_albums rejects (Tests 3, 4, 5)", expected_albums_rejects, actual_albums_rejects)
        overall_status.append(status)
        
        # 3. load_albums song skip check (Internal Autograder Check)
        cur = mydb.cursor(buffered=True)
        # Count only the NEW songs on Adele's album '25'
        cur.execute("""
            SELECT COUNT(song_id) 
            FROM songs s 
            JOIN artists a ON s.artist_id = a.artist_id 
            JOIN albums al ON s.album_id = al.album_id
            WHERE a.name = 'Adele' AND al.title = '25' AND s.title NOT IN ('Hello');
        """)
        actual_adele_album_songs = cur.fetchone()[0]
        expected_adele_album_songs = 2 
        status = print_comparison("3. load_albums song skip check", expected_adele_album_songs, actual_adele_album_songs)
        overall_status.append(status)
        cur.close()

        # ----------------------------
        # Load Ratings (Test 4)
        # ----------------------------
        ratings = [
            # Bad Blood Ratings: 3 valid
            ('alice', ('Taylor Swift', 'Bad Blood'), 5, '2024-03-01'), 
            ('bob', ('Taylor Swift', 'Bad Blood'), 4, '2024-04-01'),
            ('charlie', ('Taylor Swift', 'Bad Blood'), 3, '2024-05-01'),
            
            # Other Valid Ratings
            ('diana', ('Daft Punk', 'Aerodynamic'), 5, '2025-01-01'),
            ('emily', ('Taylor Swift', 'Blank Space'), 4, '2024-06-01'),
            
            # Rejects
            ('unknown', ('Taylor Swift', 'Shake It Off'), 3, '2024-01-01'), 
            ('alice', ('Metallica', 'Fade To Black'), 3, '2024-02-01'), 
            ('alice', ('Taylor Swift', 'Bad Blood'), 1, '2024-03-02'), # Reject: Duplicate
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
        status = print_comparison("4. load_song_ratings rejects (4 Types)", expected_rating_rejects, actual_rating_rejects)
        overall_status.append(status)

        # ----------------------------
        # 5. QUERY TESTS
        # ----------------------------

        # 5a. get_most_prolific_individual_artists
        actual_prolific = get_most_prolific_individual_artists(mydb, 3, (2010, 2020))
        expected_prolific = [('Adele', 4), ('Taylor Swift', 3), ('Ed Sheeran', 2)]
        status = print_comparison("5a. get_most_prolific_individual_artists", expected_prolific, actual_prolific)
        overall_status.append(status)

        # 5b. get_artists_last_single_in_year (2015) - Still expected to fail for Adele
        actual_artists_2015 = get_artists_last_single_in_year(mydb, 2015)
        expected_artists_2015 = {'Taylor Swift'} 
        status = print_comparison("5b. get_artists_last_single_in_year (2015)", expected_artists_2015, actual_artists_2015)
        overall_status.append(status)

        # 5c. get_top_song_genres (n=4)
        actual_top_genres = get_top_song_genres(mydb, 4)
        expected_top_genres = [('Pop', 6), ('Electronic', 4), ('Rock', 4), ('Soul', 3)]
        status = print_comparison("5c. get_top_song_genres", expected_top_genres, actual_top_genres)
        overall_status.append(status)

        # 5d. get_album_and_single_artists
        actual_both_artists = get_album_and_single_artists(mydb)
        expected_both_artists = {'Adele'}
        status = print_comparison("5d. get_album_and_single_artists", expected_both_artists, actual_both_artists)
        overall_status.append(status)

        # 5e. get_most_rated_songs (n=2, year_range=(2014, 2017))
        # CORRECTED EXPECTED: 'Bad Blood' has 3 valid ratings based on the ratings list above.
        actual_most_rated = get_most_rated_songs(mydb, (2014, 2017), 2)
        expected_most_rated = [('Bad Blood', 'Taylor Swift', 3), ('Blank Space', 'Taylor Swift', 1)]
        status = print_comparison("5e. get_most_rated_songs (Release Date Filter)", expected_most_rated, actual_most_rated)
        overall_status.append(status)
        
        # 5f. get_most_engaged_users (n=3, year_range=(2024, 2024))
        actual_engaged_users = get_most_engaged_users(mydb, (2024, 2024), 3)
        expected_engaged_users = [('alice', 1), ('bob', 1), ('charlie', 1)]
        status = print_comparison("5f. get_most_engaged_users (Rating Date Filter)", expected_engaged_users, actual_engaged_users)
        overall_status.append(status)

        mydb.close()
        
        passed_count = sum(overall_status)
        print(f"\n--- ALL TESTS EXECUTED ---")
        print(f"Total Tests Passed: {passed_count}/{len(overall_status)}")

    except Error as e:
        print(f"\n[DATABASE ERROR] Connection or Query failed: {e}")


if __name__ == "__main__":
    main()