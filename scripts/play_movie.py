# scripts/play_movie.py

import os
import sys
import argparse
import json
import textwrap
import time
import re

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils import log_progress, error_exit

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_info(text, width=68):
    print("="*width)
    print(textwrap.fill(text, width).center(width))
    print("="*width)

def wrap_text(text, width=68):
    return '\n'.join(textwrap.wrap(text, width))

def read_frame(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def play_movie(movie_dir, frame_delay=0.6):
    # Load movie information
    with open(os.path.join(movie_dir, 'story.json'), 'r') as f:
        story_data = json.load(f)
    
    clear_screen()
    display_info(f"Movie: {story_data['title']}")
    print(f"\n{wrap_text('Synopsis: ' + story_data['synopsis'])}\n")
    input("Press Enter to start the movie...")

    scene_dirs = sorted([d for d in os.listdir(movie_dir) if os.path.isdir(os.path.join(movie_dir, d))])
    
    try:
        for scene_index, scene_dir in enumerate(scene_dirs):
            # Use the index of the scene directory instead of trying to parse a number from the directory name
            scene_data = story_data['scenes'][scene_index]
            
            clear_screen()
            display_info(f"Scene {scene_index + 1}: {scene_data['name']}")
            print(f"\n{wrap_text(scene_data['description'])}")
            print(f"\n{wrap_text(scene_data['caption'])}\n")
            input("Press Enter to start the scene...")
            
            scene_path = os.path.join(movie_dir, scene_dir)
            frame_files = sorted([f for f in os.listdir(scene_path) if f.endswith('.txt')])
            
            for frame_file in frame_files:
                clear_screen()
                frame_content = read_frame(os.path.join(scene_path, frame_file))
                print(frame_content)
                time.sleep(frame_delay)
        
        clear_screen()
        display_info("End of Movie")
        print(f"\n{wrap_text('Thank you for watching ' + story_data['title'] + '!')}")
        
    except KeyboardInterrupt:
        print("\nPlayback interrupted. Exiting...")
    except IndexError:
        error_exit("Error: Mismatch between number of scene directories and scenes in story data.")

def list_movies(data_dir):
    movies = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d)) and d != 'debug_output']
    return sorted(movies)

def select_movie(movies):
    print("\nAvailable movies:")
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie}")
    
    while True:
        try:
            choice = input("\nEnter the number of the movie you want to play (or 'q' to quit): ")
            if choice.lower() == 'q':
                return None
            index = int(choice) - 1
            if 0 <= index < len(movies):
                return movies[index]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")

def main(frame_delay=0.6):
    data_dir = os.path.join(project_root, 'data', 'movies')
    movies = list_movies(data_dir)
    
    if not movies:
        error_exit("No movies found in the data directory.")
    
    movie_name = select_movie(movies)
    if movie_name is None:
        log_progress("Movie selection cancelled.")
        return
    
    movie_dir = os.path.join(data_dir, movie_name)
    log_progress(f"Playing movie: {movie_name}")
    
    try:
        play_movie(movie_dir, frame_delay)
    except KeyboardInterrupt:
        log_progress("Movie playback interrupted.")
    
    log_progress("Movie playback complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play an ASCII movie")
    parser.add_argument("--delay", type=float, default=0.6, help="Delay between frames in seconds (default: 0.6)")
    args = parser.parse_args()

    try:
        main(args.delay)
    except Exception as e:
        error_exit(f"An unexpected error occurred: {str(e)}")

