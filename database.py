import sqlite3
import hashlib
import os


class FingerprintDatabase:
    def __init__(self, db_path=None):

        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'database', 'fingerprints.db')
    
        db_directory = os.path.dirname(db_path)
        if db_directory and not os.path.exists(db_directory):
            os.makedirs(db_directory)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            name TEXT,
            artist TEXT,
            duration REAL
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS fingerprints (
            hash TEXT,
            song_id INTEGER,
            offset INTEGER,
            FOREIGN KEY (song_id) REFERENCES songs(id)
        )
        ''')
        self.conn.commit()
    
    def add_song(self, name, artist, duration):
        self.cursor.execute('INSERT INTO songs (name, artist, duration) VALUES (?, ?, ?)',
                            (name, artist, duration))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def store_fingerprints(self, song_id, fingerprints):
        # Prepare data for batch insertion
        data = []
        for freq_anchor, freq_target, time_delta, offset in fingerprints:
            # Create a hash from the fingerprint components
            hash_input = f"{freq_anchor}|{freq_target}|{time_delta}"
            hash_str = hashlib.md5(hash_input.encode()).hexdigest()
        
            data.append((hash_str, song_id, int(offset)))
        
        # Batch insert
        self.cursor.executemany('INSERT INTO fingerprints (hash, song_id, offset) VALUES (?, ?, ?)', data)
        self.conn.commit()
    
    def find_matches(self, fingerprints):
        matches = {}
        for freq_anchor, freq_target, time_delta, sample_offset in fingerprints:
            # Create the same hash as when storing
            hash_input = f"{freq_anchor}|{freq_target}|{time_delta}"
            hash_str = hashlib.md5(hash_input.encode()).hexdigest()
            
            # Look for matches
            self.cursor.execute('SELECT song_id, offset FROM fingerprints WHERE hash = ?', (hash_str,))
            results = self.cursor.fetchall()
            
            for song_id, db_offset in results:
                if song_id not in matches:
                    matches[song_id] = []
                
                # Convert both to integers before subtraction
                db_offset_int = int(db_offset)
                sample_offset_int = int(sample_offset)
                
                # Calculate the time offset difference
                matches[song_id].append(db_offset_int - sample_offset_int)
        
        return matches
    
    def get_song_info(self, song_id):
        self.cursor.execute('SELECT name, artist FROM songs WHERE id = ?', (song_id,))
        return self.cursor.fetchone()
    
    def get_all_songs(self):
        self.cursor.execute('SELECT id, name, artist, duration FROM songs')
        songs = []
        for row in self.cursor.fetchall():
            songs.append({
                'id': row[0],
                'name': row[1],
                'artist': row[2],
                'duration': row[3]
            })
        return songs
    
    def close(self):
        self.conn.close()