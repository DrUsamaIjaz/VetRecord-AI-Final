import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

SYSTEM = """You are the Record Writer Agent for VetRecord AI.
Write ONE concise paragraph (max 3 sentences) of recommended next steps
for the farmer, in simple English. Do not diagnose. Advise whether to
visit a vet urgently, monitor, or apply basic home care.

Return ONLY the paragraph. No preamble. No markdown."""

def write_record(state: dict) -> dict:
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
        state["recommended_next_steps"] = resp.content.strip()
    except Exception as e:
        state["errors"].append(f"record_writer: {e}")
        state["recommended_next_steps"] = "Consult a veterinarian for guidance."
    return state