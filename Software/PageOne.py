import os
import pydicom
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DicomViewerPage1(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg='#323232')

        # Set window properties for page 1
        self.master = master
        self.dicom_data = None
        self.vol_data = None
        self.middle_slice_idx = 0
        self.rectangle = None
        self.fig, self.ax = plt.subplots(figsize=(7, 6))
        self.fig.patch.set_facecolor('#323232')
        self.ax.set_facecolor('#424242')

        self.create_widgets()

    def create_widgets(self):
        # Frame for browse buttons
        browse_frame = tk.Frame(self, bg='#323232')
        browse_frame.pack(pady=35)

        # Single DICOM Browse button
        self.single_browse_btn = tk.Button(browse_frame,
                                           text="Single DICOM",
                                           command=self.load_single,
                                           bg="#555555",
                                           fg="white",
                                           font=("Helvetica", 14, "bold"),
                                           relief="groove",
                                           padx=10,
                                           pady=10)
        self.single_browse_btn.pack(side="left", padx=10)

        # Multiple DICOM Browse button
        self.multi_browse_btn = tk.Button(browse_frame,
                                          text="Multiple DICOM",
                                          command=self.load_multi,
                                          bg="#555555",
                                          fg="white",
                                          font=("Helvetica", 14, "bold"),
                                          relief="groove",
                                          padx=10,
                                          pady=10)
        self.multi_browse_btn.pack(side="left", padx=10)

        # Frame for canvas and scrollbar
        self.canvas_frame = tk.Frame(self, bg='#323232')
        self.canvas_frame.pack(pady=10)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.scroll_image)
        self.scrollbar.pack(side="right", fill="y")

        # Matplotlib canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

        # Frame for buttons
        button_frame = tk.Frame(self, bg='#323232')
        button_frame.pack(pady=20)

        # Next button
        self.next_btn = tk.Button(button_frame,
                                  text="Next",
                                  command=self.go_next,
                                  bg="#555555",
                                  fg="white",
                                  font=("Helvetica", 14, "bold"),
                                  relief="groove",
                                  padx=10,
                                  pady=10)
        self.next_btn.pack(side="left", padx=10)

        # Reset button (beside the Next button)
        self.reset_btn = tk.Button(button_frame,
                                   text="Reset",
                                   command=self.reset_drawing,
                                   bg="#555555",
                                   fg="white",
                                   font=("Helvetica", 14, "bold"),
                                   relief="groove",
                                   padx=10,
                                   pady=10)
        self.reset_btn.pack(side="left", padx=10)

        # Bind rectangle drawing
        self.drawing_rectangle = False
        self.rectangle = None
        self.canvas.mpl_connect("button_press_event", self.start_rectangle)
        self.canvas.mpl_connect("motion_notify_event", self.update_rectangle)
        self.canvas.mpl_connect("button_release_event", self.finalize_rectangle)

    def reset_drawing(self):
        """Reset the drawing by clearing the rectangle."""
        if self.rectangle:
            self.rectangle.remove()  # Remove the current rectangle patch
            self.rectangle = None  # Reset the rectangle variable

        # Redraw the canvas to reflect the cleared drawing
        self.canvas.draw()

    def load_single(self):
        """Load the DICOM file and display the initial slice."""
        dicom_path = filedialog.askopenfilename(filetypes=[("DICOM Files", "*.dcm")])
        if not dicom_path:
            return

        # Load DICOM data
        self.dicom_data = pydicom.dcmread(dicom_path)
        self.vol_data = self.dicom_data.pixel_array
        self.middle_slice_idx = self.vol_data.shape[0] // 2

        # Configure scrollbar
        self.scrollbar.config(command=self.scroll_image)
        self.scrollbar.set(self.middle_slice_idx / (self.vol_data.shape[0] - 1),
                           (self.middle_slice_idx + 1) / (self.vol_data.shape[0] - 1))

        # Display initial slice
        self.update_image()

    def load_multi(self):
        """Load a folder of DICOM files and create a 3D volume."""
        dicom_folder = filedialog.askdirectory()
        if not dicom_folder:
            return

        # Show a message to wait
        wait_message = tk.Label(self.master, text="Please wait... Loading files.",
                                fg="red", font=("Arial", 20, "bold"))
        wait_message.place(relx=0.5, rely=0.5, anchor="center")  # Center the message
        self.master.update()  # Force update to show the message

        slices = []
        for file in os.listdir(dicom_folder):
            file_path = os.path.join(dicom_folder, file)

            dcom_data = pydicom.dcmread(file_path)
            if len(dcom_data.pixel_array.shape) == 2:
                instance_number = int(dcom_data.InstanceNumber)
                slices.append((instance_number, dcom_data.pixel_array))

        slices = sorted(slices, key=lambda x: x[0])
        sorted_pixel_arrays = [slice[1] for slice in slices]
        self.vol_data = np.stack(sorted_pixel_arrays, axis=0)
        self.middle_slice_idx = self.vol_data.shape[0] // 2

        # Configure scrollbar
        self.scrollbar.config(command=self.scroll_image)
        self.scrollbar.set(self.middle_slice_idx / (self.vol_data.shape[0] - 1),
                           (self.middle_slice_idx + 1) / (self.vol_data.shape[0] - 1))

        # Display initial slice
        self.update_image()

        # Remove the wait message
        wait_message.destroy()
        self.master.update()

    def scroll_image(self, *args):
        """Update the slice index and replot the image."""
        if self.vol_data is not None:
            if args[0] == "moveto":
                # Adjust index based on scrollbar position
                fraction = float(args[1])
                self.middle_slice_idx = int(fraction * (self.vol_data.shape[0] - 1))
            elif args[0] == "scroll":
                # Adjust index based on scroll amount
                step = int(args[1])
                self.middle_slice_idx = max(0, min(self.middle_slice_idx + step, self.vol_data.shape[0] - 1))

            # Update scrollbar position
            self.scrollbar.set(self.middle_slice_idx / (self.vol_data.shape[0] - 1),
                               (self.middle_slice_idx + 1) / (self.vol_data.shape[0] - 1))

            self.update_image()

    def update_image(self):
        """Update the displayed image based on the current slice index."""
        if self.vol_data is not None:
            middle_slice = self.vol_data[self.middle_slice_idx, :, :]
            self.ax.clear()
            self.ax.imshow(middle_slice, cmap="gray")
            self.ax.set_xticks([])  # Remove x-axis ticks
            self.ax.set_yticks([])  # Remove y-axis ticks

            if self.rectangle:
                self.ax.add_patch(self.rectangle)

            self.canvas.draw()

    def start_rectangle(self, event):
        """Start drawing a rectangle."""
        if event.inaxes:
            # Check if a rectangle already exists, prevent drawing a new one
            if self.rectangle is not None:
                print("A rectangle already exists. Reset before drawing a new one.")
                return

            self.drawing_rectangle = True  # Set flag to indicate drawing has started
            self.rect_start = (event.xdata, event.ydata)
            self.rectangle = Rectangle(self.rect_start, 0, 0, edgecolor='red', facecolor='none', linewidth=2)
            self.ax.add_patch(self.rectangle)

    def update_rectangle(self, event):
        """Update the rectangle while the mouse is being dragged."""
        if self.drawing_rectangle and event.inaxes:
            x0, y0 = self.rect_start
            x1, y1 = event.xdata, event.ydata
            self.rectangle.set_width(x1 - x0)
            self.rectangle.set_height(y1 - y0)
            self.rectangle.set_xy((min(x0, x1), min(y0, y1)))
            self.canvas.draw()

    def finalize_rectangle(self, event):
        """Finalize the rectangle when the mouse is released."""
        if self.drawing_rectangle and event.inaxes:
            self.rect_end = (event.xdata, event.ydata)
            print(f"Rectangle finalized from {self.rect_start} to {self.rect_end}")
            self.drawing_rectangle = False

    def go_next(self):
        """Go to the next page (Page 2)."""
        self.master.show_page_2(self.vol_data, self.rect_start, self.rect_end)
