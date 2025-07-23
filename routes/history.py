# routes/history.py
from fastapi import APIRouter, Query
from utils.firebase import db

router = APIRouter()

@router.get("/")
def get_user_history(user_id: str = Query(...)):
    try:
        transcripts = db.child("users").child(user_id).child("transcripts").get().val()
        translations = db.child("users").child(user_id).child("translations").get().val()

        history = []
        if transcripts:
            for key, entry in transcripts.items():
                history_item = {
                    "file_name": entry.get("file_name", "Unknown"),
                    "transcript": entry.get("transcript", ""),
                    "timestamp": entry.get("timestamp", ""),
                    "translated_to": []
                }

                if translations:
                    for t in translations.values():
                        if t.get("timestamp") and t["timestamp"] >= entry["timestamp"]:
                            history_item["translated_to"].append(t["translated_to"])
                history.append(history_item)

        return history
    except Exception as e:
        return {"error": str(e)}
