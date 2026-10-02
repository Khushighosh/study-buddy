import random
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

import quiz
from rag import ask, retrieve

app = FastAPI()


class Question(BaseModel):
    question: str


class Result(BaseModel):
    topic: str
    correct: bool


@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "index.html")


@app.post("/api/ask")
def api_ask(body: Question):
    return {"answer": ask(body.question)}


@app.get("/api/quiz")
def api_quiz(weak: bool = False):
    rows = quiz.weak_topics(1) if weak else []
    if rows:
        doc, meta = random.choice(retrieve(rows[0][0], k=3))
    else:
        doc, meta = quiz.random_chunk()
    q = quiz.generate(doc)
    if not q:
        return {"error": "Couldn't generate a question, try again."}
    q["source"] = f"{meta['source']} p.{meta['page']}"
    return q


@app.post("/api/result")
def api_result(body: Result):
    quiz.db.execute(
        "INSERT INTO results (topic, correct, ts) VALUES (?, ?, ?)",
        (body.topic, int(body.correct), time.time()),
    )
    quiz.db.commit()
    return {"ok": True}


@app.get("/api/stats")
def api_stats():
    return [
        {"topic": t, "accuracy": round(a * 100), "count": n}
        for t, a, n in quiz.weak_topics(5)
    ]