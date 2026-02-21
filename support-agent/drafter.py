import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
    temperature=0.3,
)

def draft_response(state):
    """
    LangGraph node that drafts support ticket responses
    """
    context_list = state.get("retrieved_context", [])
    context_text = "\n- " + "\n- ".join(context_list) if context_list else "No relevant knowledge base context found."

    prompt = f"""
You are a helpful support agent. Write a short, practical reply.

CUSTOMER ISSUE:
Subject: {state['subject']}
Description: {state['description']}

KNOWLEDGE BASE SNIPPETS:
{context_text}

Rules:
- Keep it 6–10 lines max
- Be friendly and direct
- Give clear steps
- Ask ONE clarifying question only if needed
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    print("[DRAFTER] got response from OpenAI")
    return {"draft_response": response.content}

drafter_node = RunnableLambda(draft_response)
