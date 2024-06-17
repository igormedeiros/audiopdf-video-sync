# Audio-PDF to Video Synchronization

This script synchronizes an audio narration with a PDF slide deck to create a video. It extracts text from the audio, identifies the slide titles in the PDF, and syncs them to produce a cohesive video presentation.

## Requirements

- Python 3.6+
- pydub
- PyMuPDF
- moviepy
- SpeechRecognition
- pyaudio

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/igormedeiros/audiopdf-video-sync.git
   cd audiopdf-video-sync

2. Install the dependencies:
```sh
pip install -r requirements.txt
```

## Usage
Place your narration MP3 file and the PDF slides in the same directory as main.py.
Run the script with the following command:
```sh
python main.py --audio ./aula1.mp3 --slides ./aula1.pdf
```

The output video will be saved as video.mp4 by default. You can specify a different output path using the --output argument:
```sh
python main.py --audio ./aula1.mp3 --slides ./aula1.pptx --output ./aula1.mp4
```

## Notes
Ensure the narration and slides are properly synced, with slide titles clearly pronounced in the audio for accurate synchronization.
Modify the script as needed to adjust durations and offsets for different slide timings.

