from datetime import datetime
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from vector_store import retrieve


class Answer(BaseModel):
    answer: str
    confidence: str
    used_kb: bool


@tool
def search_knowledge_base(query: str) -> str:
    """Search the local knowledge base for context relevant to the query."""
    return retrieve(query, top_k=4)


@tool
def get_current_date() -> str:
    """Returns today's date."""
    return datetime.now().strftime("%A, %B %d, %Y")


tools = [search_knowledge_base, get_current_date]
tool_map = {t.name: t for t in tools}

system_prompt = (
    "You are a helpful assistant with access to a local knowledge base. "
    "Use search_knowledge_base to answer factual questions. "
    "Use get_current_date if the user asks about today or the current date. "
    "If you don't know something, say so."
)


def handle_tool_calls(response, llm, history):
    history.append(response)
    for call in response.tool_calls:
        fn = tool_map.get(call["name"])
        result = fn.invoke(call["args"]) if fn else "tool not found"
        history.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    final = llm.invoke(history)
    history.append(AIMessage(content=final.content))
    return final.content


def structured_demo(llm):
    slm = llm.with_structured_output(Answer)
    q = "What are the main design principles of a RAG pipeline?"
    res = slm.invoke([
        SystemMessage(content="Answer the question, rate confidence as high/medium/low, and say if you used a knowledge base."),
        HumanMessage(content=q),
    ])
    print(f"\nQ: {q}")
    print(f"A: {res.answer}")
    print(f"confidence={res.confidence}  used_kb={res.used_kb}\n")


if __name__ == "__main__":
    llm = ChatOllama(model="llama3.2:1b")
    llm_tools = llm.bind_tools(tools)

    structured_demo(llm)

    history = [SystemMessage(content=system_prompt)]

    while True:
        user_input = input("you: ").strip()
        if not user_input:
            continue
        if user_input == "quit":
            break
        if user_input == "demo":
            structured_demo(llm)
            continue

        history.append(HumanMessage(content=user_input))
        resp = llm_tools.invoke(history)

        if resp.tool_calls:
            reply = handle_tool_calls(resp, llm_tools, history)
        else:
            history.append(AIMessage(content=resp.content))
            reply = resp.content

        print(f"assistant: {reply}\n")
