from typing import TypedDict, List, Literal, Optional

class GraphState(TypedDict):
    subject: str
    description: str
    category: Optional[str]
    retrieved_context: List[str]
    draft_response: Optional[str]
    review_result: Optional[str]
    retry_count: int

    