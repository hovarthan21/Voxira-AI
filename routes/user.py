# routes/user.py
from fastapi import APIRouter, Query
from utils.firebase import db

router = APIRouter()

@router.get("/history")
def get_user_history(user_id: str = Query(...)):
    try:
        transcripts = db.child("users").child(user_id).child("transcripts").get().val() or {}
        translations = db.child("users").child(user_id).child("translations").get().val() or {}

        transcript_history = list(transcripts.values())
        translation_history = list(translations.values())

        return {
            "transcripts": transcript_history,
            "translations": translation_history
        }
    except Exception as e:
        return {"error": str(e)}
