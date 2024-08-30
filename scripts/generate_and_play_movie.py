# scripts/generate_and_play_movie.py

import os
import sys
import time
import json
import argparse

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.story_generator import generate_story, save_story
from src.frame_generator import generate_frames
from src.movie_player import play_movie
from src.utils import create_movie_directory, log_progress, error_exit

def main(use_openai=False, resume=False, topic=None):
    # Set up directories
    data_dir = os.path.join(project_root, 'data', 'movies')
    debug_dir = os.path.join(data_dir, 'debug_output')
    os.makedirs(debug_dir, exist_ok=True)
    
    model = "gpt-4o-mini" if use_openai else "gemma2"
    base_url = None if use_openai else "http://localhost:11434/v1"
    
    if resume:
        # Find the most recent movie directory
        movie_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d)) and d != 'debug_output']
        if not movie_dirs:
            error_exit("No existing movie found to resume.")
        latest_movie_dir = max(movie_dirs, key=lambda d: os.path.getmtime(os.path.join(data_dir, d)))
        movie_dir = os.path.join(data_dir, latest_movie_dir)
        
        # Load existing story
        story_file = os.path.join(movie_dir, 'story.json')
        if not os.path.exists(story_file):
            error_exit(f"Story file not found in {movie_dir}")
        with open(story_file, 'r') as f:
            story_data = json.load(f)
        log_progress(f"Resuming movie generation for: {story_data['title']}")
    else:
        log_progress("Generating new story...")
        story_data = generate_story(debug_dir, use_local_llm=not use_openai, model=model, base_url=base_url, topic=topic)
        if not story_data:
            return  # Error message already printed in generate_story
        
        movie_dir = create_movie_directory(data_dir, story_data['title'])
        save_story(story_data, movie_dir)
    
    log_progress("Generating frames...")
    generate_frames(story_data, movie_dir, use_local_llm=not use_openai, model=model, base_url=base_url, resume=resume)
    log_progress("All frames generated.")
    
    log_progress("Starting movie playback...")
    time.sleep(2)  # Give a moment for the user to prepare
    
    try:
        play_movie(movie_dir)
    except KeyboardInterrupt:
        log_progress("Movie playback interrupted.")
    
    log_progress("Movie generation and playback complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and play ASCII movie")
    parser.add_argument("--openai", action="store_true", help="Use OpenAI instead of local Ollama")
    parser.add_argument("--resume", action="store_true", help="Resume the most recent movie generation")
    parser.add_argument("--topic", type=str, help="Specify a topic for the story generation")
    args = parser.parse_args()

    try:
        main(use_openai=args.openai, resume=args.resume, topic=args.topic)
    except Exception as e:
        error_exit(f"An unexpected error occurred: {str(e)}")

