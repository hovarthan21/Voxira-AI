import whisper  
from fastapi import APIRouter, File, UploadFile, Form
import os
from models.whisper_model import transcribe_audio
from utils.firebase import db
from datetime import datetime

os.environ["PATH"] += os.pathsep + r"C:\Users\Hovarthanvishnu\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"

router = APIRouter()

model = whisper.load_model("medium") 

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def transcribe(file: UploadFile = File(...), user_id: str = Form(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

    
        transcript = transcribe_audio(file_location)
        timestamp = datetime.now().isoformat()
        history_data = {
            "file_name": file.filename,
            "transcript": transcript,
            "timestamp": timestamp,
            "translated_to": [],
        }
        db.child("users").child(user_id).child("history").push(history_data)
        
        
        return {"transcript": transcript, "timestamp": timestamp}

    except Exception as e:
        return {"error": str(e)}
