# app.py

import os
import subprocess
import cv2
import shutil # For robust directory cleanup
from datetime import datetime
import re # For parsing FFmpeg progress


# --- Phase 1.2: FFmpeg Frame Extraction/Re-assembly Functions (MODIFIED FOR PROGRESS) ---

# app.py

# ... (imports, get_video_fps, get_video_frame_count) ...

def run_ffmpeg_command(command, description, total_frames=None):
    """
    Runs an FFmpeg command and provides real-time progress updates,
    and prints all other FFmpeg output.
    """
    print(f"\n--- {description} ---")
    print(f"Executing command: {' '.join(command)}")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # Redirect stderr to stdout
        universal_newlines=True,
        bufsize=1
    )

    last_progress_line = ""
    # Store all lines for potential later inspection if needed
    all_ffmpeg_output = []

    for line in process.stdout:
        line = line.strip()
        all_ffmpeg_output.append(line) # Store every line

        # Only print progress for actual progress lines
        if "frame=" in line or "time=" in line or "speed=" in line:
            frame_match = re.search(r'frame=\s*(\d+)', line)
            if total_frames and frame_match:
                current_frame = int(frame_match.group(1))
                percentage = (current_frame / total_frames) * 100
                progress_bar = '#' * int(percentage // 2) + '-' * (50 - int(percentage // 2))
                # Using \r for progress bar, but only if it's an actual progress line
                print(f"\r[{progress_bar}] {percentage:.1f}% Frame: {current_frame}/{total_frames} ", end="", flush=True)
            else:
                # If no total_frames or frame match, but it's a progress line, just print it normally
                print(f"\r{line}", end="", flush=True)
            last_progress_line = line
        else:
            # Print other informational/warning lines from FFmpeg
            # Avoid re-printing status lines if they appear
            if line and not any(k in line for k in ["Press [q] to stop", "encoder", "Stream mapping", "Output #", "Past duration", "conversion failed", "averaging frame rate"]):
                print(f"\n[FFmpeg] {line}")
                
    print("\n") # Ensure a final newline after any progress bar

    process.wait()

    if process.returncode != 0:
        print(f"\nERROR: FFmpeg command failed with exit code {process.returncode}.")
        print(f"Full FFmpeg output (last lines):")
        for output_line in all_ffmpeg_output[-20:]: # Print last 20 lines of output
            print(f"> {output_line}")
        raise subprocess.CalledProcessError(process.returncode, command, output="\n".join(all_ffmpeg_output))
    else:
        print(f"Successfully completed {description}.")


# --- Updated extract_frames to use run_ffmpeg_command again ---
def extract_frames(video_path, output_dir):
    """Extracts frames from a video using FFmpeg."""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
        
    command = [
        'ffmpeg',
        '-i', video_path,
        '-q:v', '2', # Quality setting for JPEG output
        f'{output_dir}/frame_%04d.jpg'
    ]
    
    total_frames = get_video_frame_count(video_path)
    if total_frames == 0: 
        print("Warning: Could not determine total frames for progress during extraction.")

    run_ffmpeg_command(command, "Extracting Frames", total_frames)

# --- Updated reconstruct_video to use run_ffmpeg_command again and Intel QSV (if applicable) ---
def reconstruct_video(input_dir, output_video_path, fps):
    """Reconstructs a video from a sequence of frames using FFmpeg."""
    if os.path.exists(output_video_path):
        os.remove(output_video_path)

    # Determine total frames from the extracted frames for progress calculation
    frame_files = [f for f in os.listdir(input_dir) if f.startswith('frame_') and f.endswith('.jpg')]
    total_frames = len(frame_files)
    if total_frames == 0:
        print("Warning: No frames found in input_dir for reconstruction. Reconstruction might fail or be empty.")
        # Raise an error or handle this more gracefully if you want to prevent FFmpeg call
        # For prototype, we'll let FFmpeg try and fail gracefully if no frames.

    command = [
        'ffmpeg',
        '-y',
        '-framerate', str(fps),
        '-i', f'{input_dir}/frame_%04d.jpg',
        '-c:v', 'h264_qsv', # Using Intel QSV. Change to 'libx264' if QSV gives issues.
        # '-preset', 'medium', # Optional QSV preset for quality/speed
        '-pix_fmt', 'yuv420p',
        output_video_path
    ]

    run_ffmpeg_command(command, "Reconstructing Video", total_frames)


def get_video_fps(video_path):
    # ... (No change to this function, it's fine as is) ...
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=avg_frame_rate',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        fps_str = result.stdout.strip()
        if '/' in fps_str:
            numerator, denominator = map(int, fps_str.split('/'))
            return numerator / denominator
        else:
            return float(fps_str)
    except Exception as e:
        print(f"ERROR: Could not determine FPS for '{video_path}'. Using default of 30. Error: {e}")
        return 30 # Default to 30 FPS if detection fails

def get_video_frame_count(video_path):
    """
    Uses FFprobe to get the total number of frames in a video.
    """
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-count_frames', # This option counts frames
        '-show_entries', 'stream=nb_read_frames', # Use nb_read_frames for exact count
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return int(result.stdout.strip())
    except Exception as e:
        print(f"ERROR: Could not determine total frames for '{video_path}'. Error: {e}")
        return 0


# (Keep all your existing functions: run_ffmpeg_command, extract_frames,
# reconstruct_video, get_video_fps, get_video_frame_count)



# (Keep all your existing functions: run_ffmpeg_command, extract_frames,
# reconstruct_video, get_video_fps, get_video_frame_count)


# --- Phase 2: Steganographic Watermark Function (REVERTED TO SUBTLE) ---

def embed_steganographic_mark(frame, text_data, frame_number, embed_frequency=50): # <--- Reverted to 50
    """
    Embeds a subtle, almost invisible text mark onto the frame.
    For prototype, applies on every 'embed_frequency' frame.
    
    Args:
        frame (np.array): The OpenCV image frame (NumPy array).
        text_data (str): The string representing the steganographic code.
        frame_number (int): The current frame number (1-based).
        embed_frequency (int): How often to embed the mark (e.g., 50 means every 50th frame).
    Returns:
        tuple: (modified_frame, bool) - The modified frame and True if mark was added, False otherwise.
    """
    mark_added = False
    if frame_number % embed_frequency == 0:
        mark_added = True
        # Define text properties - REVERTED TO SUBTLE VALUES
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4 # <--- Subtle font size
        font_thickness = 1 # <--- Thin text
        text_color = (255, 255, 255) # <--- White text (BGR format)

        # Get text size to position it accurately
        (text_width, text_height), baseline = cv2.getTextSize(text_data, font, font_scale, font_thickness)

        # Position the text (bottom-right corner, with some padding)
        padding_x = 10
        padding_y = 20
        x_pos = frame.shape[1] - text_width - padding_x
        y_pos = frame.shape[0] - padding_y

        # Create a blank overlay for the text
        overlay = frame.copy()
        
        # Draw the text on the overlay
        cv2.putText(overlay, text_data, (x_pos, y_pos), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        # Blend the overlay with the original frame for transparency
        # Adjust alpha (transparency) - lower for more "invisible".
        alpha = 0.08 # <--- Subtle transparency factor
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
    return frame, mark_added


# --- Test Block in __main__ (NO CHANGES NEEDED, it already has the counter) ---
# This block correctly uses the 'mark_added' return and 'frames_marked_count'.
if __name__ == '__main__':
    test_video_input = 'sample.mp4'
    temp_frames_output_dir = 'temp_processed_frames'
    output_watermarked_video = 'watermarked_sample.mp4'

    if not os.path.exists(test_video_input):
        print(f"ERROR: Test video '{test_video_input}' not found. Please place a video file or update the path.")
    else:
        print(f"\n--- Starting Video Watermarking Prototype ---")
        try:
            fps = get_video_fps(test_video_input)
            print(f"Detected FPS: {fps}")

            # Step 1: Extract frames
            extract_frames(test_video_input, temp_frames_output_dir)

            # Step 2: Apply Steganographic Watermark to each frame
            print("\n--- Applying Steganographic Watermark ---")
            steg_code = f"UID_{os.getpid()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_CONFIDENTIAL"
            print(f"Using Steganographic Code: {steg_code}")

            frame_files = sorted([f for f in os.listdir(temp_frames_output_dir) if f.startswith('frame_') and f.endswith('.jpg')])
            total_frames = len(frame_files)
            frames_marked_count = 0 

            for i, frame_file in enumerate(frame_files):
                frame_path = os.path.join(temp_frames_output_dir, frame_file)
                frame = cv2.imread(frame_path)
                if frame is None:
                    print(f"Warning: Could not read frame {frame_path}. Skipping.")
                    continue

                # Apply the steganographic mark
                modified_frame, mark_added = embed_steganographic_mark(frame, steg_code, i + 1) 

                if mark_added:
                    frames_marked_count += 1

                # Save the modified frame
                cv2.imwrite(frame_path, modified_frame)

                # Basic console progress for this loop
                if (i + 1) % 100 == 0 or (i + 1) == total_frames:
                    print(f"\rProcessed {i+1}/{total_frames} frames for steganographic mark.", end="", flush=True)
            print(f"\nSteganographic watermarking complete. Marks added to {frames_marked_count} out of {total_frames} frames.")

            # Step 3: Reconstruct video from watermarked frames
            reconstruct_video(temp_frames_output_dir, output_watermarked_video, fps)
            
            print(f"\n--- Prototype Complete ---")
            print(f"Watermarked video saved to: '{output_watermarked_video}'")
            print(f"Temporary frames directory: '{temp_frames_output_dir}'") # Ensure this matches
            print(f"You can now review '{output_watermarked_video}' to find the subtle marks.")


        except Exception as e:
            print(f"\n--- Prototype FAILED ---")
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()
            print("Please ensure FFmpeg/FFprobe are correctly installed and in your system PATH, and the video file exists.")
        
        finally:
            if os.path.exists(temp_frames_output_dir):
                shutil.rmtree(temp_frames_output_dir)
                print(f"Cleaned up temporary frames directory: {temp_frames_output_dir}")