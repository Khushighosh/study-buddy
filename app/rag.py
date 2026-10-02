import ollama
from ingest import col, embed

CHAT_MODEL = "qwen2.5:7b"

SYSTEM = (
    "You are a study buddy. Answer ONLY using the notes provided. "
    "Cite the source like [filename p.N] after each fact. "
    "If the notes do not contain the answer, say: "
    "'This isn't covered in your notes.' Do not guess or add outside facts. "
    "Keep answers clear and exam-friendly."
)


def retrieve(question: str, k: int = 5):
    res = col.query(query_embeddings=[embed(question)], n_results=k)
    return list(zip(res["documents"][0], res["metadatas"][0]))


def ask(question: str) -> str:
    hits = retrieve(question)
    context = "\n\n".join(
        f"[{m['source']} p.{m['page']}]\n{d}" for d, m in hits
    )
    reply = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Notes:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return reply["message"]["content"]


if __name__ == "__main__":
    print("Study buddy ready. Type 'quit' to exit.")
    while True:
        q = input("\nYou: ").strip()
        if q.lower() in {"quit", "exit"}:
            break
        if q:
            print("\nBuddy:", ask(q))