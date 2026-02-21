from langgraph.graph import StateGraph, END
from classifier import classifier_node
from retriever import retriever_node
from drafter import drafter_node
from reviewer import review_node
from schemas import GraphState

workflow = StateGraph(GraphState)
workflow.add_node("classifier", classifier_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("drafter", drafter_node)
workflow.add_node("reviewer", review_node)

# Entry Point
workflow.set_entry_point("classifier")

# Workflow
workflow.add_edge("classifier", "retriever")
workflow.add_edge("retriever", "drafter")
workflow.add_edge("drafter", "reviewer")

# Condition edge for review loop
def retryfunction(state):
    retry_count = state.get('retry_count', 0)
    if state['review_decision'] == "APPROVED":
        return "end"
    elif retry_count < 2:
       return "retry"
    else:
        return "Escalate"
    
workflow.add_conditional_edges(
    "reviewer",
    retryfunction,
    {
        "end": END,
        "retry": "retriever",
        "Escalate": "escalate",
    }
)

def escalate_ticket(state):
    print("AI failed 2 attempts. Sending to human support.")
    return {"escalation_reason": "Escalated after 2 failed attempts"}

workflow.add_node("escalate", escalate_ticket)
workflow.add_edge("escalate", END)
app = workflow.compile()

# test
if __name__ == "__main__":
    state: GraphState = {
    "subject": input("Enter ticket subject: "),
    "description": input("Enter ticket description: "),
    "category": None,
    "retrieved_context": [],
    "draft_response": None,
    "review_result": None,
    "retry_count": 0
}
    result = app.invoke(state)
    print("\nWorkflow finished with result:")
    print(result['draft_response'])
