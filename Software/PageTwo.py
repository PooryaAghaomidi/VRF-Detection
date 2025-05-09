import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DicomViewerPage2(tk.Frame):
    def __init__(self, master, vol_data):
        super().__init__(master)

        self.configure(bg='#323232')
        self.vol_data = vol_data
        self.middle_slice_idx = 0
        self.rectangle = None

        self.fig, self.ax = plt.subplots(figsize=(7, 6))
        self.fig.patch.set_facecolor('#323232')
        self.ax.set_facecolor('#424242')

        self.create_widgets()

    def create_widgets(self):
        """Create all UI components for Page 2"""
        # Draw on: Left or Right
        self.view_frame = tk.Frame(self, bg='#323232')
        self.view_frame.pack(pady=20)

        self.draw_label = tk.Label(self.view_frame, text="Draw on:", bg='#323232', fg="white", font=("Helvetica", 14, "bold"))
        self.draw_label.pack(side="left", padx=10)

        # Create the two radio buttons (options)
        self.var = tk.IntVar()
        radio_left = tk.Radiobutton(self.view_frame, text="Left", variable=self.var, command=self.init_image, value=1, selectcolor="black", bg="#323232", fg="white", font=("Helvetica", 14, "bold"))
        radio_left.pack(side="left", padx=10)

        radio_right = tk.Radiobutton(self.view_frame, text="Right", variable=self.var, command=self.init_image, value=2, selectcolor="black", bg="#323232", fg="white", font=("Helvetica", 14, "bold"))
        radio_right.pack(side="left", padx=10)

        # Frame for canvas and scrollbar
        self.canvas_frame = tk.Frame(self, bg='#323232')
        self.canvas_frame.pack(pady=10)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.scroll_image)
        self.scrollbar.pack(side="right", fill="y")

        # Matplotlib canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

        # Buttons: Previous, Reset, and Next
        button_frame = tk.Frame(self, bg='#323232')
        button_frame.pack(pady=20)

        self.prev_btn = tk.Button(button_frame, text="Previous", command=self.go_previous, bg="#555555", fg="white",
                                  font=("Helvetica", 14, "bold"), relief="groove", padx=10, pady=10)
        self.prev_btn.pack(side="left", padx=10)

        self.reset_btn = tk.Button(button_frame, text="Reset", command=self.reset_drawing, bg="#555555", fg="white",
                                   font=("Helvetica", 14, "bold"), relief="groove", padx=10, pady=10)
        self.reset_btn.pack(side="left", padx=10)

        self.next_btn = tk.Button(button_frame, text="Next", command=self.go_next, bg="#555555", fg="white",
                                  font=("Helvetica", 14, "bold"), relief="groove", padx=10, pady=10)
        self.next_btn.pack(side="left", padx=10)

        # Bind rectangle drawing
        self.drawing_rectangle = False
        self.rectangle = None
        self.canvas.mpl_connect("button_press_event", self.start_rectangle)
        self.canvas.mpl_connect("motion_notify_event", self.update_rectangle)
        self.canvas.mpl_connect("button_release_event", self.finalize_rectangle)

    def init_image(self):
        if self.var.get() == 1:
            self.middle_slice_idx = self.vol_data.shape[1] // 2
            middle_slice = self.vol_data[:, self.middle_slice_idx, :]
        elif self.var.get() == 2:
            self.middle_slice_idx = self.vol_data.shape[2] // 2
            middle_slice = self.vol_data[:, :, self.middle_slice_idx]

        self.ax.clear()
        self.ax.imshow(middle_slice, cmap="gray")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

    def update_image(self):
        """Update the displayed image based on the current slice index."""
        if self.vol_data is not None:
            if self.var.get() == 1:
                middle_slice = self.vol_data[:, self.middle_slice_idx, :]
            elif self.var.get() == 2:
                middle_slice = self.vol_data[:, :, self.middle_slice_idx]

            self.ax.clear()
            self.ax.imshow(middle_slice, cmap="gray")
            self.ax.set_xticks([])  # Remove x-axis ticks
            self.ax.set_yticks([])  # Remove y-axis ticks

            if self.rectangle:
                self.ax.add_patch(self.rectangle)

            self.canvas.draw()

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

    def go_previous(self):
        """Go back to Page 1."""
        self.master.show_page_1()

    def go_next(self):
        """Proceed to the next page if rectangle exists."""
        return self.master.show_page_3(self.rect_start, self.rect_end)

    def reset_drawing(self):
        """Reset the drawing."""
        if self.rectangle:
            self.rectangle.remove()
            self.rectangle = None
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
