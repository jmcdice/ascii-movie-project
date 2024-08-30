# src/movie_player.py
import os
import time
import sys
import json

def clear_screen():
    # Clear the console screen
    os.system('cls' if os.name == 'nt' else 'clear')

def read_frame(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def display_info(text, width=80):
    print("="*width)
    print(text.center(width))
    print("="*width)

def play_movie(movie_dir, frame_delay=0.1):
    # Load movie information
    with open(os.path.join(movie_dir, 'story.json'), 'r') as f:
        story_data = json.load(f)
    
    clear_screen()
    display_info(f"Movie: {story_data['title']}")
    print(f"\nSynopsis: {story_data['synopsis']}\n")
    input("Press Enter to start the movie...")

    scene_dirs = sorted([d for d in os.listdir(movie_dir) if os.path.isdir(os.path.join(movie_dir, d))])
    
    try:
        for scene_dir in scene_dirs:
            scene_number = int(scene_dir.split('_')[1])
            scene_data = story_data['scenes'][scene_number - 1]
            
            clear_screen()
            display_info(f"Scene {scene_number}: {scene_data['name']}")
            print(f"\nDescription: {scene_data['description']}")
            print(f"Caption: {scene_data['caption']}\n")
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
        print(f"\nThank you for watching {story_data['title']}!")
        
    except KeyboardInterrupt:
        print("\nPlayback interrupted. Exiting...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python movie_player.py <path_to_movie_directory> [frame_delay]")
        sys.exit(1)

    movie_dir = sys.argv[1]
    frame_delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1

    if not os.path.isdir(movie_dir):
        print(f"Error: {movie_dir} is not a valid directory.")
        sys.exit(1)

    play_movie(movie_dir, frame_delay)

