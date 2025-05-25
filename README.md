# Project Sentinel: Confidential Video Leakage Solution with Anti-Analog Hole Watermarking

## _A cutting-edge system designed to protect sensitive video content from unauthorized distribution and identify leak sources._

---

## Table of Contents
- [About Project Sentinel](#about-project-sentinel)
- [Problem Solved](#problem-solved)
- [Key Features](#key-features)
- [How It Works (Technical Overview)](#how-it-works-technical-overview)
- [Project Status](#project-status)
- [Prerequisites](#prerequisites)
- [Getting Started (Prototype Setup)](#getting-started-prototype-setup)
- [Usage (Running the Prototype)](#usage-running-the-prototype)
- [Demo](#demo)
- [Future Enhancements / Roadmap](#future-enhancements--roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## About Project Sentinel

In an era where digital content can be easily replicated and shared, securing confidential video from unauthorized leaks is a paramount challenge. Traditional Digital Rights Management (DRM) and basic watermarking often fall short against the "analog hole"—where content is simply re-recorded from a digital screen using a physical camera.

**Project Sentinel** is an innovative, multi-layered video watermarking and leak attribution system designed to directly counter this critical vulnerability. It aims to provide an unprecedented deterrent against content leakage by making any leaked video either directly attributable to its source or rendered effectively unusable.

**This project is currently in active development, with a functional prototype demonstrating its core capabilities.**

## Problem Solved

*   **The "Analog Hole":** Traditional DRM cannot prevent a user from simply recording their screen with a phone or camera, bypassing digital protection layers.
*   **Lack of Attribution:** Without robust watermarking, identifying the source of a leak is extremely difficult, making accountability impossible.
*   **Content Value Degradation:** Leaked confidential videos (e.g., pre-release movies, sensitive corporate training, legal depositions) retain their full value, encouraging unauthorized sharing.

## Key Features

*   **Multi-Layered Adaptive Watermarking:**
    *   **Steganographic Layer:** An invisible (for production), resilient identifier embedded within the video content for source attribution.
    *   **Perceptually Destructive Watermark (PDW):** A unique, active watermark designed to be invisible or highly subtle digitally, but to become conspicuously visible and degrade content quality upon:
        *   Unauthorized re-recording from a digital screen (analog hole attack).
        *   Aggressive digital filtering or re-encoding attempts aimed at watermark removal.
*   **Deterrence by Degradation:** Directly impacts the informational value of illegally distributed content, rendering it useless or clearly branded.
*   **GPU-Accelerated Processing:** Leverages hardware acceleration (e.g., Intel Quick Sync Video) for efficient video frame processing and reconstruction, enhancing performance.
*   **Real-time Progress Feedback:** Command-line updates and progress bars for long-running video processing tasks.

## How It Works (Technical Overview)

Project Sentinel operates by meticulously processing video files frame by frame, applying its two distinct watermarking layers. The core logic is implemented in **Python** using powerful libraries for video and image manipulation, alongside external tools for robust encoding.

1.  **Video Ingestion & Frame Extraction:**
    *   The system uses `FFmpeg` to extract all individual frames from the input video, saving them as high-quality image files (e.g., JPGs).
    *   `FFprobe` is used to accurately determine video properties like Frames Per Second (FPS) and total frame count for precise reconstruction and progress tracking.

2.  **Multi-Layered Watermark Application (per frame):**
    *   **Steganographic Layer (Attribution):** Using `OpenCV`'s image manipulation capabilities, a unique identifier (`CODE` derived from sender ID and timestamp) is overlaid onto a subset of frames. This is done with extremely low opacity and small font size to simulate invisibility. In a full system, this would evolve to more sophisticated DWT/DCT domain embedding for greater resilience and imperceptibility.
    *   **Perceptually Destructive Watermark (PDW - Deterrent):** This is the core innovation. A carefully designed, high-frequency checkerboard pattern is overlaid onto *every* frame using `OpenCV`'s `addWeighted` blending. Crucially, this pattern undergoes **subtle temporal variations** (e.g., alternating between two slightly different patterns) between consecutive frames. When viewed digitally, this subtle variation is almost imperceptible.

3.  **Video Reconstruction & Output:**
    *   After watermarking, the modified frames are re-assembled into a single video file using `FFmpeg`.
    *   **GPU Acceleration:** For efficient encoding, the system is configured to utilize hardware encoders (e.g., `h264_qsv` for Intel Quick Sync Video) where available, significantly speeding up the reconstruction process compared to CPU-only encoding.

### Technologies Utilized:
*   **Python:** Main programming language for logic and orchestration.
*   **FFmpeg / FFprobe:** Industry-standard tools for video encoding, decoding, and analysis.
*   **OpenCV (`cv2`):** Powerful library for image and video processing, used for frame manipulation and watermarking.
*   **Pillow (`PIL`):** Used for advanced image operations if needed.
*   **`subprocess` module:** For seamless integration and communication with FFmpeg/FFprobe.
*   **`Flask` (Future):** Planned for building a user-friendly web interface for secure upload and delivery.

## Project Status

**Project Sentinel is currently in the prototype phase.**

The following core functionalities have been successfully implemented and demonstrated in the current `app.py` script:

*   **Robust Video Processing Pipeline:** Functional frame extraction and video reconstruction using FFmpeg, with real-time console progress.
*   **GPU Acceleration Integration:** Successful utilization of Intel Quick Sync Video (QSV) for faster video encoding.
*   **Functional Steganographic Watermark:** Embedding of subtle, traceable text identifiers into video frames (currently visible only upon close inspection of specific frames).
*   **Basic Perceptually Destructive Watermark (PDW):** A demonstrable implementation that visibly degrades video quality upon re-recording from a digital display, effectively proving the "anti-analog hole" concept.

## Prerequisites

Before running the prototype, ensure you have the following installed and configured:

1.  **Python 3.x:** Download and install from [python.org](https://www.python.org/downloads/).
2.  **FFmpeg & FFprobe:**
    *   Download the **pre-built binaries** for your operating system from [ffmpeg.org/download.html](https://ffmpeg.org/download.html) (choose a `full` or `essentials` build).
    *   **Crucially, add the path to the `bin` directory** (e.g., `C:\ffmpeg\ffmpeg-latest\bin` on Windows) to your system's PATH environment variable. Verify installation by opening a **new** terminal and running `ffmpeg -version` and `ffprobe -version`.
3.  **Required Python Libraries:**
    ```bash
    pip install opencv-python Flask Pillow numpy
    ```

## Getting Started (Prototype Setup)

Follow these steps to set up and run the prototype:

1.  **Clone the Repository (or create project directory):**
    ```bash
    git clone https://github.com/your-username/project-sentinel.git # Replace with your repo link
    cd project_sentinel
    ```
    *If not using Git, manually create a folder named `project_sentinel` and navigate into it.*

2.  **Place `app.py`:** Ensure your `app.py` script is in this root directory.

3.  **Add a Sample Video:** Place a short video file (e.g., `sample.mp4`, `test.mov`) in the root directory of the project (alongside `app.py`). This will be your input video for watermarking.

4.  **Generate PDW Pattern Files:** The PDW relies on two small image files (`pdw_pattern_a.png` and `pdw_pattern_b.png`). Run this small Python script *once* in your project's root directory to generate them:

    ```python
    # Save this as generate_pdw_patterns.py and run it: python generate_pdw_patterns.py
    import cv2
    import numpy as np

    pattern_size = 8 # Size of the repeating pattern (e.g., 8x8 pixels)

    # Pattern A: Basic checkerboard
    pattern_a = np.zeros((pattern_size, pattern_size), dtype=np.uint8)
    for r in range(pattern_size):
        for c in range(pattern_size):
            if (r + c) % 2 == 0:
                pattern_a[r, c] = 255 # White pixel
        cv2.imwrite('pdw_pattern_a.png', pattern_a)

    # Pattern B: Inverted checkerboard (for subtle temporal variation)
    pattern_b = 255 - pattern_a # Invert pattern_a
    cv2.imwrite('pdw_pattern_b.png', pattern_b)

    print("Created pdw_pattern_a.png and pdw_pattern_b.png in the current directory.")
    ```

5.  **Clean up temporary directories (if necessary):** The script automatically cleans up `temp_processed_frames/` but if you've stopped it mid-run, you might want to manually delete this folder before a fresh run. Also delete any `watermarked_sample.mp4` or `reconstructed_sample.mp4` from previous failed runs.

## Usage (Running the Prototype)

Once setup, execute the `app.py` script from your terminal in the project's root directory:

```bash
python app.py