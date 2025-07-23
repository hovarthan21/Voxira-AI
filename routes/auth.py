from fastapi import APIRouter, HTTPException, Form
import pyrebase
import json

router = APIRouter()

with open("firebase/firebase_config.json") as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

@router.post("/signup")
def signup(email: str = Form(...), password: str = Form(...)):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return {"message": "User created", "token": user['idToken']}
    except Exception as e:
        error_detail = str(e)
        if "EMAIL_EXISTS" in error_detail:
            raise HTTPException(status_code=400, detail="Email already exists")
        elif "WEAK_PASSWORD" in error_detail:
            raise HTTPException(status_code=400, detail="Password should be at least 6 characters")
        elif "INVALID_EMAIL" in error_detail:
            raise HTTPException(status_code=400, detail="Invalid email format")
        else:
            raise HTTPException(status_code=400, detail=f"Signup failed: {error_detail}")

@router.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return {"message": "Logged in", "token": user['idToken']}
    except Exception as e:
        error_detail = str(e)
        if "EMAIL_NOT_FOUND" in error_detail:
            raise HTTPException(status_code=401, detail="Email not registered")
        elif "INVALID_PASSWORD" in error_detail:
            raise HTTPException(status_code=401, detail="Invalid password")
        else:
            raise HTTPException(status_code=401, detail=f"Login failed: {error_detail}")
