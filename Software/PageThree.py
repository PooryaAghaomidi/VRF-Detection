import csv
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DicomViewerPage3(tk.Frame):
    def __init__(self, master, my_data, start_rect_1, end_rect_1, start_rect_2, end_rect_2):
        super().__init__(master)
        self.master = master
        self.grid(sticky="nsew")

        self.start_rect_1 = start_rect_1
        self.end_rect_1 = end_rect_1
        self.start_rect_2 = start_rect_2
        self.end_rect_2 = end_rect_2

        self.configure(bg='#323232')

        # Variables
        self.dicom_data = None
        self.vol_data = None
        self.rect_coords = [None, None, None]  # Rectangles for three axes
        self.parameter_names = [tk.StringVar() for _ in range(6)]
        self.parameter_values = [tk.StringVar() for _ in range(6)]

        # UI Components
        self.create_widgets()

        self.vol_data = my_data

        # Configure scrollbars
        for i, scrollbar in enumerate(self.scrollbars):
            scrollbar.config(to=self.vol_data.shape[i] - 1)
            scrollbar.set(self.vol_data.shape[i] // 2)

        # Update images
        self.update_images()

    def create_widgets(self):
        # Set the background color for the main window
        self.config(bg="#323232")

        # Image Display Canvas
        self.fig, self.axes = plt.subplots(1, 3, figsize=(15, 5))
        # Set the background color of the figure and axes
        self.fig.patch.set_facecolor('#323232')  # Set the figure background color
        for ax in self.axes:
            ax.set_facecolor('#323232')  # Set the axes background color
            ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, columnspan=3, padx=10, pady=0, sticky="nsew")

        # Set the background color for the canvas widget (it may not always work, but it's worth trying)
        self.canvas_widget.config(bg="#323232")

        # Scrollbar for slice navigation
        self.scrollbars = [
            tk.Scale(self, from_=0, to=0, orient="horizontal",
                     command=lambda value, axis=i: self.update_slice(int(value), axis))
            for i in range(3)
        ]
        for i, scrollbar in enumerate(self.scrollbars):
            scrollbar.grid(row=1, column=i, padx=0, pady=0, sticky="nsew")
            scrollbar.config(bg="#323232", fg="white")  # Set background and foreground for the scrollbar

        # Parameter Fields
        self.entries = []
        for i in range(4):
            for j in range(3):
                entry = tk.Entry(self)
                entry.grid(row=i + 2, column=j, padx=5, pady=5, sticky='nsew')
                entry.config(bg="#323232", fg="white")  # Set background and foreground for the entry fields
                self.entries.append(entry)

        # Set placeholders for parameters
        self.entries[0].insert(0, "Crown position")
        self.entries[1].insert(0, "Root position")
        self.entries[2].insert(0, "Long axis of the tooth")
        self.entries[3].insert(0, " ")
        self.entries[4].insert(0, " ")
        self.entries[5].insert(0, " ")
        self.entries[6].insert(0, "External root resorption in adjacent teeth")
        self.entries[7].insert(0, "Relationship with the sinus and nasal floor")
        self.entries[8].insert(0, "Extra Parameter")
        self.entries[9].insert(0, " ")
        self.entries[10].insert(0, " ")
        self.entries[11].insert(0, "None")

        # Save Button
        save_button = tk.Button(self, text="Save", command=self.save_data)
        save_button.grid(row=7, column=1, padx=0, pady=0, sticky="nsew")
        save_button.config(bg="#323232", fg="white")  # Set background and foreground for the save button

        # Reset Button (calls self.show_page_1)
        reset_button = tk.Button(self, text="Reset the software", command=self.reset_app)
        reset_button.grid(row=8, column=1, padx=0, pady=0, sticky="nsew")
        reset_button.config(bg="#323232", fg="white")  # Set background and foreground for the reset button

        # Configure the grid to ensure that columns and rows expand properly
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1)  # Add weight to row 8 for reset button
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

    def reset_app(self):
        """Calls the reset_app method in MainWindow"""
        self.master.reset_app()

    def update_slice(self, index, axis):
        if self.vol_data is not None:
            self.rect_coords[axis] = None  # Clear rectangle for this axis
            self.update_images()

    def update_images(self):
        if self.vol_data is None:
            return

        slices = [
            self.vol_data[self.scrollbars[0].get(), :, :],
            self.vol_data[:, self.scrollbars[1].get(), :],
            self.vol_data[:, :, self.scrollbars[2].get()]
        ]

        for i, ax in enumerate(self.axes):
            ax.clear()
            ax.imshow(slices[i], cmap='gray')
            ax.axis('off')

            if self.rect_coords[i]:
                rect = self.rect_coords[i]
                ax.add_patch(plt.Rectangle((rect[0], rect[1]), rect[2] - rect[0], rect[3] - rect[1],
                                           fill=False, color='red'))

        self.canvas.draw()

    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if file_path:
            # Prepare data for CSV export
            data = [
                ["Start coordination for rect 1", self.start_rect_1],
                ["End coordination for rect 1", self.end_rect_1],
                ["Start coordination for rect 2", self.start_rect_2],
                ["End coordination for rect 2", self.end_rect_2],
                [f"{self.entries[0].get()}", self.entries[3].get()],
                [f"{self.entries[1].get()}", self.entries[4].get()],
                [f"{self.entries[2].get()}", self.entries[5].get()],
                [f"{self.entries[6].get()}", self.entries[9].get()],
                [f"{self.entries[7].get()}", self.entries[10].get()],
                [f"{self.entries[8].get()}", self.entries[11].get()],
            ]

            # Write to CSV file
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)

            print(f"Data exported to {file_path}")
