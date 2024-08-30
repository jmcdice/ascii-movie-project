# src/story_generator.py

import os
import json
import re
from .llm_config import create_llm_client, get_llm_completion
from .utils import log_progress, error_exit

def create_story_template():
    return {
        "title": "",
        "topic": "",  # Optional topic field
        "synopsis": "",
        "scenes": [
            {
                "name": "",
                "description": "",
                "caption": "",
                "num_frames": 10  # Default number of frames per scene
            }
        ] * 8  # Template for up to 8 scenes
    }

def create_story_prompt(template):
    prompt = f"""Create a short movie script by filling out this JSON template:
{json.dumps(template, indent=2)}
Guidelines:

IMPORTANT: Only return valid JSON, nothing else.

1. Provide a catchy title."""

    if template['topic']:
        prompt += f"\n2. Choose a topic and incorporate it into the story. The topic is: {template['topic']}"

    prompt += """
2. Write a brief synopsis in 2-3 sentences.
3. Create 5-8 scenes. For each scene:
   - Give it a name
   - Write a brief description in 1-2 sentences
   - Provide a caption for the ASCII art frame
   - Specify the number of frames (between 5 and 15)
Fill out the JSON template with your creative story. 
Ensure all fields are filled and the JSON structure is maintained.
"""

    return prompt

def generate_story(output_dir, use_local_llm=False, model="gpt-4o-mini", base_url=None, topic=None):
    client = create_llm_client(use_local_llm, base_url)
    template = create_story_template()
    if topic:
        template['topic'] = topic  # Set the topic if provided
    prompt = create_story_prompt(template)

    try:
        messages = [{"role": "user", "content": prompt}]
        content = get_llm_completion(client, model, messages)
    except Exception as e:
        error_exit(f"Failed to generate story: {str(e)}")

    # Save raw API output
    raw_output_file = os.path.join(output_dir, 'raw_story_output.txt')
    try:
        with open(raw_output_file, 'w') as f:
            f.write(content)
        log_progress(f"Raw API output saved to {raw_output_file}")
    except IOError as e:
        error_exit(f"Failed to save raw output: {str(e)}")

    # Extract JSON content
    json_match = re.search(r'(\{.*\})', content, re.DOTALL)
    if json_match:
        json_content = json_match.group(1)
    else:
        error_exit(f"Failed to extract JSON content. Check {raw_output_file} for raw output.")
        return None

    try:
        story_data = json.loads(json_content)
        # Remove any empty scenes and ensure num_frames is within bounds
        story_data['scenes'] = [
            {**scene, 'num_frames': max(5, min(15, scene.get('num_frames', 10)))}
            for scene in story_data['scenes']
            if scene['name']
        ]
        return story_data
    except json.JSONDecodeError as e:
        error_exit(f"Failed to parse story JSON. Error: {str(e)}. Check {raw_output_file} for raw output.")
        return None

def save_story(story_data, output_dir):
    story_file = os.path.join(output_dir, 'story.json')
    try:
        with open(story_file, 'w') as f:
            json.dump(story_data, f, indent=2)
        log_progress(f"Processed story saved to {story_file}")
    except IOError as e:
        error_exit(f"Failed to save story: {str(e)}")

if __name__ == "__main__":
    output_dir = "data/debug_output"
    os.makedirs(output_dir, exist_ok=True)
    story = generate_story(output_dir, topic="Space Exploration")
    if story:
        save_story(story, output_dir)
        print(json.dumps(story, indent=2))


