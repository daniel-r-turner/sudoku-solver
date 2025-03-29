import customtkinter as ctk


class SudokuGrid(ctk.CTkFrame):
    """A 9x9 grid of Sudoku cells."""
    def __init__(self, parent):
        super().__init__(parent)
        self.cells = []

        self.inner_frame = ctk.CTkFrame(self)
        self.inner_frame.pack()

        for row in range(9):
            row_cells = []
            for col in range(9):
                cell = ctk.CTkEntry(self.inner_frame, width=40, height=40, font=("Roboto", 14), justify="center")
                def _on_key_release(*args, cell=cell, row=row, col=col):
                    cell.configure(font=("Roboto", 14))
                    if parent.sudoku_grid is not None:
                        existing_board_cell = parent.sudoku_grid.get_cell_from_cord(row_num=row, col_num=col)
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

    def add_dividers(self):
        """Adds black lines between every 3x3 block."""
        for i in range(1, 3):  # dividers after row/col 3 and 6
            # Horizontal line
            h_line = ctk.CTkFrame(self.inner_frame, height=2, width=400, fg_color="black")
            h_line.place(x=0, y=i * 3 * 44)  # 44 is approx row height including padding

            # Vertical line
            v_line = ctk.CTkFrame(self.inner_frame, width=2, height=400, fg_color="black")
            v_line.place(x=i * 3 * 44, y=0)  # 44 is approx column width including padding