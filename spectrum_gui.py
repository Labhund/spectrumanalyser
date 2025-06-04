import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk # ImageTk for displaying image if needed, Image for processing
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os # To get basename of file for title

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
        self.drop_label_text = tk.StringVar(value="Drag and drop a .jpg file here")
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


        # Frame for the plot
        plot_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=1)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        # Matplotlib Figure and Axes
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Column Index')
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
        self.drop_label_text.set("Drag and drop a .jpg file here")
        event.widget.config(background=ttk.Style().lookup('TLabel', 'background'))


    def handle_drop(self, event):
        self.drop_label_text.set("Drag and drop a .jpg file here")
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

    def process_and_display_plot(self, image_path):
        try:
            # 1. Read the .jpg image
            img = Image.open(image_path)
            img_rgb = img.convert("RGB")
            img_array = np.array(img_rgb)

            # 2. Get arrays of the R, G, and B channels
            R_channel = img_array[:, :, 0]
            G_channel = img_array[:, :, 1]
            B_channel = img_array[:, :, 2]

            # 3. Calculate the average of each vertical column of pixels for each channel
            avg_R_per_column = np.mean(R_channel, axis=1)
            avg_G_per_column = np.mean(G_channel, axis=1)
            avg_B_per_column = np.mean(B_channel, axis=1)

            num_columns = img_array.shape[0]
            column_indices = np.arange(num_columns)

            # 4. Plot the averages on the existing Axes
            self.ax.clear() # Clear previous plot

            self.ax.plot(column_indices, avg_R_per_column, color='red', label='Red Channel Column Avg')
            self.ax.plot(column_indices, avg_G_per_column, color='green', label='Green Channel Column Avg')
            self.ax.plot(column_indices, avg_B_per_column, color='blue', label='Blue Channel Column Avg')

            self.ax.set_title(f'Average Pixel Value per Column\n{os.path.basename(image_path)}')
            self.ax.set_xlabel('Column Index')
            self.ax.set_ylabel('Average Pixel Value (0-255)')
            self.ax.legend()
            self.ax.grid(True)
            self.ax.invert_xaxis() # Invert x-axis

            self.fig.tight_layout() # Adjust plot to prevent labels from being cut off
            self.canvas.draw()

        except FileNotFoundError:
            messagebox.showerror("Error", f"The image file '{image_path}' was not found.")
            self.ax.clear()
            self.ax.set_title('Error loading image')
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {e}")
            self.ax.clear()
            self.ax.set_title('Error during processing')
            self.canvas.draw()

if __name__ == "__main__":
    app = SpectrumAnalyserApp()
    app.mainloop()