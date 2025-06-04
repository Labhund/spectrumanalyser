from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import sys  # Add this import at the top of your file

def plot_channel_column_averages(image_path):
    """
    Reads a JPG image, extracts R, G, B channels, calculates the average
    of each vertical column for each channel, and plots these averages.
    """
    try:
        # 1. Read the .jpg image
        img = Image.open(image_path)
        # Ensure the image is in RGB format
        img_rgb = img.convert("RGB")
        img_array = np.array(img_rgb)

        # 2. Get arrays of the R, G, and B channels
        # R_channel is a 2D array of red values for all pixels
        # G_channel is a 2D array of green values for all pixels
        # B_channel is a 2D array of blue values for all pixels
        R_channel = img_array[:, :, 0]
        G_channel = img_array[:, :, 1]
        B_channel = img_array[:, :, 2]

        # 3. Calculate the average of each vertical column of pixels for each channel
        # np.mean(axis=0) calculates the mean along the columns (downwards)
        avg_R_per_column = np.mean(R_channel, axis=1)
        avg_G_per_column = np.mean(G_channel, axis=1)
        avg_B_per_column = np.mean(B_channel, axis=1)

        # 4. Plot the averages
        num_columns = img_array.shape[0]
        column_indices = np.arange(num_columns)

        plt.figure(figsize=(12, 7))

        plt.plot(column_indices, avg_R_per_column, color='red', label='Red Channel Column Average')
        plt.plot(column_indices, avg_G_per_column, color='green', label='Green Channel Column Average')
        plt.plot(column_indices, avg_B_per_column, color='blue', label='Blue Channel Column Average')

        plt.title(f'Average Pixel Value per Column for RGB Channels\nImage: {image_path}')
        plt.xlabel('Column Index')
        plt.ylabel('Average Pixel Value (0-255)')
        plt.legend()
        plt.grid(True)
        plt.gca().invert_xaxis()  # Invert x-axis to match the image's left-to-right orientation
        plt.tight_layout()
        plt.show()

        # The R_channel, G_channel, B_channel arrays are available here if needed
        # For example, to print the shape of the Red channel array:
        # print(f"Red channel array shape: {R_channel.shape}")


    except FileNotFoundError:
        print(f"Error: The image file '{image_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_file_path = sys.argv[1]  # Use the first command-line argument as the image path
    else:
        # Default or error if no path is provided
        print("Error: No image path provided. Please run the script with an image path argument.")
        print("Usage: python spectrum_analyser.py <path_to_your_image.jpg>")
        # You might want to set a default image or exit here
        image_file_path = "your_image.jpg"  # Or sys.exit(1) to stop execution

    plot_channel_column_averages(image_file_path)
    print(f"Processing complete for {image_file_path}. If a plot window appeared, close it to exit.")
    if image_file_path == "your_image.jpg" and len(sys.argv) <= 1:
        print("Ensure you have an image file at the specified path or provide one as a command line argument.")