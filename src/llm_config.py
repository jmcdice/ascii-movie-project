# src/llm_config.py

import os
from openai import OpenAI
from anthropic import Anthropic

def create_llm_client(provider='openai', use_local_llm=False, base_url=None, api_key=None):
    """
    Create and return an LLM client based on the given configuration.
    
    :param provider: String, 'openai', 'anthropic', or 'ollama'
    :param use_local_llm: Boolean, if True use local LLM (Ollama)
    :param base_url: String, base URL for the API (used for local LLM)
    :param api_key: String, API key for the chosen provider
    :return: LLM client
    """
    if provider == 'openai':
        if use_local_llm:
            return OpenAI(
                base_url=base_url or 'http://localhost:11434/v1',
                api_key='ollama'  # required, but unused for local LLM
            )
        else:
            return OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    elif provider == 'anthropic':
        return Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    elif provider == 'ollama':
        return OpenAI(
            base_url=base_url or 'http://localhost:11434/v1',
            api_key='ollama'  # required, but unused for local LLM
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def get_llm_completion(client, model, messages, temperature=0.7):
    """
    Get a completion from the LLM using the provided client.
    
    :param client: LLM client (OpenAI or Anthropic)
    :param model: String, name of the model to use
    :param messages: List of message dictionaries
    :param temperature: Float, temperature for generation
    :return: Generated content
    """
    if isinstance(client, OpenAI):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    elif isinstance(client, Anthropic):
        # Convert messages to Anthropic format
        prompt = ""
        for message in messages:
            role = message['role']
            content = message['content']
            if role == 'system':
                prompt += f"Human: {content}\n\nAssistant: Understood. How can I help you?\n\n"
            elif role == 'user':
                prompt += f"Human: {content}\n\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n\n"
        prompt += "Assistant: "

        response = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    else:
        raise ValueError(f"Unsupported client type: {type(client)}")
