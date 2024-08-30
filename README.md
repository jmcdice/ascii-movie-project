# ASCII Movie Generator and Player

## Overview
The ASCII Movie Generator and Player is a Python-based project that creates and displays animated ASCII art movies. It uses AI to generate a story, converts the story into ASCII art frames, and then plays these frames in a command-line interface, creating a unique animated movie experience.

## Features
- AI-powered story and scene generation using OpenAI or local LLM (Ollama)
- Conversion of story scenes into ASCII art frames
- Command-line ASCII art movie player with scene information display
- Customizable frame rate for playback
- Movie selection interface for playing existing movies

## Prerequisites
- Python 3.7+
- OpenAI API key (for story generation using OpenAI)
- Ollama (for local LLM support)

## Installation

1. Clone the repository:
```
   git clone https://github.com/jmcdice/ascii-movie-project.git
   cd ascii-movie-project
```

2. Install the required dependencies:
```
   python -m venv .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
```

3. Set up your OpenAI API key as an environment variable (if using OpenAI):
```
   export OPENAI_API_KEY='your-api-key-here'
```

4. Install Ollama (if using local LLM):
   - Follow the instructions at [Ollama's official website](https://ollama.ai/download)

## Usage

### Generating and Playing a Movie

Run the main script to generate and play a new ASCII movie:

```
   python scripts/generate_and_play_movie.py
```

By default, this uses Ollama (local LLM). To use OpenAI instead:

```
   python scripts/generate_and_play_movie.py --openai
```

You can also provide a topic to start with:

```
   python scripts/generate_and_play_movie.py --topic "Time Travel" --openai
```

This script will:
1. Generate a new story using AI
2. Create ASCII art frames for each scene
3. Play the movie in your terminal

### Playing an Existing Movie

To play an existing ASCII movie:

```
   python scripts/play_movie.py
```

This will show a list of available movies and prompt you to choose one. You can also specify a custom frame delay:

```
   python scripts/play_movie.py --delay 0.2
```

### Resuming Movie Generation

To resume the most recent movie generation:

```
   python scripts/generate_and_play_movie.py --resume
```

## Project Structure

```
   ascii_movie_project/
   ├── README.md
   ├── requirements.txt
   ├── data/
   │   └── movies/
   │       ├── debug_output/
   │       ├── movie_name_1/
   │       └── movie_name_2/
   ├── scripts/
   │   ├── generate_and_play_movie.py
   │   └── play_movie.py
   └── src/
       ├── __init__.py
       ├── frame_generator.py
       ├── llm_config.py
       ├── movie_player.py
       ├── story_generator.py
       └── utils.py
```

## Contributing

Contributions to the ASCII Movie Generator and Player are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - go nuts. 

