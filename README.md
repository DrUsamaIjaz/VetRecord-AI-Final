# VetRecord AI v2 — Multi-Agent Livestock Health Assistant

## Agent Contract (DO NOT CHANGE)

### Shared State (passed between agents)
```python
{
    "raw_input": str,              # original text or transcription
    "language": str,               # "ur" or "en"
    "pet_info": str,               # species
    "symptoms": list[str],
    "duration": str,
    "urgency": str,                # "Low" | "Medium" | "High"
    "possible_conditions": list[str],
    "recommended_next_steps": str,
    "reminder": dict,              # {vaccine, due_date}
    "vet_notification": str,       # message to vet
    "errors": list[str]
}