# from moviepy.editor import VideoFileClip
from moviepy import *
from pydub import AudioSegment
import os
import numpy as np

def audioextract(input_video_path, output_audio_path):
    # Load the video clip
    video_clip = VideoFileClip(input_video_path)

    # Extract the audio from the video clip
    audio_clip = video_clip.audio

    # Write the audio to a separate file
    audio_clip.write_audiofile(output_audio_path)

    # Close the video and audio clips
    audio_clip.close()
    video_clip.close()

    print("Audio extraction successful!")

# def trim_audio(output_path, trim_start_seconds=20, trim_end_seconds=30):
#     """
#     Remove the first 'trim_start_seconds' seconds and the last 'trim_end_seconds' seconds from an audio file
    
#     Args:
#         output_path (str): Path to save output audio file
#         trim_start_seconds (int): Number of seconds to trim from start (default: 20)
#         trim_end_seconds (int): Number of seconds to trim from end (default: 30)
#     """
#     try:
#         # Load the audio from the input file
#         audio = AudioSegment.from_mp3(mp3_file)
        
#         # Convert seconds to milliseconds for pydub
#         trim_start_ms = trim_start_seconds * 1000
#         trim_end_ms = trim_end_seconds * 1000
        
#         # Calculate new duration after trimming
#         new_duration = len(audio) - trim_start_ms - trim_end_ms
        
#         # Ensure we don't try to trim more than the audio length
#         if new_duration <= 0:
#             raise ValueError("Audio is shorter than the total trim duration")
        
#         # Trim the audio (take everything between trim_start_ms and new_duration)
#         trimmed_audio = audio[trim_start_ms:len(audio) - trim_end_ms]
        
#         # Export the trimmed audio
#         trimmed_audio.export(
#             output_path,
#             format="mp3",  # Can be changed to wav, etc.
#             bitrate="192k"  # Adjust quality as needed
#         )
        
#         print(f"Successfully trimmed audio saved to: {output_path}")
#         print(f"Original duration: {len(audio)/1000:.2f} seconds")
#         print(f"New duration: {len(trimmed_audio)/1000:.2f} seconds")
        
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

# Example usage
# if __name__ == "__main__":
#     input_video_path = "week4bda.webm"
#     output_audio_path = "extracted_audio.mp3"
#     audioextract(input_video_path, output_audio_path)