# src/llm_config.py
import os
from openai import OpenAI

def create_llm_client(use_local_llm=False, base_url=None, api_key=None):
    """
    Create and return an OpenAI client based on the given configuration.
    
    :param use_local_llm: Boolean, if True use local LLM (Ollama)
    :param base_url: String, base URL for the API (used for local LLM)
    :param api_key: String, API key for OpenAI (not used for local LLM)
    :return: OpenAI client
    """
    if use_local_llm:
        return OpenAI(
            base_url=base_url or 'http://localhost:11434/v1',
            api_key='ollama'  # required, but unused for local LLM
        )
    else:
        return OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

def get_llm_completion(client, model, messages, temperature=0.7):
    """
    Get a completion from the LLM using the provided client.
    
    :param client: OpenAI client
    :param model: String, name of the model to use
    :param messages: List of message dictionaries
    :param temperature: Float, temperature for generation
    :return: Generated content
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

