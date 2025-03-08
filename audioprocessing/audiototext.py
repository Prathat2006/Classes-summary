import whisper
import torch
from tqdm import tqdm
import numpy as np

def transcribe_audio(audio_path, progress_callback=None):
    try:
        # Check if GPU is available and use it
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model("base").to(device)
        print(f"\nUsing device: {device.upper()}")

        # Load audio and calculate total duration
        audio = whisper.load_audio(audio_path)
        total_samples = len(audio)
        sample_rate = whisper.audio.SAMPLE_RATE  # 16000 Hz by default in Whisper
        total_duration = total_samples / sample_rate  # Duration in seconds

        # Process in chunks (e.g., 10-second chunks)
        chunk_duration = 10  # seconds
        chunk_samples = chunk_duration * sample_rate
        num_chunks = int(np.ceil(total_samples / chunk_samples))
        
        transcribed_text = ""
        
        # Process audio chunks with progress
        for i in tqdm(range(num_chunks), desc="Transcribing", bar_format='{l_bar}{bar}| {elapsed}'):
            start_sample = i * chunk_samples
            end_sample = min((i + 1) * chunk_samples, total_samples)
            audio_chunk = audio[start_sample:end_sample]
            
            # Pad or trim audio chunk to expected length if needed
            audio_chunk = whisper.pad_or_trim(audio_chunk)
            
            # Transcribe chunk (no language specified, as in original)
            result = model.transcribe(audio_chunk)
            transcribed_text += result["text"] + " "
            
            # Update progress (1 chunk processed)
            if progress_callback:
                progress_callback(100 / num_chunks)  # Percentage per chunk

        return transcribed_text.strip()

    except Exception as e:
        return f"Error: {str(e)}"