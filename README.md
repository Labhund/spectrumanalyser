# JPG Spectrum Analyser

A simple Python application that displays the average Red, Green, and Blue (RGB) channel values for each row of a JPG image. Users can drag and drop a JPG file onto the application window to generate and view the spectrum plot.

## Features

*   Drag and drop interface for JPG/JPEG files.
*   Calculates and plots the average pixel value for R, G, and B channels per row.
*   Detects peaks in each color channel.
*   Automatically identifies the zero-order diffraction peak based on the highest intensity peak.
*   Allows users to infer pixel size by inputting a known physical distance on the sensor between the zero-order peak and another peak, along with the corresponding pixel indices.
*   Calculates and displays wavelengths for detected peaks.
*   Adjustable peak detection parameters (height threshold, minimum distance).
*   Adjustable spectrometer parameters (grating lines/mm, grating-to-sensor distance, pixel size).
*   Uses Tkinter for the GUI and Matplotlib for plotting.
*   Clear separation of image processing, spectrometry calculations, and GUI logic.

## Directory Structure

```
spectrumanalyser/
├── src/
│   ├── spectrum_gui.py        # Main Tkinter GUI application
│   ├── image_processing.py    # Backend image processing logic
│   └── spectrometry_calculations.py # Backend spectrometry calculation logic
├── examples/
│   └── IMG_5301.jpg         # Example image
├── requirements.txt       # Python package dependencies
└── README.md              # This file
```

## Prerequisites

*   Python 3.7 or newer
*   pip (Python package installer)

## Installation

1.  **Clone the repository or download the files.**

2.  **Navigate to the project directory:**
    ```bash
    cd path/to/spectrumanalyser
    ```

3.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

Execute the main GUI script from the root `spectrumanalyser` directory:

```bash
python src/spectrum_gui.py
```

Drag and drop a `.jpg` or `.jpeg` file (like the one in the `examples/` folder) onto the designated area in the application window to see the spectrum plot.

## Screenshots

### Main Interface
![Main Interface](screenshots/interface_demo.png)

### Analysis Settings
![Settings Panel](screenshots/settings_demo.png)

## Example input
![Settings Panel](examples/IMG_5301.jpg)

## Dependencies

The project relies on the following Python libraries:

*   **Pillow**: For image manipulation (opening and processing JPG files).
*   **NumPy**: For numerical operations, especially array handling for pixel data.
*   **Matplotlib**: For creating and embedding plots in the GUI.
*   **TkinterDnD2**: To enable drag-and-drop functionality in Tkinter.
*   **SciPy**: For scientific computing, specifically `find_peaks` for peak detection.
*   **Tkinter**: (Usually included with Python) For the graphical user interface.
