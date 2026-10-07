
Commit it.

---

## 🤖 PHASE 2: THE 4 AGENTS (3 hours)

Each agent is a small function. Every agent gets input state, adds its piece, returns updated state.

### File: `agents/symptom_extractor.py`

```python
import os, json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

SYSTEM = """You are the Symptom Extractor Agent for VetRecord AI.
Given an animal description (English or Urdu), extract ONLY:
- pet_info (species: dog, cat, cow, buffalo, goat, sheep, poultry, parrot, rabbit, etc.)
- symptoms (list of symptoms)
- duration (how long, or "Unknown")

Return ONLY valid JSON:
{{
  "pet_info": "...",
  "symptoms": ["...", "..."],
  "duration": "..."
}}
No explanation. No markdown."""

def extract_symptoms(state: dict) -> dict:
    try:
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )
        chain = ChatPromptTemplate.from_messages([
            ("system", SYSTEM), ("human", "{input}")
        ]) | llm
        resp = chain.invoke({"input": state["raw_input"]})
        text = resp.content.strip()
        start, end = text.find("{"), text.rfind("}")
        data = json.loads(text[start:end+1])
        state["pet_info"] = data.get("pet_info", "Unknown")
        state["symptoms"] = data.get("symptoms", [])
        state["duration"] = data.get("duration", "Unknown")
    except Exception as e:
        state["errors"].append(f"symptom_extractor: {e}")
        state["pet_info"] = state.get("pet_info", "Unknown")
        state["symptoms"] = state.get("symptoms", [])
        state["duration"] = state.get("duration", "Unknown")
    return state