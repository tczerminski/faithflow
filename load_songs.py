import json
import os

directory = 'songs'

def load_songs():
    songs = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as f:
                try:
                    song = json.load(f)
                    songs[song['id']] = song
                except json.JSONDecodeError as e:
                    print(f"Error decoding {filename}: {e}")
    return songs