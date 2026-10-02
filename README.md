\# Study Buddy



An offline exam study partner built for a friend. It answers questions and

generates quizzes from their own notes, running entirely on a laptop with open

models. Nothing is uploaded anywhere.



\## Features

\- Ask questions and get answers with citations to the notes

\- Says "This isn't covered in your notes" instead of guessing

\- Multiple-choice quizzes generated from the notes

\- Tracks weak topics and offers to practice them



\## Stack

Ollama (qwen2.5:7b + nomic-embed-text), ChromaDB, SQLite, FastAPI, plain HTML.



\## Run it

1\. Install \[Ollama](https://ollama.com/download) and Python 3.12

2\. Pull the models:

```

&#x20;  ollama pull qwen2.5:7b

&#x20;  ollama pull nomic-embed-text

```

3\. Install packages: `python -m pip install -r requirements.txt`

4\. Put notes (.pdf, .txt, .md) in `data/notes/`

5\. Index them: `python app/ingest.py`

6\. Start the app: `python -m uvicorn main:app --app-dir app`

7\. Open http://127.0.0.1:8000



Run all commands from the project folder.

