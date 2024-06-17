import os
import argparse
from moviepy.editor import *
from pdf2image import convert_from_path
import tempfile
import speech_recognition as sr
from pydub import AudioSegment

def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path)
    return images

def convert_mp3_to_wav(mp3_path):
    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = mp3_path.replace('.mp3', '.wav')
    audio.export(wav_path, format="wav")
    return wav_path

def recognize_speech_from_audio(audio_path):
    recognizer = sr.Recognizer()
    wav_path = convert_mp3_to_wav(audio_path)
    timestamps = []

    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        
        # Mock timestamps for demo purposes (you should replace this with actual logic)
        timestamps = [
            {"title": "Introdução ao Curso", "start_time": 0},
            {"title": "Importância da Proteção contra Descargas Atmosféricas", "start_time": 10},
            {"title": "Normas Técnicas e Regulações", "start_time": 20},
            {"title": "Componentes de um SPDA", "start_time": 30},
            {"title": "Tipos de SPDA", "start_time": 40},
            {"title": "Manutenção e Inspeção", "start_time": 50},
            {"title": "Conclusão", "start_time": 60},
        ]

    os.remove(wav_path)  # Clean up temporary WAV file
    return timestamps, len(audio_data.frame_data) / audio_data.sample_rate

def create_video_from_pdf_and_audio(pdf_path, audio_path, output_path):
    # Convert PDF to images
    images = pdf_to_images(pdf_path)

    # Recognize speech and get timestamps
    timestamps, audio_duration = recognize_speech_from_audio(audio_path)

    # Create video clips from images based on timestamps
    clips = []
    temp_files = []
    for i, image in enumerate(images):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            image.save(tmp_file, format='PNG')
            temp_files.append(tmp_file.name)
            
            start_time = timestamps[i]["start_time"]
            end_time = timestamps[i+1]["start_time"] if i+1 < len(timestamps) else audio_duration
            
            img_clip = ImageClip(tmp_file.name).set_start(start_time).set_duration(end_time - start_time)
            clips.append(img_clip)

    # Concatenate image clips into a single video
    video = concatenate_videoclips(clips, method="compose")

    # Add audio to the video
    audio = AudioFileClip(audio_path).subclip(0, audio_duration)
    final_video = video.set_audio(audio)

    # Write the result to a file
    final_video.write_videofile(output_path, codec='libx264', fps=24)

    # Clean up temporary files
    for temp_file in temp_files:
        os.remove(temp_file)

def main():
    parser = argparse.ArgumentParser(description="Create a video from a PDF with synchronized audio.")
    parser.add_argument("--audio", required=True, help="Path to the audio file (MP3 format).")
    parser.add_argument("--slides", required=True, help="Path to the PDF file.")
    parser.add_argument("--output", required=True, help="Path to the output video file (MP4 format).")

    args = parser.parse_args()
    
    create_video_from_pdf_and_audio(args.slides, args.audio, args.output)

if __name__ == "__main__":
    main()
