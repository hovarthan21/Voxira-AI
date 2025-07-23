import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/auth"   # Change to your backend URL after deployment
BASE_API = "http://127.0.0.1:8000" 
st.set_page_config(
    page_title="Voxira AI",
    page_icon="icon.webp",  # Optional: Emoji as favicon
    layout="centered"
)
 

def login_page():
    st.title("Login to Voxira AI")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{API_URL}/login", data={"email": email, "password": password})
        if res.status_code == 200:
            st.success("Login successful")
            st.session_state.token = res.json()['token']
            st.session_state.page = "dashboard"
            st.session_state.user_id = email.split("@")[0]  # basic user id
        else:
            st.error("Invalid login")

def signup_page():
    st.title("Sign Up for Voxira AI")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        res = requests.post(f"{API_URL}/signup", data={"email": email, "password": password})
        if res.status_code == 200:
            st.success("Account created. Now login.")
        else:
            st.error(f"Signup failed: {res.text}")

# Page routing
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    login_page()
    if st.button("No account? Sign Up"):
        st.session_state.page = "signup"

elif st.session_state.page == "signup":
    signup_page()
    if st.button("Have account? Login"):
        st.session_state.page = "login"

# ✅ Dashboard View
elif st.session_state.page == "dashboard":
    st.title("Upload Audio or Video for Transcription")
    user_id = st.session_state.get("user_id", "test-user")
    uploaded_file = st.file_uploader("Upload your audio/video file", type=["mp3", "wav", "mp4", "m4a"])

    url_input = st.text_input("Or paste a YouTube/video URL")

    if url_input:
        st.info("A valid URL will be downloaded for transcription.")


    if uploaded_file:
        if st.button("Transcribe"):
            with st.spinner("Transcribing... please wait"):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                data = {"user_id": user_id}

                # Case 1: Local file upload
                if uploaded_file:
                    files["file"] = (uploaded_file.name, uploaded_file, uploaded_file.type)

                # Case 2: URL input
                elif url_input:
                    try:
                        from pytube import YouTube
                        import tempfile

                        yt = YouTube(url_input)
                        stream = yt.streams.filter(only_audio=True).first()
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                        stream.download(filename=temp_file.name)
                        temp_file.seek(0)

                        files["file"] = ("downloaded_audio.mp4", temp_file, "video/mp4")
                        st.success("Video downloaded successfully.")
                    except Exception as e:
                        st.error(f"Error downloading video: {e}")
                        st.stop()

                response = requests.post(f"{BASE_API}/transcribe/", files=files, data=data)

                if "transcript" in response.json():
                    transcript = response.json()["transcript"]
                    st.success("✅ Transcription Completed")
                    st.session_state.transcript = transcript
                    st.text_area("Transcript:", transcript, height=300)
                else:
                    st.error("Error: " + response.json().get("error", "Unknown error"))

    # 🌍 Translation Section
    if "transcript" in st.session_state:
        st.markdown("---")
        st.subheader("🌐 Translate Transcript to Other Languages")

        languages = {
            "English": "en", "Tamil": "ta", "Hindi": "hi", "French": "fr",
            "German": "de", "Spanish": "es", "Chinese": "zh-cn", "Arabic": "ar",
            "Japanese": "ja", "Korean": "ko", "Telugu": "te", "Malayalam": "ml"
        }

        lang_keys = list(languages.keys())
        for i in range(0, len(lang_keys), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(lang_keys):
                    lang = lang_keys[i + j]
                    if cols[j].button(f"Translate to {lang}"):
                        with st.spinner(f"Translating to {lang}..."):
                            data = {
                                "user_id": user_id,
                                "text": st.session_state.transcript,
                                "target_lang": languages[lang]
                            }
                            res = requests.post(f"{BASE_API}/translate/", data=data)

                            if "translated" in res.json():
                                translated = res.json()["translated"]
                                st.success(f"✅ Translated to {lang}")
                                st.text_area(f"{lang} Translation:", translated, height=250)

                                st.download_button(
                                    label=f"📥 Download {lang} Translation",
                                    data=translated,
                                    file_name=f"{lang}_translation.txt",
                                    mime="text/plain"
                                )
                            else:
                                st.error("Translation failed.")
    else:
        st.info("👉 Please transcribe a file first to enable translation.")

    # 📜 History Section
    st.markdown("---")
    st.subheader("📜 Your Transcription & Translation History")

    if st.button("🔁 Load History"):
        try:
            response = requests.get(f"{BASE_API}/credits/history", params={"user_id": user_id})
            if response.status_code == 200:
                data = response.json()
                if not data:
                    st.info("No history found.")
                else:
                    for i, entry in enumerate(data):
                        st.markdown(f"**{i+1}. File:** `{entry['file_name']}`")
                        st.markdown(f"🕒 *{entry['timestamp']}*")
                        st.markdown("📝 **Transcript:**")
                        st.code(entry['transcript'], language="text")

                        if entry.get("translated_to"):
                            langs = ", ".join(entry["translated_to"])
                            st.markdown(f"🌐 Translated to: {langs}")
                        st.markdown("---")
            else:
                st.error(f"Failed to load history.{response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
