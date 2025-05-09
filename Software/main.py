import tkinter as tk
from PageOne import DicomViewerPage1
from PageTwo import DicomViewerPage2
from PageThree import DicomViewerPage3


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dicom Viewer")
        self.state('zoomed')
        self.configure(bg='#323232')

        self.current_page = None
        self.show_page_1()

    def show_page_1(self):
        """Show Page 1"""
        if self.current_page:
            self.current_page.destroy()

        self.current_page = DicomViewerPage1(self)
        self.current_page.pack(fill="both", expand=True)

    def show_page_2(self, vol_data, start_rect_1, end_rect_1):
        """Show Page 2"""
        if self.current_page:
            self.current_page.destroy()

        self.start_rect_1, self.end_rect_1 = start_rect_1, end_rect_1

        self.arch_data = vol_data.copy()
        self.current_page = DicomViewerPage2(self, vol_data)
        self.current_page.pack(fill="both", expand=True)

    def show_page_3(self, start_rect_2, end_rect_2):
        """Show Page 3"""
        if self.current_page:
            self.current_page.destroy()

        self.start_rect_2, self.end_rect_2 = start_rect_2, end_rect_2

        self.current_page = DicomViewerPage3(self, self.arch_data, self.start_rect_1, self.end_rect_1, self.start_rect_2, self.end_rect_2)
        self.current_page.pack(fill="both", expand=True)

    def reset_app(self):
        """Reset the app to the beginning (Page 1)"""
        # Reset any state variables that need to be cleared
        self.start_rect_1 = self.end_rect_1 = None
        self.start_rect_2 = self.end_rect_2 = None
        self.arch_data = None

        # Show the first page
        self.show_page_1()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
