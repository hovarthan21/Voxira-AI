from fastapi import APIRouter, Form
from googletrans import Translator
from utils.firebase import db
from datetime import datetime

router = APIRouter()
translator = Translator()

@router.post("/")
def translate_text(user_id: str = Form(...), text: str = Form(...), target_lang: str = Form(...)):
    try:
        # Translate the text
        translated = translator.translate(text, dest=target_lang)
        translated_text = translated.text

        # Save to history
        translation_data = {
            "translated_to": target_lang,
            "translated_text": translated_text,
            "timestamp": datetime.now().isoformat()
        }
        db.child("users").child(user_id).child("translations").push(translation_data)

        # ❌ Removed credit deduction since it's not needed
        # credits = db.child("users").child(user_id).child("credits").get().val()
        # db.child("users").child(user_id).update({"credits": credits - 1})

        return {"translated": translated_text}
    except Exception as e:
        return {"error": str(e)}
