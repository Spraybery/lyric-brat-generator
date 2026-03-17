import os
import sys

# Add FFmpeg to PATH for Whisper (Windows fallback)
ffmpeg_path = r"C:\Users\delan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")

import whisper
import json
import argparse

def transcribe_to_json(audio_file, output_file=None, model_name="base"):
    """
    Transcribe audio/video file using Whisper and return our JSON format as a dict.
    Optionally writes to output_file if provided.

    Models (speed vs accuracy):
    - tiny: Fastest, least accurate
    - base: Good balance (recommended)
    - small: Better accuracy
    - medium: High accuracy
    - large: Best accuracy (slow, needs GPU)
    """
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print(f"Transcribing '{audio_file}'... (this may take a while)")
    result = model.transcribe(audio_file, word_timestamps=True)

    # Convert Whisper output to our format
    title = os.path.splitext(os.path.basename(audio_file))[0]
    output = {
        "meta": {
            "title": title,
            "artist": "Unknown"
        },
        "lines": []
    }

    for segment in result["segments"]:
        line = {
            "start": round(segment["start"], 3),
            "end": round(segment["end"], 3),
            "text": segment["text"].strip(),
            "words": []
        }

        # Add word-level timestamps
        if "words" in segment:
            for word_info in segment["words"]:
                line["words"].append({
                    "text": word_info["word"].strip(),
                    "start": round(word_info["start"], 3),
                    "end": round(word_info["end"], 3)
                })

        output["lines"].append(line)

    # Optionally write JSON output to file
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Successfully generated '{output_file}'")

    print(f"Found {len(output['lines'])} lines of lyrics.")
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract lyrics with timestamps using Whisper AI")
    parser.add_argument("audio_file", help="Path to audio/video file (mp3, mp4, wav, etc.)")
    parser.add_argument("output_file", help="Path to output JSON file")
    parser.add_argument("--model", default="base", help="Whisper model: tiny, base, small, medium, large")
    
    args = parser.parse_args()
    result = transcribe_to_json(args.audio_file, args.output_file, args.model)
    if not args.output_file:
        print(json.dumps(result, indent=2, ensure_ascii=False))
