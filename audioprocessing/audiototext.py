import whisper
import torch

# 🔹 Define your audio file path
audio_file_path = "audio2.mp3"  # Change this to your file path

def transcribe_audio(audio_path):
    try:
        # 🔹 Check if GPU is available and use it
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model("base").to(device)  # Move model to GPU if available

        print(f"\nUsing device: {device.upper()}")  # Print whether using CPU or GPU

        # 🔹 Transcribe using GPU if available
        result = model.transcribe(audio_path)

        return result["text"]

    except Exception as e:
        return f"Error: {str(e)}"

# if __name__ == "__main__":
#     print(f"\nProcessing file: {audio_file_path}")

#     transcription = transcribe_audio(audio_file_path)

#     print("\nTranscription:\n", transcription)

#     # Save the transcription to a text file
#     with open("transcription.txt", "w") as file:
#         file.write(transcription)
