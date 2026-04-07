import requests

def generate_answer(query,results):
    docs_text ="\n".join([f"-{doc.page_content}" for doc,score in results])
    combined_input = f"""
    Answer the following question using ONLY the provided documents.
    Return the response strictly in JSOn format like this:
    {{
    "answer":"..."
    "sources":["...","..."]
    }}
    If the answer is not present,say "i don't know".
    Question:{query}
    Documents:{docs_text}
    Answer:
     """

    url ="http://localhost:11434/api/chat"
    payload={
        "model":"llama3.2",
        "messages":[{
            "role":"system",
            "content":"You are a helpful assistant"
        },{
            "role":"user",
            "content":combined_input
        }],
        "stream":False,
        "format": "json"
    }

    response = requests.post(url,json=payload)
   # print(response.status_code)
   # print(response.text)
    data = response.json()
    return data