import tkinter as tk
from tkinter import ttk, messagebox, filedialog # MODIFIED: Added filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk # ImageTk for displaying image if needed, Image for processing
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os # To get basename of file for title
from image_processing import calculate_rgb_row_profiles # MODIFIED: Import the new backend function

class SpectrumAnalyserApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("JPG Spectrum Analyser")
        self.geometry("800x700")

        # Style
        style = ttk.Style(self)
        style.theme_use('clam') # Or 'alt', 'default', 'classic'

        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Drop target label
        self.drop_label_text = tk.StringVar(value="Drag and drop a .jpg file here, or click to browse") # MODIFIED text
        drop_target = ttk.Label(
            main_frame,
            textvariable=self.drop_label_text,
            relief="solid",
            padding="20",
            anchor=tk.CENTER,
            font=("Arial", 14)
        )
        drop_target.pack(fill=tk.X, pady=(0, 10))

        # Register the label as a drop target
        drop_target.drop_target_register(DND_FILES)
        drop_target.dnd_bind('<<Drop>>', self.handle_drop)
        drop_target.dnd_bind('<<DragEnter>>', self.handle_drag_enter)
        drop_target.dnd_bind('<<DragLeave>>', self.handle_drag_leave)
        drop_target.bind('<Button-1>', self.handle_click_to_browse) # MODIFIED: Added click binding


        # Frame for the plot
        plot_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=1)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        # Matplotlib Figure and Axes
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Row Index') # MODIFIED: Reflects row-based analysis
        self.ax.set_ylabel('Average Pixel Value (0-255)')
        self.ax.set_title('Plot will appear here')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Matplotlib Toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.current_image_path = None

    def handle_drag_enter(self, event):
        self.drop_label_text.set("Release to drop file...")
        event.widget.config(background="lightblue")


    def handle_drag_leave(self, event):
        self.drop_label_text.set("Drag and drop a .jpg file here, or click to browse") # MODIFIED text
        event.widget.config(background=ttk.Style().lookup('TLabel', 'background'))


    def handle_drop(self, event):
        self.drop_label_text.set("Drag and drop a .jpg file here, or click to browse") # MODIFIED text
        event.widget.config(background=ttk.Style().lookup('TLabel', 'background'))
        # event.data often comes with curly braces on some systems, clean it
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]

        if not file_path.lower().endswith(('.jpg', '.jpeg')):
            messagebox.showerror("Error", "Please drop a .jpg or .jpeg file.")
            return

        self.current_image_path = file_path
        self.process_and_display_plot(file_path)

    def handle_click_to_browse(self, event):
        """Handles click on the drop label to open a file dialog."""
        file_path = filedialog.askopenfilename(
            title="Select a JPG/JPEG image",
            filetypes=(("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*"))
        )
        if file_path: # If a file was selected
            if not file_path.lower().endswith(('.jpg', '.jpeg')):
                messagebox.showerror("Error", "Please select a .jpg or .jpeg file.")
                return
            self.current_image_path = file_path
            self.process_and_display_plot(file_path)
        # Reset label text in case it was changed by drag events
        self.drop_label_text.set("Drag and drop a .jpg file here, or click to browse")


    def process_and_display_plot(self, image_path):
        try:
            # Call the backend function from image_processing.py
            # Peak detection parameters from image_processing.py defaults will be used
            plot_data = calculate_rgb_row_profiles(image_path)

            if plot_data is None:
                messagebox.showerror("Error", f"Could not process image: {os.path.basename(image_path)}.\nFile might be missing or corrupted.")
                self.ax.clear()
                self.ax.set_title('Error processing image')
                self.ax.set_xlabel('Row Index') # Reset labels
                self.ax.set_ylabel('Average Pixel Value (0-255)')
                self.ax.grid(True)
                self.canvas.draw()
                return

            indices = plot_data["indices"]
            avg_R = plot_data["avg_R"]
            avg_G = plot_data["avg_G"]
            avg_B = plot_data["avg_B"]
            
            # MODIFIED: Get peak data
            peaks_R_data = plot_data["peaks_R"]
            peaks_G_data = plot_data["peaks_G"]
            peaks_B_data = plot_data["peaks_B"]

            x_axis_label = plot_data["x_axis_label"]
            plot_title_suffix = plot_data["plot_title_suffix"]

            self.ax.clear() # Clear previous plot

            self.ax.plot(indices, avg_R, color='red', label='Red Channel Avg')
            self.ax.plot(indices, avg_G, color='green', label='Green Channel Avg')
            self.ax.plot(indices, avg_B, color='blue', label='Blue Channel Avg')

            # MODIFIED: Annotate peaks
            peak_label_offset_points = 5 # Offset for the label text in points
            peak_marker_size = 5

            # Annotate Red channel peaks
            for i in range(len(peaks_R_data["indices"])):
                peak_idx = peaks_R_data["indices"][i] # This is the row index
                peak_hgt = peaks_R_data["heights"][i]
                self.ax.plot(peak_idx, peak_hgt, 'x', color='maroon', markersize=peak_marker_size) 
                self.ax.annotate(f'{peak_idx}', # Text to display (row index)
                                 xy=(peak_idx, peak_hgt), # Point to annotate
                                 xytext=(0, peak_label_offset_points), # Offset in points from the point
                                 textcoords='offset points',
                                 ha='center', va='bottom', # Alignment of text
                                 fontsize=8, color='maroon')

            # Annotate Green channel peaks
            for i in range(len(peaks_G_data["indices"])):
                peak_idx = peaks_G_data["indices"][i]
                peak_hgt = peaks_G_data["heights"][i]
                self.ax.plot(peak_idx, peak_hgt, 'x', color='darkgreen', markersize=peak_marker_size)
                self.ax.annotate(f'{peak_idx}',
                                 xy=(peak_idx, peak_hgt),
                                 xytext=(0, peak_label_offset_points),
                                 textcoords='offset points',
                                 ha='center', va='bottom',
                                 fontsize=8, color='darkgreen')

            # Annotate Blue channel peaks
            for i in range(len(peaks_B_data["indices"])):
                peak_idx = peaks_B_data["indices"][i]
                peak_hgt = peaks_B_data["heights"][i]
                self.ax.plot(peak_idx, peak_hgt, 'x', color='navy', markersize=peak_marker_size)
                self.ax.annotate(f'{peak_idx}',
                                 xy=(peak_idx, peak_hgt),
                                 xytext=(0, peak_label_offset_points),
                                 textcoords='offset points',
                                 ha='center', va='bottom',
                                 fontsize=8, color='navy')

            self.ax.set_title(f'Average Pixel Value {plot_title_suffix}\n{os.path.basename(image_path)}')
            self.ax.set_xlabel(x_axis_label)
            self.ax.set_ylabel('Average Pixel Value (0-255)')
            self.ax.legend()
            self.ax.grid(True)
            self.ax.invert_xaxis() # Keep original x-axis inversion

            self.fig.tight_layout() # Adjust plot to prevent labels from being cut off
            self.canvas.draw()

        except Exception as e: # Catch-all for unexpected issues in GUI part
            messagebox.showerror("Error", f"An unexpected error occurred in the GUI: {e}")
            self.ax.clear()
            self.ax.set_title('Unexpected GUI error')
            self.ax.set_xlabel('Row Index') # Reset labels
            self.ax.set_ylabel('Average Pixel Value (0-255)')
            self.ax.grid(True)
            self.canvas.draw()

if __name__ == "__main__":
    app = SpectrumAnalyserApp()
    app.mainloop()