# music_db.py
from typing import Tuple, List, Set
import mysql.connector
from mysql.connector import IntegrityError

# ---------------------------
# Helpers
# ---------------------------

def _get_or_create_artist(cursor, artist_name: str) -> int:
    """Gets artist_id if exists, otherwise inserts and returns new ID."""
    cursor.execute("SELECT artist_id FROM artists WHERE name = %s", (artist_name,))
    r = cursor.fetchone()
    if r:
        return r[0]
    cursor.execute("INSERT INTO artists (name) VALUES (%s)", (artist_name,))
    return cursor.lastrowid

def _get_or_create_genre(cursor, genre_name: str) -> int:
    """Gets genre_id if exists, otherwise inserts and returns new ID."""
    cursor.execute("SELECT genre_id FROM genres WHERE name = %s", (genre_name,))
    r = cursor.fetchone()
    if r:
        return r[0]
    cursor.execute("INSERT INTO genres (name) VALUES (%s)", (genre_name,))
    return cursor.lastrowid

# ---------------------------
# Core Functions: Database Population (Loading)
# ---------------------------

def clear_database(mydb):
    """
    Empties all tables in the database.
    (CRITICAL for Autolab submission)
    """
    cur = mydb.cursor()
    
    # Disable FK checks for safe and fast TRUNCATE
    cur.execute("SET FOREIGN_KEY_CHECKS = 0;") 
    
    # Order doesn't strictly matter with TRUNCATE if FK checks are off
    tables = ["ratings", "song_genres", "songs", "albums", "users", "artists", "genres"]
    for t in tables:
        # TRUNCATE is faster and more efficient than DELETE FROM without a WHERE clause
        cur.execute(f"TRUNCATE TABLE {t};") 
        
    # Re-enable FK checks
    cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    mydb.commit()
    cur.close()

def load_users(mydb, users: List[str]) -> Set[str]:
    """Adds users, rejecting duplicates."""
    rejects = set()
    cur = mydb.cursor()
    try:
        for u in users:
            try:
                cur.execute("INSERT INTO users (username) VALUES (%s)", (u,))
            except IntegrityError:
                rejects.add(u)
        mydb.commit()
    except Exception as e:
        mydb.rollback()
        raise e
    finally:
        cur.close()
    return rejects

def load_single_songs(mydb, single_songs: List[Tuple[str, Tuple[str, ...], str, str]]) -> Set[Tuple[str, str]]:
    """Adds single songs, enforcing required constraints."""
    rejects = set()
    cur = mydb.cursor()
    try:
        # Input format: (title, genres: Tuple[str...], artist_name, release_date)
        for title, genres, artist_name, release_date in single_songs:
            
            # Constraint: Every song must be in at least one genre.
            if not genres:
                rejects.add((title, artist_name))
                continue

            artist_id = _get_or_create_artist(cur, artist_name)

            # Constraint: An artist may not record the same song (title) more than once.
            cur.execute("SELECT song_id FROM songs WHERE title = %s AND artist_id = %s", (title, artist_id))
            if cur.fetchone():
                rejects.add((title, artist_name))
                continue

            # Insert single song (album_id=NULL, is_single=TRUE)
            cur.execute(
                "INSERT INTO songs (title, artist_id, album_id, release_date, is_single) VALUES (%s,%s,NULL,%s,TRUE)",
                (title, artist_id, release_date)
            )
            song_id = cur.lastrowid

            # Link genres
            for g in genres:
                genre_id = _get_or_create_genre(cur, g)
                cur.execute("INSERT INTO song_genres (song_id, genre_id) VALUES (%s,%s)", (song_id, genre_id))

        mydb.commit()
    except Exception as e:
        mydb.rollback()
        raise e
    finally:
        cur.close()
    return rejects

def load_albums(mydb, albums: List[Tuple[str,str,str,str,List[str]]]) -> Set[Tuple[str,str]]:
    """Adds albums and their songs, enforcing album/song constraints."""
    rejects = set()
    cur = mydb.cursor()
    try:
        # Input format: (album_title, genre_name, artist_name, release_date, song_titles: List[str])
        for album_title, genre_name, artist_name, release_date, song_titles in albums:
            
            artist_id = _get_or_create_artist(cur, artist_name)

            # Constraint: The combination of album name and artist name is unique.
            cur.execute("SELECT album_id FROM albums WHERE title = %s AND artist_id = %s", (album_title, artist_id))
            if cur.fetchone():
                rejects.add((album_title, artist_name))
                continue

            # Insert/Get Album Genre
            genre_id = _get_or_create_genre(cur, genre_name)
            
            # Insert Album
            cur.execute(
                "INSERT INTO albums (title, artist_id, release_date, genre_id) VALUES (%s,%s,%s,%s)",
                (album_title, artist_id, release_date, genre_id)
            )
            album_id = cur.lastrowid

            # Insert Album Songs and Link Genre
            for s_title in song_titles:
                
                # Constraint: An artist may not record the same song (title) more than once.
                cur.execute("SELECT song_id FROM songs WHERE title = %s AND artist_id = %s", (s_title, artist_id))
                if cur.fetchone():
                    # Skip duplicate song, but continue with the rest of the album
                    continue
                    
                # Insert Song (album_id=album_id, is_single=FALSE)
                cur.execute(
                    "INSERT INTO songs (title, artist_id, album_id, release_date, is_single) VALUES (%s,%s,%s,%s,FALSE)",
                    (s_title, artist_id, album_id, release_date)
                )
                song_id = cur.lastrowid
                
                # Link Song to Album Genre (all songs in the album are in the album's genre)
                cur.execute(
                    "INSERT INTO song_genres (song_id, genre_id) VALUES (%s,%s)", 
                    (song_id, genre_id)
                )

        mydb.commit()
    except Exception as e:
        mydb.rollback()
        raise e
    finally:
        cur.close()
    return rejects

def load_song_ratings(mydb, song_ratings: List[Tuple[str,Tuple[str,str],int,str]]) -> Set[Tuple[str,str,str]]:
    """Adds ratings, rejecting invalid data or duplicates."""
    rejects = set()
    cur = mydb.cursor()
    try:
        # Input format: (username, (artist_name, song_title), rating, rating_date)
        for username, (artist_name, song_title), rating, rating_date in song_ratings:
            
            # Constraint: Rating is limited to 1,2,3,4, or 5 (numeric).
            if not (1 <= rating <= 5):
                rejects.add((username, artist_name, song_title))
                continue

            # Find user
            cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            r = cur.fetchone()
            if not r:
                rejects.add((username, artist_name, song_title))
                continue
            user_id = r[0]

            # Find song by artist+title (using case-insensitive comparison inherent to MySQL VARCHAR)
            cur.execute("""
                SELECT s.song_id
                FROM songs s
                JOIN artists a ON s.artist_id = a.artist_id
                WHERE a.name = %s AND s.title = %s
            """, (artist_name, song_title))
            s = cur.fetchone()
            if not s:
                rejects.add((username, artist_name, song_title))
                continue
            song_id = s[0]

            # Check existing rating (assuming PK is (user_id, song_id) meaning one rating per user per song)
            cur.execute("SELECT 1 FROM ratings WHERE user_id = %s AND song_id = %s", (user_id, song_id))
            if cur.fetchone():
                rejects.add((username, artist_name, song_title))
                continue

            # Insert rating
            cur.execute("INSERT INTO ratings (user_id, song_id, rating, rating_date) VALUES (%s,%s,%s,%s)",
                        (user_id, song_id, rating, rating_date))
            
        mydb.commit()
    except Exception as e:
        mydb.rollback()
        raise e
    finally:
        cur.close()
    return rejects

# ---------------------------
# Core Functions: Queries
# ---------------------------

def get_most_prolific_individual_artists(mydb, n: int, year_range: Tuple[int, int]) -> List[Tuple[str,int]]:
    """
    Finds the top n artists by song count in a year range (treating all as 'individual' since schema lacks distinction).
    """
    cur = mydb.cursor()
    y1, y2 = year_range
    cur.execute("""
        SELECT a.name, COUNT(s.song_id) AS num_songs
        FROM songs s
        JOIN artists a ON s.artist_id = a.artist_id
        WHERE YEAR(s.release_date) BETWEEN %s AND %s
        GROUP BY a.artist_id, a.name
        ORDER BY num_songs DESC, a.name ASC
        LIMIT %s
    """, (y1, y2, n))
    rows = cur.fetchall()
    cur.close()
    return rows

def get_artists_last_single_in_year(mydb, year: int) -> Set[str]:
    """
    Finds artists whose latest single release date falls exactly in the specified year.
    """
    cur = mydb.cursor()
    cur.execute("""
        SELECT a.name
        FROM artists a
        JOIN songs s ON a.artist_id = s.artist_id
        WHERE s.is_single = TRUE
        GROUP BY a.artist_id, a.name
        HAVING YEAR(MAX(s.release_date)) = %s
        ORDER BY a.name ASC
    """, (year,))
    result = {r[0] for r in cur.fetchall()}
    cur.close()
    return result

def get_top_song_genres(mydb, n: int) -> List[Tuple[str,int]]:
    """
    Returns the top n most frequently assigned genres to songs.
    """
    cur = mydb.cursor()
    cur.execute("""
        SELECT g.name, COUNT(sg.song_id) AS num_songs
        FROM genres g
        JOIN song_genres sg ON g.genre_id = sg.genre_id
        GROUP BY g.genre_id, g.name
        ORDER BY num_songs DESC, g.name ASC
        LIMIT %s
    """, (n,))
    rows = cur.fetchall()
    cur.close()
    return rows

def get_album_and_single_artists(mydb) -> Set[str]:
    """
    Returns the names of artists who have both released a song on an album AND a single.
    """
    cur = mydb.cursor()
    cur.execute("""
        SELECT a.name
        FROM artists a
        WHERE EXISTS (SELECT 1 FROM songs s WHERE s.artist_id = a.artist_id AND s.album_id IS NOT NULL)
          AND EXISTS (SELECT 1 FROM songs s WHERE s.artist_id = a.artist_id AND s.is_single = TRUE)
        ORDER BY a.name ASC
    """)
    result = {r[0] for r in cur.fetchall()}
    cur.close()
    return result

def get_most_rated_songs(mydb, year_range: Tuple[int,int], n: int) -> List[Tuple[str,str,int]]:
    """
    Returns the top n most rated songs whose RELEASE DATE falls within the year range.
    """
    cur = mydb.cursor()
    y1, y2 = year_range
    cur.execute("""
        SELECT s.title, a.name, COUNT(r.song_id) AS num_ratings
        FROM ratings r
        JOIN songs s ON r.song_id = s.song_id
        JOIN artists a ON s.artist_id = a.artist_id
        WHERE YEAR(s.release_date) BETWEEN %s AND %s -- Filtering by SONG RELEASE DATE (crucial fix)
        GROUP BY s.song_id, s.title, a.name
        ORDER BY num_ratings DESC, s.title ASC
        LIMIT %s
    """, (y1, y2, n))
    rows = cur.fetchall()
    cur.close()
    return rows

def get_most_engaged_users(mydb, year_range: Tuple[int,int], n: int) -> List[Tuple[str,int]]:
    """
    Returns the top n users who gave the most ratings whose RATING DATE falls within the year range.
    """
    cur = mydb.cursor()
    y1, y2 = year_range
    cur.execute("""
        SELECT u.username, COUNT(r.song_id) AS total_ratings
        FROM ratings r
        JOIN users u ON r.user_id = u.user_id
        WHERE YEAR(r.rating_date) BETWEEN %s AND %s -- Filtering by RATING DATE
        GROUP BY u.user_id, u.username
        ORDER BY total_ratings DESC, u.username ASC
        LIMIT %s
    """, (y1, y2, n))
    rows = cur.fetchall()
    cur.close()
    return rows

def main():
    pass

if __name__ == "__main__":
    main()