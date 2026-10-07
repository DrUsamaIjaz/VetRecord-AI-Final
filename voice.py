import os, tempfile
from groq import Groq

def transcribe_audio(audio_bytes: bytes, language: str = "ur") -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language=language,
                response_format="text"
            )
        return result if isinstance(result, str) else result.text
    finally:
        os.unlink(tmp_path)