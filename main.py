from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, transcribe, translate, user, history



app = FastAPI()


# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/auth")
app.include_router(transcribe.router, prefix="/transcribe")
app.include_router(translate.router, prefix="/translate")
app.include_router(user.router, prefix="/credits")
app.include_router(history.router, prefix="/history")

@app.get("/")
def home():
    return {"message": "Welcome to PolyLingua AI"}
