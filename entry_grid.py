"""
entry_grid.py

This module implements the SudokuGrid class, which provides a graphical 9x9 grid
of Sudoku cells using the CustomTkinter library. The grid allows user interaction
with the puzzle through key events and visually separates the 3x3 sub-grids with dividers.
"""

import customtkinter as ctk


class SudokuGrid(ctk.CTkFrame):
    """
    A 9x9 grid of Sudoku cells.

    This class creates an interactive grid for a Sudoku puzzle where each cell is
    represented by a CustomTkinter Entry widget. It supports key events for updating
    the grid, candidate management, and visual feedback when the puzzle is solved.

    Attributes:
        cells (list[list[ctk.CTkEntry]]): A 2D list representing the 9x9 grid of cell widgets.
        inner_frame (ctk.CTkFrame): A container frame that holds all the Sudoku cells.
    """

    def __init__(self, parent):
        """
        Initialize the SudokuGrid widget and build the 9x9 grid of entry cells.

        For each cell, a key release event handler is bound to update the grid state,
        manage candidates, and check for puzzle completion.

        Args:
            parent (ctk.CTk): The main application window (an instance of SudokuApp) that contains this grid.
        """
        super().__init__(parent)
        self.cells = []

        self.inner_frame = ctk.CTkFrame(self)
        self.inner_frame.pack()

        for row in range(9):
            row_cells = []
            for col in range(9):
                cell = ctk.CTkEntry(self.inner_frame, width=40, height=40, font=("Roboto", 14), justify="center")
                def _on_key_release(*args, cl=cell, ro=row, co=col):
                    """
                    Handle key release events in a Sudoku grid cell.

                    This function performs the following tasks when a key is released:
                      - Resets the cell's font to ensure consistent appearance.
                      - If the Sudoku grid has been initialized, retrieves the corresponding board cell
                        and, if it was previously filled (thus being replaced), add the previous value back
                        as a candidate to the cells that it sees.
                      - If the Sudoku grid hasn't been initialized, no candidate eliminations were made with
                        the previously stored value, so no action is required
                      - Updates the internal grid state and candidate displays.
                      - Checks if the puzzle is solved, and if so, updates the UI to indicate success.

                    Args:
                        *args: Positional arguments capturing the key release event details.
                        cl (ctk.CTkEntry): The entry cell widget where the key event occurred.
                        ro (int): The row index of the cell.
                        co (int): The column index of the cell.
                    """
                    cl.configure(font=("Roboto", 14))
                    if parent.sudoku_grid is not None:
                        existing_board_cell = parent.sudoku_grid.get_cell_from_cord(row_num=ro, col_num=co)
                        if existing_board_cell.value != 0:
                            cells_to_fix = set(parent.sudoku_grid.get_full_row(cell=existing_board_cell) +
                                               parent.sudoku_grid.get_full_col(cell=existing_board_cell) +
                                               parent.sudoku_grid.get_full_box(cell=existing_board_cell))
                            cells_to_fix.remove(existing_board_cell)
                            for c in [ctf for ctf in cells_to_fix if ctf.is_empty()]:
                                c.add_candidate(existing_board_cell.value)
                    parent.update_grid(update=True)
                    parent.show_candidates()
                    if parent.sudoku_grid.board_solved():
                        parent.log_text.configure(text_color="green", text="Congratulations!")
                        for r in range(9):
                            for c in range(9):
                                cell_entry = parent.grid_frame.cells[r][c]
                                cell_entry.configure(text_color="green")
                    else:
                        parent.log_text.configure(text="")
                cell.bind("<KeyRelease>", _on_key_release)
                cell.grid(row=row, column=col, padx=2, pady=2)
                row_cells.append(cell)

            self.cells.append(row_cells)

        self.add_dividers()  # add grid lines

    def add_dividers(self) -> None:
        """
        Adds visual dividers between the 3x3 sub-grids of the Sudoku board to indicate boxes.
        """
        for i in range(1, 3):  # dividers after row/col 3 and 6
            # Horizontal line
            h_line = ctk.CTkFrame(self.inner_frame, height=2, width=400, fg_color="black")
            h_line.place(x=0, y=i * 3 * 44)  # 44 is approx row height including padding

            # Vertical line
            v_line = ctk.CTkFrame(self.inner_frame, width=2, height=400, fg_color="black")
            v_line.place(x=i * 3 * 44, y=0)  # 44 is approx column width including padding