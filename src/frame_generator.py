# src/frame_generator.py

import os
import json
import time
from .llm_config import create_llm_client, get_llm_completion
from .utils import log_progress, error_exit

def create_frame_prompt(scene, frame_number, total_frames, ascii_art_height, frame_width, previous_frame=None):
    if frame_number == 1:
        return f"""Generate the first frame of an ASCII art animation for the following scene:

Scene: {scene['name']}
Description: {scene['description']}
Frame 1 of {total_frames}
The ASCII art should be exactly {ascii_art_height} lines tall and {frame_width} characters wide.
Create a detailed initial scene that can be animated in subsequent frames.
Do not include any caption or text at the bottom of the ASCII art. Only return the frame, nothing else."""
    else:
        return f"""Generate the next frame of an ASCII art animation based on the following:

Previous frame:
{previous_frame}

Scene: {scene['name']}
Description: {scene['description']}
Frame {frame_number} of {total_frames}
The ASCII art should be exactly {ascii_art_height} lines tall and {frame_width} characters wide.
Make only subtle changes from the previous frame to create a smooth animation effect.
Include the number {frame_number} at the top of the ASCII art on a line by itself.
Do not include any caption or text at the bottom of the ASCII art. Only return the frame, nothing else."""

def generate_and_save_frame(client, model, scene, frame_number, total_frames, frame_width, frame_height, scene_number, caption, previous_frame):
    log_progress(f"Generating frame {frame_number} of {total_frames} for Scene {scene_number}: {scene['name']}")

    caption_height = 2  # Reserve 2 lines for the caption
    ascii_art_height = frame_height - caption_height

    prompt = create_frame_prompt(scene, frame_number, total_frames, ascii_art_height, frame_width, previous_frame)
    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = get_llm_completion(client, model, messages)
    except Exception as e:
        error_exit(f"Error generating frame {frame_number} for scene {scene_number}: {str(e)}")

    # Remove triple backticks if present at the start of any line
    response_lines = response.splitlines()
    cleaned_response = "\n".join(line for line in response_lines if not line.strip().startswith('```'))

    # Add caption at the bottom
    caption_line = f"Scene {scene_number}: {caption}"
    separator_line = "-" * frame_width
    full_frame = f"{cleaned_response}\n{separator_line}\n{caption_line.center(frame_width)}"

    filename = f"scene_{scene_number:02d}_frame_{frame_number:03d}.txt"
    file_path = os.path.join(scene['output_dir'], filename)

    try:
        with open(file_path, "w") as f:
            f.write(full_frame)
        log_progress(f"Saved frame {frame_number} to {filename}")
    except IOError as e:
        error_exit(f"Error saving frame {frame_number} for scene {scene_number}: {str(e)}")

    return full_frame


def generate_frames(story_data, output_dir, use_local_llm=False, model="gpt-4o-mini", base_url=None, frame_width=68, frame_height=14, resume=False):
    client = create_llm_client(use_local_llm, base_url)

    for scene_number, scene in enumerate(story_data['scenes'], 1):
        scene['output_dir'] = os.path.join(output_dir, f"scene_{scene_number:02d}")
        os.makedirs(scene['output_dir'], exist_ok=True)

        log_progress(f"Starting Scene {scene_number}: {scene['name']}")
        log_progress(f"Description: {scene['description']}")
        log_progress(f"Number of frames: {scene['num_frames']}")
        log_progress(f"Caption: {scene['caption']}")

        existing_frames = os.listdir(scene['output_dir']) if resume else []
        start_frame = len(existing_frames) + 1 if resume else 1

        previous_frame = None
        if start_frame > 1:
            try:
                with open(os.path.join(scene['output_dir'], f"scene_{scene_number:02d}_frame_{start_frame-1:03d}.txt"), 'r') as f:
                    previous_frame = '\n'.join(f.read().split('\n')[:-3])  # Exclude the separator and caption
            except IOError as e:
                error_exit(f"Error reading previous frame for scene {scene_number}: {str(e)}")

        for frame_number in range(start_frame, scene['num_frames'] + 1):
            frame = generate_and_save_frame(
                client, model, scene, frame_number, 
                scene['num_frames'], frame_width, frame_height, 
                scene_number, scene['caption'], previous_frame
            )
            previous_frame = '\n'.join(frame.split('\n')[:-3])  # Exclude the separator and caption when passing to the next iteration

            log_progress(f"Preview of frame {frame_number}:")
            log_progress('\n'.join(frame.split('\n')[:6]) + "\n...")  # Print first 6 lines as a preview
            time.sleep(1)  # Add a small delay to avoid overwhelming the API

        log_progress(f"Completed Scene {scene_number}: {scene['name']}")

    log_progress(f"All frames generated and saved in: {output_dir}")
    return output_dir

if __name__ == "__main__":
    # For testing purposes
    try:
        with open('data/movies/sample_story.json', 'r') as f:
            story_data = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        error_exit(f"Error loading sample story: {str(e)}")

    output_dir = "data/movies/test_movie"
    generate_frames(story_data, output_dir)
