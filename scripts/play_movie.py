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
from src.llm_config import create_llm_client  # Import for potential future use

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

def play_movie(movie_dir, frame_delay=0.6, frame_height=15, frame_width=70):
    # Load movie information
    story_file = os.path.join(movie_dir, 'story.json')
    if not os.path.exists(story_file):
        error_exit(f"Story file not found: {story_file}")
    
    with open(story_file, 'r') as f:
        story_data = json.load(f)
    
    clear_screen()
    display_info(f"Movie: {story_data['title']}", width=frame_width)
    print(f"\n{wrap_text('Synopsis: ' + story_data['synopsis'], width=frame_width)}\n")
    input("Press Enter to start the movie...")

    scene_dirs = sorted([d for d in os.listdir(movie_dir) if os.path.isdir(os.path.join(movie_dir, d)) and d.startswith('scene_')])
    
    try:
        for scene_index, scene_dir in enumerate(scene_dirs):
            scene_number = int(re.search(r'scene_(\d+)', scene_dir).group(1))
            scene_data = story_data['scenes'][scene_index]
            
            clear_screen()
            
            # Prepare the content for the scene intro
            scene_title = f"Scene {scene_number}: {scene_data['name']}"
            description = wrap_text(scene_data['description'], width=frame_width)
            caption = wrap_text(scene_data['caption'], width=frame_width)
            
            # Create the scene intro frame
            adjusted_intro = ['+' + '-' * frame_width + '+']  # Top border
            adjusted_intro.append('|' + scene_title.center(frame_width)[:frame_width] + '|')  # Centered Scene title
            adjusted_intro.append('|' + '-' * frame_width + '|')  # Border line under the scene title
            
            # Calculate how many lines the description and caption take
            scene_intro_lines = description.split('\n') + [''] + caption.split('\n')
            total_lines = len(scene_intro_lines)
            
            # Truncate lines if they exceed the frame height
            if total_lines > (frame_height - 3):  # -3 for title, border, and padding
                scene_intro_lines = scene_intro_lines[:(frame_height - 3)]
                total_lines = len(scene_intro_lines)
            
            # Calculate padding to center the description/caption
            padding_top = (frame_height - total_lines - 3) // 2  # -3 for title, border, and bottom padding
            padding_bottom = frame_height - total_lines - padding_top - 3
            
            # Add top padding
            for _ in range(padding_top):
                adjusted_intro.append('|' + ' ' * frame_width + '|')
            
            # Add the description and caption
            for line in scene_intro_lines:
                adjusted_intro.append('|' + line.center(frame_width)[:frame_width] + '|')
            
            # Add bottom padding
            for _ in range(padding_bottom):
                adjusted_intro.append('|' + ' ' * frame_width + '|')
            
            adjusted_intro.append('+' + '-' * frame_width + '+')  # Bottom border
            
            print('\n'.join(adjusted_intro))
            input("Press Enter to start the scene...")

            scene_path = os.path.join(movie_dir, scene_dir)
            frame_files = sorted([f for f in os.listdir(scene_path) if f.endswith('.txt') and f.startswith(f'scene_{scene_number:02d}_frame_')])
            
            for frame_file in frame_files:
                clear_screen()
                frame_content = read_frame(os.path.join(scene_path, frame_file))
                
                # Ensure consistent frame size with border and dialogue at the bottom
                frame_lines = frame_content.split('\n')
                
                # Truncate lines if they exceed the frame height
                if len(frame_lines) > frame_height:
                    frame_lines = frame_lines[:frame_height]
                
                adjusted_frame = ['+' + '-' * frame_width + '+']  # Top border
                
                # Calculate padding above the dialogue
                padding_lines = frame_height - len(frame_lines)
                
                # Add padding lines
                for _ in range(padding_lines):
                    adjusted_frame.append('|' + ' ' * frame_width + '|')
                
                # Add the actual content
                for line in frame_lines:
                    adjusted_frame.append('|' + line.ljust(frame_width)[:frame_width] + '|')
                
                adjusted_frame.append('+' + '-' * frame_width + '+')  # Bottom border
                
                print('\n'.join(adjusted_frame))
                time.sleep(frame_delay)
        
        # Display goodbye frame
        clear_screen()
        goodbye_frame = [
            "+" + "-" * frame_width + "+",
            "|" + " " * frame_width + "|",
            "|" + "The End".center(frame_width) + "|",
            "|" + " " * frame_width + "|",
            "|" + f"Thank you for watching".center(frame_width) + "|",
            "|" + f"{story_data['title']}".center(frame_width) + "|",
            "|" + " " * frame_width + "|",
            "+" + "-" * frame_width + "+",
        ]
        
        # Pad the goodbye frame to match frame_height
        while len(goodbye_frame) < frame_height + 2:  # +2 for top and bottom border
            if len(goodbye_frame) == frame_height + 1:
                goodbye_frame.insert(-1, "|" + "-" * frame_width + "|")  # Adjust before the bottom border
            else:
                goodbye_frame.insert(-2, "|" + " " * frame_width + "|")
        
        print('\n'.join(goodbye_frame))
        
    except KeyboardInterrupt:
        print("\nPlayback interrupted. Exiting...")
    except IndexError:
        error_exit("Error: Mismatch between number of scene directories and scenes in story data.")

def list_movies(data_dir):
    movies = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d)) and d != 'debug_output']
    return sorted(movies, key=lambda x: os.path.getmtime(os.path.join(data_dir, x)), reverse=True)

def select_movie(movies):
    clear_screen()
    print("\nAvailable movies (most recent first):\n")
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
    except FileNotFoundError as e:
        error_exit(f"Error: {str(e)}")
    
    #log_progress("Movie playback complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play an ASCII movie")
    parser.add_argument("--delay", type=float, default=0.6, help="Delay between frames in seconds (default: 0.6)")
    args = parser.parse_args()

    try:
        main(args.delay)
    except Exception as e:
        error_exit(f"An unexpected error occurred: {str(e)}")
