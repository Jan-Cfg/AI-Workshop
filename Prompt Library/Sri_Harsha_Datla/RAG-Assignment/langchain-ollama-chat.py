from chroma_db import retrieve_context_from_chroma
from chainlit import Message, on_chat_start
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import chainlit as cl

@on_chat_start
async def main():
    await Message(
        content=f"Hello, How can I help you today?",
    ).send()


@cl.on_message
async def run_chatbot(message: cl.Message):
    chat = ChatOllama(model="gemma3")

    # Take user_input from the chat
    user_input = str(message.content)

    # Retrieve context from Chroma DB using Langchain libraries
    context = retrieve_context_from_chroma(user_input, k=100)

    # Create enhanced system message with RAG context
    system_content = f"You are a helpful and concise assistant. Use the provided context to answer questions accurately. Relevant context from documents:{context}"

    # Give System message for the LLM
    messages = cl.user_session.get("messages", [
        SystemMessage(
            content=system_content)
    ])

    # Add the system message with RAG context to the history
    enhanced_messages = messages
    
    # Add the user's chat prompt to the history. This way all user prompts for the current session are stored in history providing context
    enhanced_messages.append(HumanMessage(content=user_input))

    try:
        # Send the entire conversation history with context to the model
        response = chat.invoke(enhanced_messages)

        # Get the LLM response
        assistant_response = response.content

        # Get token counts. I decided not to print them, but they can be printed for each request and response
        input_tokens = response.response_metadata.get('prompt_eval_count', 'N/A')
        output_tokens = response.response_metadata.get('eval_count', 'N/A')

        # Send the response back to the user
        await cl.Message(content=f"{assistant_response}"
                                 # f"\n\n*Input tokens: {input_tokens}*\n*Output tokens: {output_tokens}*"
                                 f"").send()

        # Add the assistant's response to the history
        messages.append(AIMessage(content=assistant_response))

        # Update the session with all requests and responses
        cl.user_session.set("messages", messages)

    except Exception as e:
        await cl.Message(content=f"An error occurred: {e}").send()



if __name__ == "__main__":
    cl.run()
