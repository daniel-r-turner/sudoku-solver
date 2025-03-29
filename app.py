"""
app.py

This module provides the main graphical user interface for the Sudoku Solver application.
It uses the CustomTkinter library for the UI and integrates with the Sudoku board, cell, and grid logic.
The application allows users to input Sudoku puzzles, display candidate digits, solve puzzles,
and receive hints for logical next steps.
"""

import customtkinter as ctk

from board import Sudoku
from cell import Cell
from entry_grid import SudokuGrid
from example_puzzles import ExamplePuzzles
from tooltip import Tooltip


class SudokuApp(ctk.CTk):
    """
    SudokuApp is the main application window for the Sudoku Solver.

    It creates and manages all UI components including the grid of entry boxes,
    control buttons, candidate display options, and the help tooltip.

    Attributes:
        show_cand_frame (ctk.CTkFrame): Frame containing the candidate display switch.
        show_cand_button (ctk.CTkSwitch): Switch to toggle candidate visibility.
        grid_frame (SudokuGrid): Custom 9x9 grid widget for the Sudoku puzzle.
        example_num (dict): Tracks the current example puzzle index for each difficulty.
        button_frame (ctk.CTkFrame): Frame containing various control buttons.
        example_difficulty_options (ctk.CTkOptionMenu): Dropdown menu for selecting puzzle difficulty.
        example_button (ctk.CTkButton): Button to load an example puzzle.
        clear_button (ctk.CTkButton): Button to clear the current grid.
        solve_button (ctk.CTkButton): Button to trigger puzzle solving.
        next_cell_button (ctk.CTkButton): Button to get the next logical move.
        hint_button (ctk.CTkButton): Button to provide a hint.
        help_button (ctk.CTkButton): Button to display help tooltip.
        tooltip (Tooltip): Tooltip instance providing help text when mouse hovers help_button.
        log_text (ctk.CTkLabel): Label used to display messages and logs.
        sudoku_grid (Sudoku or None): Current Sudoku board instance; initialized on first grid update.
    """
    def __init__(self):
        """
        Initialize the SudokuApp window, configure UI elements,
        and set up the necessary widgets for the Sudoku Solver.
        """
        super().__init__()
        self.title("Sudoku Solver")
        self.geometry("700x800")

        self.show_cand_frame = ctk.CTkFrame(self)
        self.show_cand_frame.pack(pady=20)
        self.show_cand_button = ctk.CTkSwitch(self.show_cand_frame, text= "Show Candidates", command=self.show_candidates)
        self.show_cand_button.grid(row=0, column=0, padx=5, pady=0)

        self.grid_frame = SudokuGrid(self)
        self.grid_frame.pack(pady=20)
        self.example_num = {
            "EASY": 0,
            "MEDIUM": 0,
            "HARD": 0
        }

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        self.example_difficulty_options = ctk.CTkOptionMenu(
            self.button_frame,
            values=["Easy", "Medium", "Hard"],
            command=self.difficulty_changed,
            width=150
        )
        self.example_difficulty_options.grid(row=0, column=0, padx=40, pady=5)

        self.example_button = ctk.CTkButton(
            self.button_frame,
            text=f"Show {self.example_difficulty_options.get()} Example",
            command=self.show_example,
            width=150,
            fg_color="green",
            hover_color="dark green"
        )
        self.example_button.grid(row=1, column=0, padx=40, pady=5)

        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear Grid", command=self.clear_grid)
        self.clear_button.grid(row=0, column=2, padx=40, pady=5)

        self.solve_button = ctk.CTkButton(self.button_frame, text="Solve Puzzle", command=self.solve_sudoku)
        self.solve_button.grid(row=1, column=2, padx=40, pady=5)

        self.next_cell_button = ctk.CTkButton(self.button_frame, text="Get Next Step", command=self.get_next)
        self.next_cell_button.grid(row=0, column=1, padx=40, pady=5)

        self.hint_button = ctk.CTkButton(self.button_frame, text="Hint", command=self.hint)
        self.hint_button.grid(row=1, column=1, padx=40, pady=5)

        self.help_button = ctk.CTkButton(self, text="?", width=30, height=30, corner_radius=15,
                                         fg_color="gray", text_color="white", hover_color="darkgray")
        self.help_button.place(x=10, rely=0.85, anchor="sw")

        self.tooltip = Tooltip(self, text=(
            f"Click into cells to place digits and customize a puzzle, or use the dropdown menu to\nchange the "
            f"difficulty of example puzzles, and click 'Show {self.example_difficulty_options.get()} Example' to "
            f"generate an\nexample puzzle. To show all possible digits for each cell, select 'Show Candidates'.\nIf "
            f"you get stuck while solving, click 'Hint' to highlight the next cell that can be filled in,\nor click "
            f"'Get Next Step' to see information about the next logical step in the puzzle.\nClick 'Clear Grid' to "
            f"remove all digits. 'Solve Puzzle' to find a solution instantly."
        ))

        self.help_button.bind("<Enter>", self.tooltip.show)  # Show on hover
        self.help_button.bind("<Leave>", self.tooltip.hide)  # Hide when leaving

        self.log_text = ctk.CTkLabel(self, text="", font=("Roboto", 14))
        self.log_text.pack()

        self.sudoku_grid = None

    def show_candidates(self) -> None:
        """
        Update the grid and display candidate digits in empty cells.

        For each cell in the grid, if the cell is empty and the 'Show Candidates'
        switch is active, update the cell's placeholder text to show the possible candidates.
        Otherwise, clear the placeholder text.
        """
        show = self.show_cand_button.get()
        self.update_grid()
        self.sudoku_grid.update_candidates(self.sudoku_grid.cells)
        for row in range(9):
            for col in range(9):
                cell_obj = self.sudoku_grid.get_cell_from_cord(row_num=row, col_num=col)
                cell = self.grid_frame.cells[row][col]
                if not cell_obj.value:
                    if show:
                        candidates_list = [str(i) if i in cell_obj.candidates else '' for i in range(1, 10)]
                        candidates_text = "".join(candidates_list)

                        cell.configure(placeholder_text=candidates_text)  
                        cell.configure(font=("Arial", 8))

                    else:
                        cell.configure(placeholder_text="")
                else:
                    cell.configure(placeholder_text="", font=("Roboto", 14))

    def update_grid(self, update: bool = False) -> None:
        """
        Create or update the Sudoku grid based on the current UI inputs.

        If the sudoku_grid is not yet created, this method instantiates it by
        reading the current cell values from the grid_frame. If the grid already exists
        and 'update' is True, the sudoku_grid is updated with the latest values.

        Args:
            update (bool): Flag to indicate whether to update an existing sudoku_grid.
        """
        if not self.sudoku_grid:
            self.sudoku_grid = Sudoku.make_sudoku(list_of_rows=[
                [int(cell.get()) if cell.get().strip() != '' else 0 for cell in row] for row in self.grid_frame.cells
            ])
        elif update:
            self.sudoku_grid.update_sudoku(list_of_rows=[
                [int(cell.get()) if cell.get().strip() != '' else 0 for cell in row] for row in self.grid_frame.cells
            ])

    def clear_grid(self, delete: bool = True) -> None:
        """
        Clear the grid display and optionally reset the sudoku_grid instance.

        This method clears the text and resets color attributes for each cell.
        If 'delete' is True, it also deletes the current sudoku_grid instance.

        Args:
            delete (bool): Flag to indicate whether to reset the sudoku_grid instance.
        """
        self.log_text.configure(text="")
        if delete:
            self.sudoku_grid = None
        for row in self.grid_frame.cells:
            for cell in row:
                if delete:
                    cell.delete(0, "end")
                    cell.configure(placeholder_text="")
                cell.configure(text_color="black", fg_color="white")

    def solve_sudoku(self) -> None:
        """
        Solve the Sudoku puzzle using the current grid input.

        This method updates the sudoku_grid, clears the UI grid if necessary,
        attempts to solve the puzzle, and then updates the UI based on the result.
        """
        self.update_grid()
        if self.sudoku_grid.board_solved():
            return
        self.clear_grid(delete=False)

        result = self.sudoku_grid.solve()
        if type(result[0]) == Cell:
            # returned a list of invalid cells
            self.display_invalid_cells(result)
        elif type(result[0]) == list:
            # returned a board
            colour = "green" if self.sudoku_grid.board_solved() else "red"
            self.log_text.configure(
                text_color=colour, text="Board solved!" if colour == "green" else "Board could not be solved"
            )
            for row in range(9):
                for col in range(9):
                    cell = self.grid_frame.cells[row][col]
                    if (not cell.get() or cell.get() == '0') and result[row][col].value != 0:  # if cell wasn't inputted, and was found, update
                        cell.delete(0)
                        cell.insert(0, str(result[row][col].value))
                    cell.configure(text_color=colour)
        self.show_candidates()

    def get_next(self) -> None:
        """
        Compute and display the next logical step in solving the puzzle.

        This method updates the grid and attempts to find the next move.
        Depending on the result type, it may update a cell with the next value,
        display information about how candidates were removed from a cell, or mark invalid cells.
        """
        self.update_grid()
        if self.sudoku_grid.board_solved():
            return
        self.clear_grid(delete=False)

        result = self.sudoku_grid.get_next_step(fill=True)
        if self.sudoku_grid.board_solved():
            self.log_text.configure(text_color="green", text="Board solved!")
            for row in range(9):
                for col in range(9):
                    cell = self.grid_frame.cells[row][col]
                    if not cell.get():
                        cell.insert(0, str(self.sudoku_grid.get_cell_from_cord(row_num=row, col_num=col).value))
                    cell.configure(text_color="green")
            return

        if type(result) == tuple:
            new_cell = result[0]
            message = result[1]
            self.log_text.configure(text_color="green", text=message)
            new_cell_entry = self.grid_frame.cells[new_cell.row][new_cell.col]
            new_cell_entry.configure(fg_color="orange", font=("Roboto", 14))
            new_cell_entry.delete(0)
            new_cell_entry.insert(0, str(new_cell.value))
            self.after(2000, lambda: new_cell_entry.configure(fg_color="white"))

        elif type(result) == str:
            self.log_text.configure(text_color="red", text=result)

        elif type(result[0]) == Cell:
            self.display_invalid_cells(result)

        elif type(result[0]) == tuple:
            updated_cells = [r[0] for r in result]
            helper_cells = [r[1] for r in result]
            message = "\n".join([r[2] for r in result])
            for c in updated_cells:
                c_entry = self.grid_frame.cells[c.row][c.col]
                c_entry.configure(fg_color="blue")
                self.after(5000, lambda entry=c_entry: entry.configure(fg_color="white"))

            for loc in helper_cells:
                for c in loc:
                    c_entry = self.grid_frame.cells[c.row][c.col]
                    c_entry.configure(fg_color="light blue")
                    self.after(5000, lambda entry=c_entry: entry.configure(fg_color="white"))

            self.log_text.configure(text_color="green", text=message)
        else:
            pass
        self.show_candidates()

    def hint(self) -> None:
        """
        Highlight the next cell that can be logically deduced.

        This method repeatedly calls get_next_step (without filling the cell)
        until a valid hint is found or an error message is returned.
        When a hint is found, the corresponding cell is highlighted.
        """
        self.update_grid()
        if self.sudoku_grid.board_solved():
            return
        self.clear_grid(delete=False)
        while True:
            result = self.sudoku_grid.get_next_step(fill=False)
            if type(result) == tuple:
                break
            elif type(result) == str:
                self.log_text.configure(text_color="red", text=result)
                break
            elif type(result[0]) == Cell:
                self.display_invalid_cells(result)
            elif type(result[0]) == tuple:
                continue

        if type(result) == tuple:
            new_cell = result[0]
            new_cell_entry = self.grid_frame.cells[new_cell.row][new_cell.col]
            new_cell_entry.configure(fg_color="orange")
            self.after(2000, lambda: new_cell_entry.configure(fg_color="white"))

    def difficulty_changed(self, difficulty) -> None:
        """
        Update the example puzzle difficulty settings.

        When the user changes the difficulty option from the dropdown menu,
        this method updates the appearance and text of the example button,
        and also updates the help tooltip text accordingly.

        Args:
            difficulty : The new difficulty being selected from the dropdown menu
        """
        difficulty_colours = {
            "Easy": "green",
            "Medium": "orange",
            "Hard": "red"
        }
        button_colour = difficulty_colours[difficulty]
        self.example_button.configure(
            text=f"Show {difficulty} Example",
            fg_color=button_colour,
            hover_color=f"dark {button_colour}"
        )
        self.tooltip.configure(text=(
            f"Click into cells to place digits and customize a puzzle, or use the dropdown menu to\nchange the "
            f"difficulty of example puzzles, and click 'Show {difficulty} Example' to "
            f"generate an\nexample puzzle. To show all possible digits for each cell, select 'Show Candidates'.\nIf "
            f"you get stuck while solving, click 'Hint' to highlight the next cell that can be filled in,\nor click "
            f"'Get Next Step' to see information about the next logical step in the puzzle.\nClick 'Clear Grid' to "
            f"remove all digits. 'Solve Puzzle' to find a solution instantly."
        ))

    def show_example(self) -> None:
        """
        Display an example puzzle based on the selected difficulty.

        This method clears the current grid, retrieves an example puzzle from the ExamplePuzzles,
        fills the grid with the puzzle digits, and then updates the candidate display.
        """
        self.clear_grid()
        example_inputs = ExamplePuzzles
        selected_difficulty = self.example_difficulty_options.get().upper()
        example_input = example_inputs[selected_difficulty].value[self.example_num[selected_difficulty]]
        self.example_num[selected_difficulty] = (
            self.example_num[selected_difficulty] + 1 if
            self.example_num[selected_difficulty] < len(example_inputs[selected_difficulty].value) - 1 else
            0
        )
        for row in range(9):
            for col in range(9):
                if cell_input := example_input[row][col]:
                    cell = self.grid_frame.cells[row][col]
                    cell.insert(0, cell_input)
                    cell.configure(font=("Roboto", 14))
        self.show_candidates()

    def display_invalid_cells(self, result) -> None:
        """
        Highlight cells that contain invalid entries in the current puzzle.

        This method identifies cells that violate Sudoku rules (e.g., duplicate digits)
        and updates their text colour to red to signal an error. It also constructs and displays
        an error message indicating the nature of the invalidity.

        Args:
            result: A list of cells that are determined to be invalid.
        """
        invalid_cells = [c for c in result if c.value in range(1,10)]
        non_sudoku_cells = [c for c in result if c.value not in range(1, 10)]
        unfillable_cells = [c for c in result if c.is_empty()]
        ex_non_sudoku_cell_text = "" if not non_sudoku_cells else (
            f" sudoku puzzles must only contain the digits 1-9, for example, the cell in row "
            f"{non_sudoku_cells[0].row + 1},\ncolumn {non_sudoku_cells[0].col + 1} contains a non-sudoku digit."
        )
        ex_unfillable_cell_txt = "" if not unfillable_cells else (
            f" based on the inputted digits, it is impossible to place a digit in row "
            f"{unfillable_cells[0].row + 1}, column {unfillable_cells[0].col + 1}."
            f"{' Also,\n' if ex_non_sudoku_cell_text else ''}")
        ex_invalid_cell_txt = "" if not invalid_cells else (
            f" the digit {invalid_cells[0].value} is duplicated in the cells ({invalid_cells[0].row + 1}, "
            f"{invalid_cells[0].col + 1}) and ({invalid_cells[1].row + 1}, {invalid_cells[1].col + 1})."
            f"{' Also,\n' if ex_unfillable_cell_txt or ex_non_sudoku_cell_text else ''}")

        err_text = (f"Invalid board! Digits must appear once in every row, column, and box. This board is invalid "
                    f"because\n {ex_invalid_cell_txt}{ex_unfillable_cell_txt}{ex_non_sudoku_cell_text}")
        self.log_text.configure(
            text_color="red", text=err_text
        )
        for c in invalid_cells:
            invalid_cell = self.grid_frame.cells[c.row][c.col]
            invalid_cell.configure(text_color="red")
        for c in non_sudoku_cells:
            non_sudoku_cell = self.grid_frame.cells[c.row][c.col]
            non_sudoku_cell.configure(text_color="red")
        for c in unfillable_cells:
            unfillable_cell = self.grid_frame.cells[c.row][c.col]
            unfillable_cell.configure(fg_color="red")

if __name__ == "__main__":
    # Set the appearance mode and launch the application
    ctk.set_appearance_mode("light")
    app = SudokuApp()
    app.mainloop()