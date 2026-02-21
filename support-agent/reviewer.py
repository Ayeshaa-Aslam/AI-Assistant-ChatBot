import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
    temperature=0,
)

def review_draft(state):
    """
    LangGraph node that reviews the draft response for quality and safety
    """
    prompt = f"""
You are a QA reviewer.
Reply with ONLY: APPROVED or REJECTED.

ORIGINAL TICKET:
Subject: {state['subject']}
Description: {state['description']}

DRAFT RESPONSE:
{state.get('draft_response', '')}

Approve if it is relevant, helpful, and safe.
Reject if it is wrong, confusing, unsafe, or not addressing the issue.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    decision = response.content.strip().upper()

    if decision == "APPROVED":
        state["review_decision"] = "APPROVED"
        state["review_result"] = "approved"
    else:
        state["retry_count"] = state.get("retry_count", 0) + 1
        state["review_decision"] = "REJECTED"
        state["review_result"] = "rejected"

    return state

review_node = RunnableLambda(review_draft)
