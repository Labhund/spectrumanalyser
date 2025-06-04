import sys
from PIL import Image
import numpy as np

def analyze_slit_from_image(image_path: str, num_slit_rows: int):
    """
    Identifies the brightest horizontal rows in an image (the "slit") and
    extracts the R, G, B pixel values from these rows. Also determines the
    center row index of these selected rows.

    Args:
        image_path (str): Path to the JPG image file.
        num_slit_rows (int): The number of brightest rows to select as the slit.

    Returns:
        tuple: A tuple containing:
            - R_array (np.ndarray): 2D array of Red pixel values from slit rows.
                                    Shape: (num_slit_rows, image_width).
            - G_array (np.ndarray): 2D array of Green pixel values from slit rows.
                                    Shape: (num_slit_rows, image_width).
            - B_array (np.ndarray): 2D array of Blue pixel values from slit rows.
                                    Shape: (num_slit_rows, image_width).
            - slit_row_indices (np.ndarray): 1D array of the actual row indices
                                             in the original image that were selected,
                                             sorted by their original row index.
            - center_row_idx (int or None): The median index of the selected slit rows.
                                            Returns None for all if an error occurs.
    """
    try:
        # 1. Load the image
        img = Image.open(image_path)
        # Ensure it's RGB (handles various image modes like RGBA, L, etc.)
        img_rgb = img.convert("RGB")
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None, None, None, None, None
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None, None, None, None

    # 2. Convert to NumPy array
    # Image data will be (height, width, channels)
    image_data = np.array(img_rgb)
    height, width, _ = image_data.shape

    if num_slit_rows <= 0:
        print("Error: num_slit_rows must be positive.")
        return None, None, None, None, None
    
    actual_num_rows_to_select = min(num_slit_rows, height)
    if num_slit_rows > height:
        print(f"Warning: num_slit_rows ({num_slit_rows}) is greater than image height ({height})."
              f" Using all {height} rows.")


    # 3. Calculate row brightness
    # Sum R, G, B for each pixel, then sum these brightnesses for all pixels in a row.
    # Using a higher precision dtype for sum to prevent overflow with large images/bright pixels.
    row_brightnesses = np.sum(image_data, axis=(1, 2), dtype=np.uint64)

    # 4. Find indices of top actual_num_rows_to_select
    # np.argsort sorts in ascending order; we take the last 'actual_num_rows_to_select'
    # indices, which correspond to the rows with the highest brightness.
    if len(row_brightnesses) == 0: # Should not happen if image loaded
        print("Error: Image data is empty.")
        return None, None, None, None, None
        
    top_row_indices = np.argsort(row_brightnesses)[-actual_num_rows_to_select:]

    # Sort these selected indices by their original row number.
    # This ensures R_array[0] corresponds to the uppermost selected slit row, etc.
    slit_row_indices_sorted = np.sort(top_row_indices)

    # 5. Initialize R, G, B arrays
    # Shape: (actual_num_rows_to_select, image_width)
    R_array = np.zeros((len(slit_row_indices_sorted), width), dtype=np.uint8)
    G_array = np.zeros((len(slit_row_indices_sorted), width), dtype=np.uint8)
    B_array = np.zeros((len(slit_row_indices_sorted), width), dtype=np.uint8)

    # 6. Populate arrays with pixel data from the selected slit rows
    for i, original_row_idx in enumerate(slit_row_indices_sorted):
        R_array[i, :] = image_data[original_row_idx, :, 0] # Red channel
        G_array[i, :] = image_data[original_row_idx, :, 1] # Green channel
        B_array[i, :] = image_data[original_row_idx, :, 2] # Blue channel

    # 7. Calculate center row index
    center_row_idx = None
    if len(slit_row_indices_sorted) > 0:
        center_row_idx = int(np.median(slit_row_indices_sorted))

    return R_array, G_array, B_array, slit_row_indices_sorted, center_row_idx

def analyze_diffraction_pattern(image_path: str, num_slit_rows_for_center: int, analysis_band_height: int):
    """
    Analyzes the diffraction pattern in an image by:
    1. Finding the center of the main slit (brightest region).
    2. Defining a horizontal band of rows around this center.
    3. Extracting RGB data from this band.

    Args:
        image_path (str): Path to the image file.
        num_slit_rows_for_center (int): How many brightest rows to use to find the slit center.
        analysis_band_height (int): The total height (number of rows) of the band
                                     around the center to analyze for the diffraction pattern.
                                     Should be an odd number for symmetry, but will be adjusted.

    Returns:
        tuple: A tuple containing:
            - R_band_array (np.ndarray): 2D array of Red pixel values from the analysis band.
            - G_band_array (np.ndarray): 2D array of Green pixel values from the analysis band.
            - B_band_array (np.ndarray): 2D array of Blue pixel values from the analysis band.
            - band_row_indices (np.ndarray): 1D array of the actual row indices in the band.
                                             Returns None for all if an error occurs.
    """
    # 1. Find the center of the slit
    # The analyze_slit_from_image now returns 5 values including center_row_idx
    _, _, _, slit_indices, center_row_idx = analyze_slit_from_image(image_path, num_slit_rows_for_center)

    if center_row_idx is None:
        print("Error: Could not determine slit center.")
        return None, None, None, None

    print(f"Determined slit center around row index: {center_row_idx}")

    # 2. Define the analysis band
    try:
        # Reload image data (could be optimized by passing image_data if needed)
        img = Image.open(image_path)
        img_rgb = img.convert("RGB")
        image_data = np.array(img_rgb)
        height, width, _ = image_data.shape
    except Exception as e:
        print(f"Error reloading image for band analysis: {e}")
        return None, None, None, None

    # Ensure band height is reasonable
    analysis_band_height = max(1, int(analysis_band_height)) # Must be at least 1
    half_band = analysis_band_height // 2

    # Calculate start and end row indices for the band, clamping to image boundaries
    start_row = max(0, center_row_idx - half_band)
    # Adjust end_row calculation for even/odd heights to get the desired total height
    end_row = min(height, start_row + analysis_band_height)
    # Recalculate start_row if end_row hit the boundary and the band is too short
    start_row = max(0, end_row - analysis_band_height)

    actual_band_height = end_row - start_row
    if actual_band_height <= 0:
        print(f"Error: Calculated analysis band has zero or negative height (start: {start_row}, end: {end_row}).")
        return None, None, None, None

    band_row_indices = np.arange(start_row, end_row)
    print(f"Analyzing band from row {start_row} to {end_row-1} (height: {actual_band_height})")

    # 3. Extract RGB data from the band
    R_band_array = np.zeros((actual_band_height, width), dtype=np.uint8)
    G_band_array = np.zeros((actual_band_height, width), dtype=np.uint8)
    B_band_array = np.zeros((actual_band_height, width), dtype=np.uint8)

    for i, original_row_idx in enumerate(band_row_indices):
        R_band_array[i, :] = image_data[original_row_idx, :, 0]
        G_band_array[i, :] = image_data[original_row_idx, :, 1]
        B_band_array[i, :] = image_data[original_row_idx, :, 2]

    return R_band_array, G_band_array, B_band_array, band_row_indices

# --- Example Usage (Updated) ---
if __name__ == "__main__":
    # --- Parameters ---
    # For finding slit center:
    num_rows_for_slit_center = 5
    # For analyzing diffraction pattern:
    diffraction_band_height = 21 # How many rows tall the analysis band should be (centered on slit)

    image_file_to_analyze = ""
    # --- End Parameters ---

    if len(sys.argv) > 1:
        image_file_to_analyze = sys.argv[1]
        print(f"Image from command line: {image_file_to_analyze}")
    else:
        print("Usage: python makearrays.py <path_to_your_image.jpg>")
        # Removed dummy image creation for clarity, assuming user provides path
        sys.exit(1)

    print("\n--- Analyzing Slit Center ---")
    # analyze_slit_from_image now returns 5 values
    R_slit, G_slit, B_slit, slit_idxs, median_idx = analyze_slit_from_image(
        image_file_to_analyze,
        num_rows_for_slit_center
    )
    if median_idx is not None:
        print(f"Found slit center around row: {median_idx} using {len(slit_idxs)} brightest rows.")
    else:
        print("Failed to find slit center.")
        sys.exit(1)

    print("\n--- Analyzing Diffraction Pattern Band ---")
    R_diff, G_diff, B_diff, band_idxs = analyze_diffraction_pattern(
        image_file_to_analyze,
        num_rows_for_slit_center, # Use same value to find center again
        diffraction_band_height
    )

    if R_diff is not None:
        print(f"\nSuccessfully extracted diffraction band data.")
        print(f"Analyzed rows: {band_idxs}")
        print(f"Shape of R_band_array: {R_diff.shape}")
        print(f"Shape of G_band_array: {G_diff.shape}")
        print(f"Shape of B_band_array: {B_diff.shape}")

        if len(band_idxs) > 0 and R_diff.shape[1] > 5:
             print("\nExample: R,G,B values for the first 5 pixels of the central row of the band:")
             center_band_row_relative_idx = R_diff.shape[0] // 2
             for col_idx in range(5):
                 print(f"  Pixel {col_idx}: R={R_diff[center_band_row_relative_idx, col_idx]}, "
                       f"G={G_diff[center_band_row_relative_idx, col_idx]}, "
                       f"B={B_diff[center_band_row_relative_idx, col_idx]}")
    else:
        print("Failed to analyze diffraction band.")