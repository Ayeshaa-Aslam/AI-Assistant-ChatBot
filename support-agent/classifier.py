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

def ticket_classifier(state):
    """
    LangGraph node that categorizes support tickets
    """
    print("[CLASSIFIER] entered")
    print("[CLASSIFIER] calling OpenAI...")

    prompt = f"""
ANALYZE THIS SUPPORT TICKET AND CATEGORIZE IT.

TICKET DETAILS:
- Subject: {state['subject']}
- Problem: {state['description']}

AVAILABLE CATEGORIES:
billing: Payment issues, refunds, subscriptions, invoices
technical: App crashes, login problems, bugs, errors
security: 2FA, passwords, unauthorized access, account security
general: Account settings, support hours, general questions

RESPOND WITH ONLY ONE WORD: billing OR technical OR security OR general.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    category_raw = response.content.strip().lower()

    print("[CLASSIFIER] got response from OpenAI")
    print("[CLASSIFIER] raw category:", category_raw)

    valid_categories = {"billing", "technical", "security", "general"}
    category = category_raw if category_raw in valid_categories else "uncategorized"

    print("[CLASSIFIER] final category:", category)
    return {"category": category}

classifier_node = RunnableLambda(ticket_classifier)




