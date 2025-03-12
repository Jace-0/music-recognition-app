import os
import tempfile
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# Import music recognition modules
from database import FingerprintDatabase
from recognizer import MusicRecognizer

app = FastAPI(title="Music Recognition App")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

db = FingerprintDatabase("fingerprints.db")
recognizer = MusicRecognizer(db)

@app.get("/")
async def home(request: Request):
    """Render the home page with the recording interface"""
    return templates.TemplateResponse("index.html", {"request": request})
    
@app.get("/add-song")
async def add_song_page(request: Request):
    """Add Song Page"""
    return templates.TemplateResponse("add-song.html", {"request": request})

@app.post("/recognize")
async def recognize_audio(audio_file: UploadFile = File(...)):
    """Recognize a song from an uploaded audio file"""
    try:
         # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            temp_path = temp_file.name
            # print(f"Created temporary file: {temp_path}")
            
            # Write the uploaded file to the temporary file
            content = await audio_file.read()
            print(f"Read {len(content)} bytes from uploaded file")
            temp_file.write(content)

        # Convert the audio to WAV format using FFmpeg directly
        try:
            import subprocess
            
            # Define output path
            wav_path = temp_path + ".wav"
            # print(f"Converting to WAV: {wav_path}")
            
            # Run FFmpeg command
            result = subprocess.run([
                'ffmpeg',
                '-i', temp_path,
                '-acodec', 'pcm_s16le',  # Use PCM 16-bit encoding
                '-ar', '44100',          # Set sample rate to 44.1 kHz
                '-ac', '1',              # Convert to mono
                '-y',                    # Overwrite output file if it exists
                wav_path
            ], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                return {"recognized": False, "error": f"FFmpeg conversion error: {result.stderr}"}
            
            # print(f"Successfully converted to WAV")
            
            # Use the WAV file for recognition
            # print(f"Recognizing song from: {wav_path}")
            result = recognizer.recognize_song(wav_path)
            
            # Clean up
            os.remove(temp_path)
            os.remove(wav_path)
            
            return result
        except Exception as e:
            print(f"Error converting audio: {e}")
            return {"recognized": False, "error": f"Error converting audio: {str(e)}"}

    except Exception as e:
        print(f"Recognition error: {e}")
        return {"recognized": False, "error": str(e)}        
            


@app.post("/add_song")
async def add_song(
    audio_file: UploadFile = File(...),
    song_name: str = Form(...),
    artist: str = Form(...)
):
    """
    Add a new song to the database
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    try:
        content = await audio_file.read()
        temp_file.write(content)
        temp_file.close()
        
        song_id = recognizer.add_song_to_database(temp_file.name, song_name, artist)
        return {"status": "success", "song_id": song_id}
    finally:
        os.unlink(temp_file.name)

@app.get("/songs")
async def get_songs():
    """Get a list of all songs in the database"""
    songs = db.get_all_songs()
    return {"songs": songs}

@app.get("/test")
async def test():
    return {"message": "Server is working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8100, reload=True)