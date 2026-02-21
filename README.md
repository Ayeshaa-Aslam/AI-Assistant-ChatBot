# Support Ticket Resolution Agent with Multi-Step Review Loop
An AI-powered support assistant built using LangGraph that classifies support tickets, retrieves relevant context, generates responses, and validates them through an automated review loop.
The system retries failed drafts (up to 2 times) and escalates unresolved tickets for human review.

---

# Features
- Accepts support ticket (subject + description).
- Classifies ticket into Billing, Technical, Security, or General.
- Category-based RAG (Retrieval Augmented Generation).
- Generates customer-facing draft response.
- LLM-based review & policy validation.
- Automatic retry loop (maximum 2 attempts).
- Optional escalation logging into CSV file.

---

# Workflow
Input Ticket → Classification → Context Retrieval (RAG) → Draft Generation → Review → Retry (if failed) → Final Output / Escalation

---

# Components
- Classification → LLM-based ticket categorization
- Retrieval (RAG) → Category-specific knowledge fetching
- Draft Generator → Context-aware response creation
- Reviewer → Quality & policy compliance check
- Retry Logic → Feedback-driven refinement (max 2 loops)
- Escalation → Logs failed cases to CSV for manual review

---

# Technical Stack
Python
LangGraph (graph-based orchestration)
LangChain
LLM Provider (OpenAI)
Vector Store / Document Retrieval
CSV (for escalation logging)

---

~ Ayesha Aslam
