import customtkinter as ctk


class Tooltip(ctk.CTkLabel):
    """A tooltip that appears when hovering over a '?' button."""
    def __init__(self, master, text):
        super().__init__(master, text=text, fg_color="dark gray", text_color="white", corner_radius=5, padx=5, pady=2)
        self.place_forget()  # Hide initially

    def show(self, event):
        self.place(x=event.x_root - self.winfo_toplevel().winfo_rootx() + 10,
                   y=event.y_root - self.winfo_toplevel().winfo_rooty() + 10)

    def hide(self, _):
        self.place_forget()
