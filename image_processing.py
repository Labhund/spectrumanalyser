from PIL import Image
import numpy as np
# Removed: import matplotlib.pyplot as plt
# Removed: import sys

def calculate_rgb_row_profiles(image_path):
    """
    Reads a JPG image, extracts R, G, B channels, and calculates the average
    pixel value for each horizontal row for each channel.

    Args:
        image_path (str): The path to the JPG image file.

    Returns:
        dict: A dictionary containing the processed data:
              {
                  "indices": numpy.ndarray (row indices),
                  "avg_R": numpy.ndarray (average red values per row),
                  "avg_G": numpy.ndarray (average green values per row),
                  "avg_B": numpy.ndarray (average blue values per row),
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

        return {
            "indices": row_indices,
            "avg_R": avg_R_per_row,
            "avg_G": avg_G_per_row,
            "avg_B": avg_B_per_row,
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