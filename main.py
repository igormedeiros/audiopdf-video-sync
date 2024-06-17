import argparse
import os
import comtypes.client
from pptx import Presentation
from moviepy.editor import *
from PIL import Image

def pptx_to_images(slides_path, output_folder="slides"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
    powerpoint.Visible = 1

    presentation = powerpoint.Presentations.Open(slides_path)
    slide_images = []

    for i, slide in enumerate(presentation.Slides):
        image_path = os.path.join(output_folder, f"slide_{i+1}.png")
        slide.Export(image_path, "PNG")
        slide_images.append(image_path)

    presentation.Close()
    powerpoint.Quit()
    
    return slide_images

def pptx_to_mp4(slides_path, audio_path, output_path, duration_per_slide=2):
    # Convert slides to images
    slide_images = pptx_to_images(slides_path)

    # Create video clips from images
    image_clips = [ImageClip(img).set_duration(duration_per_slide) for img in slide_images]

    # Concatenate image clips
    video = concatenate_videoclips(image_clips, method="compose")

    # Add audio
    audio = AudioFileClip(audio_path).set_duration(video.duration)
    video = video.set_audio(audio)

    # Write the result to a file
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")

    # Clean up temporary slide images
    for img in slide_images:
        os.remove(img)
    os.rmdir('slides')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PPTX to MP4 with audio.")
    parser.add_argument("--audio", required=True, help="Path to the audio file (MP3 format).")
    parser.add_argument("--slides", required=True, help="Path to the PowerPoint file (PPTX format).")
    parser.add_argument("--output", required=True, help="Path to the output video file (MP4 format).")

    args = parser.parse_args()
    pptx_to_mp4(args.slides, args.audio, args.output)
