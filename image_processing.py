from PIL import Image
import numpy as np
from scipy.signal import find_peaks # MODIFIED: Import find_peaks

# MODIFIED: Define default parameters for peak detection
# These can be adjusted for sensitivity.
# Height: Minimum intensity of a peak.
# Distance: Minimum horizontal distance (in row indices) between peaks.
DEFAULT_PEAK_HEIGHT_THRESHOLD = 2.5  # Adjusted for typical signal noise
DEFAULT_PEAK_MIN_DISTANCE = 200       # Adjusted to separate distinct peaks

def calculate_rgb_row_profiles(image_path, peak_height_threshold=DEFAULT_PEAK_HEIGHT_THRESHOLD, peak_min_distance=DEFAULT_PEAK_MIN_DISTANCE):
    """
    Reads a JPG image, extracts R, G, B channels, calculates the average
    pixel value for each horizontal row, and finds peaks in these profiles.

    Args:
        image_path (str): The path to the JPG image file.
        peak_height_threshold (float): Minimum height for a peak to be detected.
        peak_min_distance (int): Minimum horizontal distance (in samples)
                                 between neighbouring peaks.

    Returns:
        dict: A dictionary containing the processed data:
              {
                  "indices": numpy.ndarray (row indices),
                  "avg_R": numpy.ndarray (average red values per row),
                  "avg_G": numpy.ndarray (average green values per row),
                  "avg_B": numpy.ndarray (average blue values per row),
                  "peaks_R": {"indices": numpy.ndarray, "heights": numpy.ndarray}, # MODIFIED
                  "peaks_G": {"indices": numpy.ndarray, "heights": numpy.ndarray}, # MODIFIED
                  "peaks_B": {"indices": numpy.ndarray, "heights": numpy.ndarray}, # MODIFIED
                  "x_axis_label": str (label for the x-axis, e.g., "Row Index"),
                  "plot_title_suffix": str (suffix for the plot title, e.g., "per Row")
              }
              Returns None if an error occurs (e.g., file not found, processing error).
    """
    try:
        img = Image.open(image_path)
        img_rgb = img.convert("RGB")
        img_array = np.array(img_rgb)  # Shape: (height, width, 3)

        # R_channel, G_channel, B_channel will have shape (height, width)
        R_channel = img_array[:, :, 0]
        G_channel = img_array[:, :, 1]
        B_channel = img_array[:, :, 2]

        # Calculate the average along axis=1 (i.e., for each row)
        # The result will have shape (height,)
        avg_R_per_row = np.mean(R_channel, axis=1)
        avg_G_per_row = np.mean(G_channel, axis=1)
        avg_B_per_row = np.mean(B_channel, axis=1)

        num_rows = img_array.shape[0]  # This is the height of the image
        row_indices = np.arange(num_rows)

        # MODIFIED: Find peaks for each channel
        peaks_r_indices, _ = find_peaks(avg_R_per_row, height=peak_height_threshold, distance=peak_min_distance)
        peaks_g_indices, _ = find_peaks(avg_G_per_row, height=peak_height_threshold, distance=peak_min_distance)
        peaks_b_indices, _ = find_peaks(avg_B_per_row, height=peak_height_threshold, distance=peak_min_distance)

        return {
            "indices": row_indices,
            "avg_R": avg_R_per_row,
            "avg_G": avg_G_per_row,
            "avg_B": avg_B_per_row,
            # MODIFIED: Include peak data in the return dictionary
            "peaks_R": {"indices": peaks_r_indices, "heights": avg_R_per_row[peaks_r_indices]},
            "peaks_G": {"indices": peaks_g_indices, "heights": avg_G_per_row[peaks_g_indices]},
            "peaks_B": {"indices": peaks_b_indices, "heights": avg_B_per_row[peaks_b_indices]},
            "x_axis_label": "Row Index",
            "plot_title_suffix": "per Row"
        }
    except FileNotFoundError:
        # Error handling can be more sophisticated, e.g., logging
        # For now, returning None allows the GUI to handle user notification
        return None
    except Exception as e:
        # print(f"An error occurred during image processing: {e}") # Optional: for debugging
        return None

# The __main__ block from the original spectrum_analyser.py should be removed
# or adapted if you want to keep a command-line interface for this script,
# but it should not interfere with its use as a library.
# For this refactoring, we assume it's primarily a library module.