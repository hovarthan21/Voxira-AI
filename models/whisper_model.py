import whisper
import os

model = whisper.load_model("medium")  

def transcribe_audio(file_path: str):
    try:
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        return f"Error: {e}"
