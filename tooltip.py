"""
tooltip.py

This module implements a Tooltip widget for the Sudoku Solver application using CustomTkinter.
The Tooltip is a label that displays helpful text when hovering over a designated UI element,
and hides when the mouse leaves the area.
"""
import customtkinter as ctk


class Tooltip(ctk.CTkLabel):
    """
    A tooltip widget that appears on mouse hover.

    Inherits from CustomTkinter's CTkLabel. The Tooltip displays a brief help message,
    and is designed to appear near the mouse cursor when hovering over a UI element.
    """
    def __init__(self, master, text):
        """
        Initialize a new Tooltip instance.

        The tooltip is configured with a dark gray background, white text,
        rounded corners, and internal padding. It is hidden by default.

        Args:
            master (ctk.CTk): The main application window (an instance of SudokuApp) that contains this tooltip.
            text (str): The text message to display in the tooltip.
        """
        super().__init__(master, text=text, fg_color="dark gray", text_color="white", corner_radius=5, padx=5, pady=2)
        self.place_forget()  # Hide initially

    def show(self, event):
        """
        Display the tooltip near the current mouse position.

        Positions the tooltip 10 pixels to the right and below the current mouse cursor,
        adjusting for the root window's position.

        Args:
            event: The Tkinter event object containing the cursor's position.
        """
        self.place(x=event.x_root - self.winfo_toplevel().winfo_rootx() + 10,
                   y=event.y_root - self.winfo_toplevel().winfo_rooty() + 10)

    def hide(self, _):
        """
        Hide the tooltip.

        Called when the mouse leaves the UI element, ensuring that the tooltip is removed from view.

        Args:
            _ : Unused event object.
        """

        self.place_forget()
