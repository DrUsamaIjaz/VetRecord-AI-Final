import os, json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

SYSTEM = """You are the Urgency Triage Agent for a veterinary assistant in Pakistan.
Given symptoms, classify urgency (Low / Medium / High) and list possible conditions.
Do NOT diagnose. Only suggest.

Return ONLY valid JSON:
{{
  "urgency": "Low|Medium|High",
  "possible_conditions": ["...", "..."]
}}
No explanation. No markdown."""

def triage_urgency(state: dict) -> dict:
    try:
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )
        chain = ChatPromptTemplate.from_messages([
            ("system", SYSTEM),
            ("human", "Animal: {pet}\nSymptoms: {symptoms}\nDuration: {duration}")
        ]) | llm
        resp = chain.invoke({
            "pet": state.get("pet_info", "Unknown"),
            "symptoms": ", ".join(state.get("symptoms", [])),
            "duration": state.get("duration", "Unknown")
        })
        text = resp.content.strip()
        start, end = text.find("{"), text.rfind("}")
        data = json.loads(text[start:end+1])
        state["urgency"] = data.get("urgency", "Medium")
        state["possible_conditions"] = data.get("possible_conditions", [])
    except Exception as e:
        state["errors"].append(f"urgency_triage: {e}")
        state["urgency"] = state.get("urgency", "Medium")
        state["possible_conditions"] = state.get("possible_conditions", [])
    return state