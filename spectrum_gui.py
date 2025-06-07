import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
from image_processing import calculate_rgb_row_profiles, DEFAULT_PEAK_HEIGHT_THRESHOLD, DEFAULT_PEAK_MIN_DISTANCE
# MODIFIED: Import calculation functions
from spectrometry_calculations import calculate_wavelength_nm, grating_spacing_from_lines_per_mm

class SpectrumAnalyserApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("JPG Spectrum Analyser")
        self.geometry("800x850") # Increased height for more settings

        # Peak detection parameters
        self.peak_height_var = tk.DoubleVar(value=DEFAULT_PEAK_HEIGHT_THRESHOLD)
        self.peak_distance_var = tk.IntVar(value=DEFAULT_PEAK_MIN_DISTANCE)
        self.current_height_label_var = tk.StringVar(value=f"{self.peak_height_var.get():.1f}")
        self.current_distance_label_var = tk.StringVar(value=f"{self.peak_distance_var.get():.0f}")

        # MODIFIED: Spectrometer physical parameters
        self.lines_per_mm_var = tk.DoubleVar(value=600.0) # Example default
        self.distance_L_mm_var = tk.DoubleVar(value=100.0) # Example default, L in mm
        self.pixel_size_um_var = tk.DoubleVar(value=2.0)  # Example default, pixel size in micrometers
        self.zero_order_pixel_var = tk.IntVar(value=0) # User needs to set this, e.g. from plot
        
        self.current_lines_mm_label_var = tk.StringVar(value=f"{self.lines_per_mm_var.get():.0f}")
        self.current_distance_L_label_var = tk.StringVar(value=f"{self.distance_L_mm_var.get():.1f}")
        self.current_pixel_size_label_var = tk.StringVar(value=f"{self.pixel_size_um_var.get():.2f}")
        self.current_zero_order_label_var = tk.StringVar(value=f"{self.zero_order_pixel_var.get()}")


        # Style
        style = ttk.Style(self)
        style.theme_use('clam')

        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Drop target label
        self.drop_label_text = tk.StringVar(value="Drag and drop a .jpg file here, or click to browse")
        drop_target = ttk.Label(
            main_frame,
            textvariable=self.drop_label_text,
            relief="solid",
            padding="20",
            anchor=tk.CENTER,
            font=("Arial", 14)
        )
        drop_target.pack(fill=tk.X, pady=(0, 5)) # Reduced bottom pady

        # Register the label as a drop target
        drop_target.drop_target_register(DND_FILES)
        drop_target.dnd_bind('<<Drop>>', self.handle_drop)
        drop_target.dnd_bind('<<DragEnter>>', self.handle_drag_enter)
        drop_target.dnd_bind('<<DragLeave>>', self.handle_drag_leave)
        drop_target.bind('<Button-1>', self.handle_click_to_browse)

        # MODIFIED: Settings button to toggle sliders (now "Analysis Settings")
        self.settings_button = ttk.Button(main_frame, text="\u2630 Analysis Settings", command=self.toggle_settings_visibility)
        self.settings_button.pack(fill=tk.X, pady=(0,5))

        # MODIFIED: Frame for sliders and settings (initially hidden)
        self.settings_frame = ttk.Frame(main_frame, padding="5", relief="groove", borderwidth=1)
        
        # Populate settings_frame - Peak Settings
        peak_settings_label = ttk.Label(self.settings_frame, text="Peak Detection:", font=("Arial", 10, "bold"))
        peak_settings_label.grid(row=0, column=0, columnspan=3, padx=5, pady=(5,2), sticky="w")

        ttk.Label(self.settings_frame, text="Height Thresh:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
        height_slider = ttk.Scale(self.settings_frame, from_=0.1, to=50.0, orient=tk.HORIZONTAL, length=180, variable=self.peak_height_var, command=self.on_settings_changed)
        height_slider.grid(row=1, column=1, padx=5, pady=3, sticky="ew")
        ttk.Label(self.settings_frame, textvariable=self.current_height_label_var, width=5).grid(row=1, column=2, padx=5, pady=3, sticky="w")

        ttk.Label(self.settings_frame, text="Min Distance:").grid(row=2, column=0, padx=5, pady=3, sticky="w")
        distance_slider = ttk.Scale(self.settings_frame, from_=1, to=1000, orient=tk.HORIZONTAL, length=180, variable=self.peak_distance_var, command=self.on_settings_changed)
        distance_slider.grid(row=2, column=1, padx=5, pady=3, sticky="ew")
        ttk.Label(self.settings_frame, textvariable=self.current_distance_label_var, width=5).grid(row=2, column=2, padx=5, pady=3, sticky="w")

        # MODIFIED: Populate settings_frame - Spectrometer Settings
        spec_settings_label = ttk.Label(self.settings_frame, text="Spectrometer Parameters:", font=("Arial", 10, "bold"))
        spec_settings_label.grid(row=3, column=0, columnspan=3, padx=5, pady=(10,2), sticky="w")
        
        ttk.Label(self.settings_frame, text="Grating (lines/mm):").grid(row=4, column=0, padx=5, pady=3, sticky="w")
        lines_entry = ttk.Entry(self.settings_frame, textvariable=self.lines_per_mm_var, width=8)
        lines_entry.grid(row=4, column=1, padx=5, pady=3, sticky="w")
        lines_entry.bind("<Return>", self.on_settings_changed)
        lines_entry.bind("<FocusOut>", self.on_settings_changed)
        ttk.Label(self.settings_frame, textvariable=self.current_lines_mm_label_var, width=5).grid(row=4, column=2, padx=5, pady=3, sticky="w")


        ttk.Label(self.settings_frame, text="L (grating-sensor, mm):").grid(row=5, column=0, padx=5, pady=3, sticky="w")
        distance_L_entry = ttk.Entry(self.settings_frame, textvariable=self.distance_L_mm_var, width=8)
        distance_L_entry.grid(row=5, column=1, padx=5, pady=3, sticky="w")
        distance_L_entry.bind("<Return>", self.on_settings_changed)
        distance_L_entry.bind("<FocusOut>", self.on_settings_changed)
        ttk.Label(self.settings_frame, textvariable=self.current_distance_L_label_var, width=5).grid(row=5, column=2, padx=5, pady=3, sticky="w")

        ttk.Label(self.settings_frame, text="Pixel Size (µm):").grid(row=6, column=0, padx=5, pady=3, sticky="w")
        pixel_size_entry = ttk.Entry(self.settings_frame, textvariable=self.pixel_size_um_var, width=8)
        pixel_size_entry.grid(row=6, column=1, padx=5, pady=3, sticky="w")
        pixel_size_entry.bind("<Return>", self.on_settings_changed)
        pixel_size_entry.bind("<FocusOut>", self.on_settings_changed)
        ttk.Label(self.settings_frame, textvariable=self.current_pixel_size_label_var, width=5).grid(row=6, column=2, padx=5, pady=3, sticky="w")

        ttk.Label(self.settings_frame, text="Zero-Order Peak (pixel row):").grid(row=7, column=0, padx=5, pady=3, sticky="w")
        zero_order_entry = ttk.Entry(self.settings_frame, textvariable=self.zero_order_pixel_var, width=8)
        zero_order_entry.grid(row=7, column=1, padx=5, pady=3, sticky="w")
        zero_order_entry.bind("<Return>", self.on_settings_changed)
        zero_order_entry.bind("<FocusOut>", self.on_settings_changed)
        ttk.Label(self.settings_frame, textvariable=self.current_zero_order_label_var, width=5).grid(row=7, column=2, padx=5, pady=3, sticky="w")
        
        self.settings_frame.columnconfigure(1, weight=1) # Make middle column expandable

        # Frame for the plot
        self.plot_frame_ref = ttk.Frame(main_frame, relief="sunken", borderwidth=1) # Stored reference
        self.plot_frame_ref.pack(fill=tk.BOTH, expand=True)

        # Matplotlib Figure and Axes
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Row Index') # MODIFIED: Reflects row-based analysis
        self.ax.set_ylabel('Average Pixel Value (0-255)')
        self.ax.set_title('Plot will appear here')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame_ref) # Use self.plot_frame_ref
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Matplotlib Toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame_ref) # Use self.plot_frame_ref
        toolbar.update()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) # This was duplicated, removed one

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

    # MODIFIED: Method to toggle settings visibility
    def toggle_settings_visibility(self):
        if self.settings_frame.winfo_ismapped():
            self.settings_frame.pack_forget()
            self.settings_button.config(text="\Analysis Settings")
        else:
            self.settings_frame.pack(fill=tk.X, pady=5, before=self.plot_frame_ref)
            self.settings_button.config(text="\Analysis Settings")


    # MODIFIED: Callback for when any settings change
    def on_settings_changed(self, event_or_slider_value=None):
        # Update display labels from the Tkinter variables
        try:
            self.current_height_label_var.set(f"{self.peak_height_var.get():.1f}")
            self.current_distance_label_var.set(f"{self.peak_distance_var.get():.0f}")
            self.current_lines_mm_label_var.set(f"{self.lines_per_mm_var.get():.0f}")
            self.current_distance_L_label_var.set(f"{self.distance_L_mm_var.get():.1f}")
            self.current_pixel_size_label_var.set(f"{self.pixel_size_um_var.get():.2f}")
            self.current_zero_order_label_var.set(f"{self.zero_order_pixel_var.get()}")
        except tk.TclError:
            # Can happen if entry field has invalid text during typing
            pass # Values will update on FocusOut or Return

        if self.current_image_path:
            self.process_and_display_plot(self.current_image_path)


    def process_and_display_plot(self, image_path):
        try:
            # Peak detection parameters
            current_peak_height = self.peak_height_var.get()
            current_peak_distance = self.peak_distance_var.get()

            # Spectrometer parameters
            lines_per_mm = self.lines_per_mm_var.get()
            L_mm = self.distance_L_mm_var.get()
            pixel_size_um = self.pixel_size_um_var.get()
            zero_order_pix = self.zero_order_pixel_var.get()

            # Convert to meters for calculation
            d_meters = grating_spacing_from_lines_per_mm(lines_per_mm)
            L_meters = L_mm / 1000.0 if L_mm is not None else None
            pixel_scale_m_px = pixel_size_um / 1e6 if pixel_size_um is not None else None
            
            # Perform image processing to get peaks
            plot_data = calculate_rgb_row_profiles(
                image_path,
                peak_height_threshold=current_peak_height,
                peak_min_distance=current_peak_distance
            )

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

            # MODIFIED: Annotate peaks with pixel index and wavelength
            peak_label_offset_points = 5 
            peak_marker_size = 5

            # Helper function for annotation
            def annotate_channel_peaks(peaks_data, channel_color, channel_name):
                for i in range(len(peaks_data["indices"])):
                    peak_idx = peaks_data["indices"][i]
                    peak_hgt = peaks_data["heights"][i]
                    
                    wavelength = None
                    if d_meters and L_meters and pixel_scale_m_px and zero_order_pix is not None:
                        wavelength = calculate_wavelength_nm(
                            peak_pixel_index=peak_idx,
                            zero_order_pixel_index=zero_order_pix,
                            L_meters=L_meters,
                            d_meters=d_meters,
                            pixel_scale_meters_per_pixel=pixel_scale_m_px
                        )
                    
                    annotation_text = f'{peak_idx}'
                    if wavelength is not None:
                        annotation_text += f'\n{wavelength:.0f} nm'
                    
                    self.ax.plot(peak_idx, peak_hgt, 'x', color=channel_color, markersize=peak_marker_size)
                    self.ax.annotate(annotation_text,
                                     xy=(peak_idx, peak_hgt),
                                     xytext=(0, peak_label_offset_points),
                                     textcoords='offset points',
                                     ha='center', va='bottom',
                                     fontsize=7, color=channel_color,
                                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7))


            annotate_channel_peaks(peaks_R_data, 'maroon', 'R')
            annotate_channel_peaks(peaks_G_data, 'darkgreen', 'G')
            annotate_channel_peaks(peaks_B_data, 'navy', 'B')

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