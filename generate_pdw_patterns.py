# generate_pdw_patterns.py
import cv2
import numpy as np
import os

def create_pdw_patterns(pattern_size=8):
    """
    Generates two small, alternating patterns for the PDW.
    These are simple checkerboard patterns designed to induce moire/flicker.
    """
    print(f"Generating PDW patterns with size {pattern_size}x{pattern_size}...")

    # Pattern A: Basic checkerboard
    pattern_a = np.zeros((pattern_size, pattern_size), dtype=np.uint8)
    for r in range(pattern_size):
        for c in range(pattern_size):
            if (r + c) % 2 == 0: # (row + col) is even, set to white
                pattern_a[r, c] = 255
    cv2.imwrite('pdw_pattern_a.png', pattern_a)
    print("Created pdw_pattern_a.png")

    # Pattern B: Inverted checkerboard (for subtle temporal variation)
    pattern_b = 255 - pattern_a # Invert pattern_a (black where A is white, vice-versa)
    cv2.imwrite('pdw_pattern_b.png', pattern_b)
    print("Created pdw_pattern_b.png")

    print("PDW pattern generation complete.")

if __name__ == '__main__':
    create_pdw_patterns(pattern_size=8) # You can try other sizes like 4 or 16 later if needed