# src/story_generator.py

import os
import json
import re
from .llm_config import get_llm_completion, get_ollama_json_completion
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
                "num_frames": 30  # Default number of frames per scene
            }
        ] * 4 
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

def generate_story(output_dir, client, model, provider, topic=None):
    template = create_story_template()
    if topic:
        template['topic'] = topic  # Set the topic if provided
    prompt = create_story_prompt(template)
    
    try:
        messages = [{"role": "user", "content": prompt}]
        if provider == 'ollama':
            story_data = get_ollama_json_completion(client, messages)
            #print("Raw Ollama response:")
            #print(json.dumps(story_data, indent=2))
        else:
            content = get_llm_completion(client, provider, messages)
            # Extract JSON content for non-Ollama providers
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
                story_data = json.loads(json_content)
            else:
                error_exit(f"Failed to extract JSON content from non-Ollama provider.")
                return None

    except Exception as e:
        error_exit(f"Failed to generate story: {str(e)}")
        return None

    # Save raw API output
    raw_output_file = os.path.join(output_dir, 'raw_story_output.json')
    try:
        with open(raw_output_file, 'w') as f:
            json.dump(story_data, f, indent=2)
        #log_progress(f"Raw API output saved to {raw_output_file}")
    except IOError as e:
        error_exit(f"Failed to save raw output: {str(e)}")

    # Process story data
    try:
        # Remove any empty scenes and ensure num_frames is within bounds
        story_data['scenes'] = [
            {**scene, 'num_frames': max(5, min(15, scene.get('num_frames', 10)))}
            for scene in story_data['scenes']
            if scene['name']
        ]
        return story_data
    except KeyError as e:
        error_exit(f"Invalid story structure. Missing key: {str(e)}. Check {raw_output_file} for raw output.")
        return None

def save_story(story_data, output_dir):
    story_file = os.path.join(output_dir, 'story.json')
    try:
        with open(story_file, 'w') as f:
            json.dump(story_data, f, indent=2)
        #log_progress(f"Processed story saved to {story_file}")
    except IOError as e:
        error_exit(f"Failed to save story: {str(e)}")

if __name__ == "__main__":
    from .llm_config import create_llm_client
    
    output_dir = "data/debug_output"
    os.makedirs(output_dir, exist_ok=True)
    
    provider = 'ollama'
    client = create_llm_client(provider)
    model = "llama2"
    
    story = generate_story(output_dir, client, model, provider, topic="Space Exploration")
    if story:
        save_story(story, output_dir)
        print(json.dumps(story, indent=2))
