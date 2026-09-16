# Saphira Desktop Companion — Reaction Image Edition

This is the first working foundation for Saphira. It uses a normal desktop window, Ollama for conversation, and reaction images for emotion. Live2D can replace the image renderer later without replacing the brain/personality architecture.

## Project layout

- `main.py` — starts Saphira
- `core/brain.py` — Ollama conversation + emotion JSON
- `ui/window.py` — desktop window + reaction image switching
- `config/settings.json` — Ollama model and Saphira personality
- `assets/reactions/` — put Saphira reaction images here

## Reaction filenames

Add PNGs with these names:

`neutral.png`, `happy.png`, `excited.png`, `sad.png`, `angry.png`, `annoyed.png`, `shocked.png`, `embarrassed.png`, `confused.png`, `disappointed.png`, `thinking.png`, `sleepy.png`

A missing emotion image falls back to `neutral` if available.

## Run

1. Install Python 3.10+.
2. Install Ollama and make sure it is running.
3. Pull the model named in `config/settings.json`, or change that name to a model you already have.
4. Open a terminal in this folder.
5. Run: `pip install -r requirements.txt`
6. Run: `python main.py`

## Next development steps

1. Make the window transparent and image-only.
2. Add proper chat UI/history.
3. Add text-to-speech.
4. Add screen/vision input.
5. Add memory.
6. Replace the reaction renderer with Live2D when the Cubism model is ready.
