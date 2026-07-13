from flask import Flask, render_template, request
import os
import whisper
import tempfile
from datetime import datetime

# Tell Python where FFmpeg is located
os.environ["PATH"] += os.pathsep + r"D:\GEN AI\ffmpeg\bin"

app = Flask(__name__)

# Load Whisper model (better accuracy than tiny)
model = whisper.load_model("base.en")


# -------------------------------
# PAGE 1 – WELCOME PAGE
# -------------------------------
@app.route("/")
def welcome():
    return render_template("welcome.html")


# -------------------------------
# PAGE 2 – MAIN PAGE
# -------------------------------
@app.route("/home")
def home():
    return render_template("index.html", transcript=None, minutes=None)


# -------------------------------
# PAGE 3 – THANK YOU PAGE
# -------------------------------
@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# -------------------------------
# TRANSCRIBE AUDIO
# -------------------------------
@app.route("/transcribe", methods=["POST"])
def transcribe():

    # Check file upload
    if "audio" not in request.files:
        return "No audio uploaded"

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return "No selected file"

    # Save uploaded audio temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
        audio_file.save(temp.name)
        audio_path = temp.name

    try:
        # Transcribe audio
        result = model.transcribe(
            audio_path,
            language="en",
            fp16=False
        )

        transcript_text = result["text"]

    except Exception as e:
        return f"Error during transcription: {str(e)}"


    # -------------------------------
    # Generate Meeting Minutes
    # -------------------------------
    now = datetime.now()

    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%I:%M %p")
    location = "Online Meeting"

    minutes_text = f"""
Meeting Minutes

Date: {date}
Time: {time}
Location: {location}

Meeting Summary:
{transcript_text}

Action Items:
- To be discussed

Decisions Taken:
- To be updated
"""

    return render_template(
        "index.html",
        transcript=transcript_text,
        minutes=minutes_text
    )


# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)