# src/utils.py
import os
import re
import json

def sanitize_dirname(title):
    # Remove any character that isn't alphanumeric, space, or hyphen
    sanitized = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Remove leading/trailing underscores and convert to lowercase
    return sanitized.strip('_').lower()

def create_movie_directory(base_dir, movie_title):
    sanitized_title = sanitize_dirname(movie_title)
    movie_dir = os.path.join(base_dir, sanitized_title)
    os.makedirs(movie_dir, exist_ok=True)
    return movie_dir

def load_story(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_story(story_data, file_path):
    with open(file_path, 'w') as f:
        json.dump(story_data, f, indent=2)

def get_frame_files(scene_dir):
    return sorted([f for f in os.listdir(scene_dir) if f.endswith('.txt')])

def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def log_progress(message):
    print(f"[PROGRESS] {message}")

def error_exit(message):
    print(f"[ERROR] {message}")
    exit(1)
