import argparse
import speech_recognition as sr
from pydub import AudioSegment
from PyPDF2 import PdfReader
import moviepy.editor as mpe
from moviepy.video.io.bindings import PIL_to_npimage
from PIL import Image
import os
import fitz
import io


# Delay for slide change (parameterizable) - NOW IN SECONDS
SLIDE_CHANGE_DELAY = 23  # Default delay is 8 seconds

def load_pdf(pdf_file):
    """Loads the PDF and extracts slide titles."""
    with open(pdf_file, 'rb') as f:
        pdf = PdfReader(f)
        slide_titles = []
        for i in range(len(pdf.pages)):
            text = pdf.pages[i].extract_text().split('\n')[0]
            title = text.strip() if text else f"Slide {i + 1}"
            slide_titles.append(title)
    return slide_titles

def load_audio(audio_mp3):
    """Loads the MP3 audio, converts to WAV, and transcribes to text."""
    recognizer = sr.Recognizer()
    sound = AudioSegment.from_mp3(audio_mp3)
    temp_wav_file = "temp.wav"  # Temporary WAV file
    sound.export(temp_wav_file, format="wav")

    with sr.AudioFile(temp_wav_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='pt-BR')
        except sr.UnknownValueError:
            raise ValueError("Could not understand the audio")
        except sr.RequestError as e:
            raise ValueError(f"Error requesting speech recognition service; {e}")

    os.remove(temp_wav_file)  # Remove temporary file

    return text, sound  # Return text and AudioSegment

def sync_slides_with_audio(slide_titles, audio_text, audio):
    """Divides the audio into segments according to the number of slides."""
    audio_duration = audio.duration_seconds
    slide_duration = audio_duration / len(slide_titles)  # Average duration per slide
    slide_times = []  # List to store the start times of each slide

    current_time = 0  # Variable to track the current time of the audio

    for i in range(len(slide_titles)):
        start_time = current_time
        end_time = start_time + slide_duration
        slide_times.append((start_time, end_time))
        current_time = end_time  # Update the current time for the next slide

    return slide_times  # Return the list with the slide times

def create_slide_images(pdf_file):
    """Creates images of the slides from the PDF."""
    slide_images = []
    with fitz.open(pdf_file) as pdf:
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution by 2x
            img = Image.open(io.BytesIO(pixmap.tobytes()))
            slide_images.append(PIL_to_npimage(img))
    return slide_images

def create_mp4_video(audio, slide_images, slide_times, output_filename):
    """Creates the MP4 video with synchronized slides and audio."""
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.editor import CompositeVideoClip, ImageClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip

    clips = []
    audio_duration = audio.duration_seconds

    for i, (img, (start, end)) in enumerate(zip(slide_images, slide_times)):
        # Calculate slide duration
        slide_duration = end - start

        # Apply slide change delay to the END time of each slide
        end = min(end + SLIDE_CHANGE_DELAY, audio_duration) 

        # Create the image clip with the correct duration
        clip_duration = end - start
        clip = mpe.ImageClip(img, duration=clip_duration).set_start(start).set_fps(1)

        # Add fade in/out only if the slide has some duration
        if clip_duration > 0:
            clip = clip.crossfadein(0.5).crossfadeout(0.5)

        clips.append(clip)

    # Convert AudioSegment to AudioFileClip
    temp_audio_file = "temp_audio.mp3"
    audio.export(temp_audio_file, format="mp3")
    audio_clip = AudioFileClip(temp_audio_file)

    # Create the final video with audio
    video = mpe.CompositeVideoClip(clips, size=slide_images[0].shape[1::-1])
    final_video = video.set_audio(audio_clip)
    final_video.write_videofile(output_filename, codec='libx264', audio_codec='aac')

    os.remove(temp_audio_file)  # Remove temporary file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize audio with slides and create MP4 video.")
    parser.add_argument('base_filename', help="Base filename (without extension) of the audio and slides files.")
    args = parser.parse_args()

    audio_filename = args.base_filename + ".mp3"
    slides_filename = args.base_filename + ".pdf"
    output_filename = args.base_filename + ".mp4"

    if not os.path.exists(audio_filename) or not os.path.exists(slides_filename):
        raise FileNotFoundError(f"Audio ({audio_filename}) or slides ({slides_filename}) file not found.")

    slide_titles = load_pdf(slides_filename)
    audio_text, audio = load_audio(audio_filename)
    slide_times = sync_slides_with_audio(slide_titles, audio_text, audio)
    slide_images = create_slide_images(slides_filename)
    create_mp4_video(audio, slide_images, slide_times, output_filename)