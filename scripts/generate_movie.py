import os
import sys
import json
import argparse

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.story_generator import generate_story, save_story
from src.frame_generator import generate_frames
from src.utils import create_movie_directory, log_progress, error_exit
from src.llm_config import create_llm_client

def main(provider='ollama', resume=False, topic=None):
    # Set up directories
    data_dir = os.path.join(project_root, 'data', 'movies')
    debug_dir = os.path.join(data_dir, 'debug_output')
    os.makedirs(debug_dir, exist_ok=True)

    if provider == 'openai':
        model = "gpt-4"
    elif provider == 'anthropic':
        model = "claude-3-sonnet-20240229"
    else:  # ollama
        model = "qwen2:7b"
    
    base_url = "http://localhost:11434/v1" if provider == 'ollama' else None
    client = create_llm_client(provider=provider, use_local_llm=(provider == 'ollama'), base_url=base_url)

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
        story_data = generate_story(debug_dir, client=client, model=model, topic=topic)
        if not story_data:
            return  # Error message already printed in generate_story
        
        movie_dir = create_movie_directory(data_dir, story_data['title'])
        save_story(story_data, movie_dir)
    
    log_progress("Generating frames...")
    generate_frames(story_data, movie_dir, client=client, model=model, resume=resume)
    log_progress("All frames generated.")
    
    log_progress(f"Movie generation complete. The movie is saved in: {movie_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ASCII movie")
    parser.add_argument("--provider", choices=['ollama', 'openai', 'anthropic'], default='ollama', 
                        help="Choose the LLM provider (default: ollama)")
    parser.add_argument("--resume", action="store_true", help="Resume the most recent movie generation")
    parser.add_argument("--topic", type=str, help="Specify a topic for the story generation")
    args = parser.parse_args()

    try:
        main(provider=args.provider, resume=args.resume, topic=args.topic)
    except Exception as e:
        error_exit(f"An unexpected error occurred: {str(e)}")
