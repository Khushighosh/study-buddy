from ingest import col, embed

q = input("Ask something from the notes: ")
res = col.query(query_embeddings=[embed(q)], n_results=3)
for d, m in zip(res["documents"][0], res["metadatas"][0]):
    print(f"\n[{m['source']} p.{m['page']}]\n{d[:300]}...")