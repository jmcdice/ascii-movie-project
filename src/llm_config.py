# src/llm_config.py

import os
import argparse
import json
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_llm_client(provider):
    """
    Create and return an LLM client based on the given provider.
    
    :param provider: String, 'openai', 'anthropic', or 'ollama'
    :return: LLM client
    """
    if provider == 'openai':
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    elif provider == 'anthropic':
        return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif provider == 'ollama':
        return OpenAI(
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1'),
            api_key='ollama'  # required, but unused for Ollama
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def get_llm_completion(client, provider, messages, temperature=0.7):
    """
    Get a completion from the LLM using the provided client.
    
    :param client: LLM client (OpenAI, Anthropic, or Ollama)
    :param provider: String, 'openai', 'anthropic', or 'ollama'
    :param messages: List of message dictionaries
    :param temperature: Float, temperature for generation
    :return: Generated content
    """
    if provider == 'openai':
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    elif provider == 'anthropic':
        model = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        prompt = "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
        prompt += "\n\nAssistant: "
        response = client.messages.create(
            model=model,
            max_tokens=int(os.getenv('ANTHROPIC_MAX_TOKENS', '1000')),
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    elif provider == 'ollama':
        model = os.getenv('OLLAMA_MODEL', 'llama2')
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def get_ollama_json_completion(client, messages, temperature=0.7):
    """
    Get a JSON completion from Ollama using the provided client.
    
    :param client: OpenAI client configured for Ollama
    :param messages: List of message dictionaries
    :param temperature: Float, temperature for generation
    :return: Generated JSON content or string
    """
    model = os.getenv('OLLAMA_MODEL', 'llama2')
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("Warning: Ollama response is not valid JSON. Returning raw string.")
        print(content)
        return content

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a movie script using an LLM.")
    parser.add_argument("--provider", choices=['openai', 'anthropic', 'ollama'], required=True, help="LLM provider to use")
    parser.add_argument("--topic", required=True, help="Topic for the movie script")
    return parser.parse_args()

def generate_movie_script(provider, topic):
    client = create_llm_client(provider)
    messages = [
        {"role": "system", "content": "You are a creative screenwriter."},
        {"role": "user", "content": f"Write a short movie script about {topic}."}
    ]
    script = get_llm_completion(client, provider, messages)
    return script

if __name__ == "__main__":
    args = parse_arguments()
    script = generate_movie_script(args.provider, args.topic)
    print(script)

