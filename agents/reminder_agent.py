import os, json
from datetime import datetime, timedelta
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

SYSTEM = """You are the Reminder Agent for VetRecord AI.
Given symptoms and urgency, suggest ONE vaccine or follow-up reminder
and when it should happen (days from today).

Return ONLY valid JSON:
{{
  "vaccine": "...",
  "days_from_now": 7,
  "vet_notification": "One short line for the vet"
}}
No explanation. No markdown."""

def schedule_reminder(state: dict) -> dict:
    try:
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )
        chain = ChatPromptTemplate.from_messages([
            ("system", SYSTEM),
            ("human",
             "Animal: {pet}\nSymptoms: {symptoms}\nUrgency: {urgency}")
        ]) | llm
        resp = chain.invoke({
            "pet": state.get("pet_info", "Unknown"),
            "symptoms": ", ".join(state.get("symptoms", [])),
            "urgency": state.get("urgency", "Medium")
        })
        text = resp.content.strip()
        start, end = text.find("{"), text.rfind("}")
        data = json.loads(text[start:end+1])
        days = int(data.get("days_from_now", 7))
        due = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        state["reminder"] = {
            "vaccine": data.get("vaccine", "Follow-up"),
            "due_date": due
        }
        state["vet_notification"] = data.get("vet_notification", "")
    except Exception as e:
        state["errors"].append(f"reminder_agent: {e}")
        state["reminder"] = {"vaccine": "Follow-up", "due_date": ""}
        state["vet_notification"] = ""
    return state