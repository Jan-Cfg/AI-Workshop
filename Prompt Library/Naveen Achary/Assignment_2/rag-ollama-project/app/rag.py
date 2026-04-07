from db import get_connection
from embedding import embed

def retrieve(query: str, k=3):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT content
        FROM documents
        ORDER BY embedding <-> %s
        LIMIT %s;
    """, (embed(query), k))

    results = [r[0] for r in cur.fetchall()]

    cur.close()
    conn.close()

    return "\n".join(results)