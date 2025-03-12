import librosa
import numpy as np
from collections import Counter
from fingerprint import create_fingerprint

class MusicRecognizer:
    def __init__(self, db):
        self.db = db
    
    def add_song_to_database(self, audio_path, song_name, artist):
        print('Song Name', song_name, 'artist', artist, 'audio_PATH', audio_path)
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        
        song_id = self.db.add_song(song_name, artist, duration)
        
        fingerprints = create_fingerprint(audio_path)

        print(f"Storing {len(fingerprints)} fingerprints...")
        self.db.store_fingerprints(song_id, fingerprints)
        
        return song_id
    
    def recognize_song(self, sample_path):
        sample_fingerprints = create_fingerprint(sample_path)
        matches = self.db.find_matches(sample_fingerprints)
        
        # Find the most likely match
        best_match = None
        highest_count = 0
        
        for song_id, offsets in matches.items():
            # Count the most common offset (evidence of alignment)
            offset_counts = Counter(offsets)
            most_common_offset, count = offset_counts.most_common(1)[0]
            
            if count > highest_count:
                highest_count = count
                best_match = (song_id, count, most_common_offset)
        
        if best_match and best_match[1] >= 5:  # Minimum threshold
            song_id, confidence, offset = best_match
            song_info = self.db.get_song_info(song_id)
            return {
                'recognized': True,
                'song_name': song_info[0],
                'artist': song_info[1],
                'confidence': confidence,
                'time_offset': offset * 0.0232  # Convert to seconds (based on hop_length)
            }
        else:
            return {
                'recognized': False
            }