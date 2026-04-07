from embedding import embed
from db import get_connection

def chunk_text(text, size=300):
    return [text[i:i+size] for i in range(0, len(text), size)]

def enrich_rag(doc_text: str):
    conn = get_connection()
    cur = conn.cursor()

    for chunk in chunk_text(doc_text):
        cur.execute(
            "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
            (chunk, embed(chunk))
        )

    conn.commit()
    cur.close()
    conn.close()