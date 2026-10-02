import json
import random
import sqlite3
import time

import ollama
from ingest import col
from rag import CHAT_MODEL, retrieve

db = sqlite3.connect("study.db", check_same_thread=False)
db.execute(
    """CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT, correct INTEGER, ts REAL)"""
)

PROMPT = """From the notes below, write ONE multiple-choice question that tests understanding.
Use ONLY facts stated in the notes. Return JSON with exactly these keys:
"topic" (a 2-4 word label), "question", "options" (list of exactly 4 strings, no A/B/C/D prefixes),
"answer_index" (integer 0-3), "explanation" (1-2 sentences based on the notes).

Notes:
{chunk}"""


def valid(q):
    return (
        isinstance(q, dict)
        and all(k in q for k in ("topic", "question", "options", "answer_index", "explanation"))
        and isinstance(q["options"], list)
        and len(q["options"]) == 4
        and q["answer_index"] in range(4)
    )


def generate(chunk):
    for _ in range(2):  # retry once if the JSON is bad
        r = ollama.chat(
            model=CHAT_MODEL,
            format="json",
            messages=[{"role": "user", "content": PROMPT.format(chunk=chunk)}],
        )
        try:
            q = json.loads(r["message"]["content"])
            if valid(q):
                return q
        except json.JSONDecodeError:
            pass
    return None


def random_chunk():
    data = col.get(include=["documents", "metadatas"])
    i = random.randrange(len(data["ids"]))
    return data["documents"][i], data["metadatas"][i]


def ask_one(chunk, meta):
    q = generate(chunk)
    if not q:
        print("Couldn't generate a question, try again.")
        return
    print(f"\n{q['question']}")
    for letter, opt in zip("ABCD", q["options"]):
        print(f"  {letter}. {opt}")

    ans = ""
    while ans not in {"A", "B", "C", "D"}:
        ans = input("Your answer (A-D): ").strip().upper()

    correct = "ABCD".index(ans) == q["answer_index"]
    right = "ABCD"[q["answer_index"]]
    print("\nCorrect!" if correct else f"\nNot quite. The answer is {right}.")
    print(f"{q['explanation']}  [{meta['source']} p.{meta['page']}]")

    db.execute(
        "INSERT INTO results (topic, correct, ts) VALUES (?, ?, ?)",
        (q["topic"], int(correct), time.time()),
    )
    db.commit()


def weak_topics(n=3):
    return db.execute(
        """SELECT topic, AVG(correct), COUNT(*) FROM results
           GROUP BY topic ORDER BY AVG(correct) ASC, COUNT(*) DESC LIMIT ?""",
        (n,),
    ).fetchall()


def show_stats():
    rows = weak_topics(5)
    if not rows:
        print("\nNo quiz history yet.")
        return
    print("\nYour weakest topics:")
    for topic, acc, n in rows:
        print(f"  {topic}: {acc * 100:.0f}% correct over {n} question(s)")


def practice_weak():
    rows = weak_topics(1)
    if not rows:
        print("\nNo history yet, take a few random questions first.")
        return
    topic = rows[0][0]
    print(f"\nPracticing your weakest topic: {topic}")
    doc, meta = random.choice(retrieve(topic, k=3))
    ask_one(doc, meta)


if __name__ == "__main__":
    while True:
        print("\n1) Random question  2) Practice weak topic  3) My stats  4) Quit")
        choice = input("> ").strip()
        if choice == "1":
            ask_one(*random_chunk())
        elif choice == "2":
            practice_weak()
        elif choice == "3":
            show_stats()
        elif choice == "4":
            break