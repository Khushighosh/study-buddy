# Study Buddy

An offline exam study partner built for a friend. It answers questions and generates quizzes from their own notes, running entirely on a laptop with open models. Nothing is uploaded anywhere.

## Features

- Ask questions and get answers with citations to the notes
- Says "This isn't covered in your notes" instead of guessing
- Multiple-choice quizzes generated from the notes
- Tracks weak topics and offers to practice them

## How it works

1. `ingest.py` splits your notes into chunks and embeds them with `nomic-embed-text` into a local ChromaDB store.
2. For each question, the closest chunks are retrieved and passed to `qwen2.5:7b` with strict instructions to answer only from them and cite the source.
3. Quiz mode asks the model for one multiple-choice question per chunk as JSON, validates it, and logs each result in SQLite so weak topics can be practiced again.

## Stack

Ollama (qwen2.5:7b and nomic-embed-text), ChromaDB, SQLite, FastAPI, plain HTML.

## Tested on

Windows laptop with 16 GB RAM, Intel Core i7-13620H and no dedicated GPU (CPU only).

## Run it

1. Install [Ollama](https://ollama.com/download) and Python 3.12.
2. Pull the models:

```
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

3. Install packages: `python -m pip install -r requirements.txt`
4. Put notes (.pdf, .txt, .md) in `data/notes/`
5. Index them: `python app/ingest.py`
6. Start the app: `python -m uvicorn main:app --app-dir app`
7. Open http://127.0.0.1:8000

Run all commands from the project folder and keep Ollama running in the background.

## Privacy

Notes, the vector database and
