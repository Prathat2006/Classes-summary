import os
import json
import shutil
from datetime import datetime
from audioprocessing.audio import audioextract
from audioprocessing.audiototext import transcribe_audio
from Textprocessing.summary import lecture_summary_agent
from Textprocessing.notesgenrate import lecture_note_generator
from tqdm import tqdm

def create_folder_structure(video_name):
    """Create necessary folders for storing intermediate and final outputs."""
    base_temp_dir = "temp"
    base_output_dir = "output"
    base_history_dir = "history"

    video_temp_dir = os.path.join(base_temp_dir, video_name)
    video_output_dir = os.path.join(base_output_dir, video_name)
    video_history_dir = base_history_dir

    os.makedirs(video_temp_dir, exist_ok=True)
    os.makedirs(video_output_dir, exist_ok=True)
    os.makedirs(video_history_dir, exist_ok=True)

    return video_temp_dir, video_output_dir, video_history_dir

def process_video(video_path):
    """Main function to process video and generate final notes PDF."""
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    temp_dir, output_dir, history_dir = create_folder_structure(video_name)

    audio_path = os.path.join(temp_dir, f"{video_name}.mp3")
    history_path = os.path.join(history_dir, f"{video_name}.json")
    final_pdf_path = os.path.join(output_dir, f"{video_name}.pdf")

    print("\n🔹 Extracting audio from video...")
    audioextract(video_path, audio_path)

    # Transcription with progress
    print("\n🔹 Transcribing audio...")
    with tqdm(total=100, desc="Transcribing", bar_format='{l_bar}{bar}| {elapsed}') as pbar:
        transcription_text = transcribe_audio(audio_path, progress_callback=lambda x: pbar.update(min(x, 100 - pbar.n)))
        # Ensure progress bar reaches 100% after task completes
        if pbar.n < 100:
            pbar.update(100 - pbar.n)

    # Summary generation with progress
    print("\n🔹 Generating summary...")
    with tqdm(total=100, desc="Summarizing", bar_format='{l_bar}{bar}| {elapsed}') as pbar:
        summary_text = lecture_summary_agent(transcription_text, progress_callback=lambda x: pbar.update(min(x, 100 - pbar.n)))
        # Ensure progress bar reaches 100% after task completes
        if pbar.n < 100:
            pbar.update(100 - pbar.n)

    # Save transcription & summary
    history_data = {
        "video_name": video_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "transcription": transcription_text,
        "summary": summary_text
    }
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)

    # Notes generation with progress
    print("\n🔹 Generating notes PDF...")
    with tqdm(total=100, desc="Generating Notes", bar_format='{l_bar}{bar}| {elapsed}') as pbar:
        lecture_note_generator(summary_text, final_pdf_path, progress_callback=lambda x: pbar.update(min(x, 100 - pbar.n)))
        # Ensure progress bar reaches 100% after task completes
        if pbar.n < 100:
            pbar.update(100 - pbar.n)

    print(f"\n✅ Notes generated successfully! Saved at: {final_pdf_path}")
    print(f"📝 History saved at: {history_path}")

if __name__ == "__main__":
    video_file = "input\statsweek5lec2.webm"
    if not os.path.isfile(video_file):
        print("❌ Error: Video file not found!")
    else:
        process_video(video_file)