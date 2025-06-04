# plot_spectrum.py (or grapher.py)
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# --- Configuration ---
# How many brightest rows to use just to find the slit's vertical center
NUM_SLIT_ROWS_FOR_CENTER = 5
# The total height (in rows) of the band centered on the slit
# where we will analyze the diffraction pattern.
ANALYSIS_BAND_HEIGHT = 21 # e.g., 10 rows above, 10 below, plus the center row
# --- End Configuration ---

# --- Import the NEW analysis function from your other script ---
try:
    from makearrays import analyze_diffraction_pattern
except ImportError:
    print("Error: Could not import 'analyze_diffraction_pattern' from makearrays.py.")
    print("Make sure 'makearrays.py' is in the same directory and updated.")
    sys.exit(1)
# --- End Import ---


def plot_diffraction_profiles(image_path, num_center_rows, band_height):
    """
    Analyzes an image to find the diffraction pattern band centered on the slit,
    calculates average RGB profiles across that band, and plots them.

    Args:
        image_path (str): Path to the image file.
        num_center_rows (int): Number of brightest rows used to locate slit center.
        band_height (int): Total height of the analysis band.
    """
    print(f"Attempting to analyze diffraction pattern in: {image_path}")
    print(f"Using {num_center_rows} brightest rows to find center.")
    print(f"Analyzing a band of height {band_height} rows.")

    try:
        # Call the function from makearrays.py
        R_values, G_values, B_values, band_indices = analyze_diffraction_pattern(
            image_path, num_center_rows, band_height
        )

        if R_values is None or G_values is None or B_values is None:
             print("Analysis failed. Exiting plot function.")
             return

        print(f"\nSuccessfully extracted data for band rows: {band_indices}")
        print(f"Shape of R_values (band): {R_values.shape}")

        # --- Calculate Average Intensity Profiles ---
        # Average across the selected rows (axis=0)
        if R_values.shape[0] > 0: # Check if any rows were actually found/returned
            avg_R = np.mean(R_values, axis=0)
            avg_G = np.mean(G_values, axis=0)
            avg_B = np.mean(B_values, axis=0)
            image_width = R_values.shape[1]
            x_pixels = np.arange(image_width) # X-axis: pixel column index
        else:
            print("Warning: No band rows were selected or returned data is empty.")
            return # Exit plotting if no data

        # --- Plotting ---
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(x_pixels, avg_R, color='red', linewidth=1.5, label='Red Channel (Avg)')
        ax.plot(x_pixels, avg_G, color='green', linewidth=1.5, label='Green Channel (Avg)')
        ax.plot(x_pixels, avg_B, color='blue', linewidth=1.5, label='Blue Channel (Avg)')

        # Add labels and title
        ax.set_xlabel('Pixel Column Index')
        ax.set_ylabel('Average Intensity (0-255)')
        ax.set_title(f'Avg RGB Intensity Profile (Diffraction Band ~{band_height} rows) - {os.path.basename(image_path)}')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlim(0, image_width - 1)
        ax.set_ylim(bottom=0) # Ensure y-axis starts at 0, consider adjusting top limit if needed

        plt.tight_layout()
        print("\nDisplaying plot...")
        plt.show()

    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
    except Exception as e:
        print(f"An error occurred during analysis or plotting: {e}")
        # You might want more detailed error handling/logging here
        import traceback
        traceback.print_exc()


# --- Main execution block ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <path_to_image_file>")
        sys.exit(1)

    image_file_path = sys.argv[1]

    # Run the plotting function with the configured parameters
    plot_diffraction_profiles(image_file_path, NUM_SLIT_ROWS_FOR_CENTER, ANALYSIS_BAND_HEIGHT)
# --- End Main ---
