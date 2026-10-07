import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents import (
    extract_symptoms,
    triage_urgency,
    write_record,
    schedule_reminder,
)

class VetState(TypedDict, total=False):
    raw_input: str
    language: str
    pet_info: str
    symptoms: list
    duration: str
    urgency: str
    possible_conditions: list
    recommended_next_steps: str
    reminder: dict
    vet_notification: str
    errors: list


def should_schedule_reminder(state: VetState) -> str:
    """Conditional edge: if urgency is High or Medium, schedule a reminder."""
    if state.get("urgency") in ("High", "Medium"):
        return "schedule_reminder"
    return "end"


def build_graph():
    graph = StateGraph(VetState)

    graph.add_node("extract_symptoms", extract_symptoms)
    graph.add_node("triage_urgency", triage_urgency)
    graph.add_node("write_record", write_record)
    graph.add_node("schedule_reminder", schedule_reminder)

    graph.set_entry_point("extract_symptoms")
    graph.add_edge("extract_symptoms", "triage_urgency")
    graph.add_edge("triage_urgency", "write_record")
    graph.add_conditional_edges(
        "write_record",
        should_schedule_reminder,
        {"schedule_reminder": "schedule_reminder", "end": END}
    )
    graph.add_edge("schedule_reminder", END)

    return graph.compile()


_graph = None

def run_workflow(raw_input: str, language: str = "en") -> dict:
    global _graph
    if _graph is None:
        _graph = build_graph()

    initial: VetState = {
        "raw_input": raw_input,
        "language": language,
        "errors": [],
    }
    result = _graph.invoke(initial)
    return dict(result)