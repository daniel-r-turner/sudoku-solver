import customtkinter as ctk

from board import Sudoku
from cell import Cell
from entry_grid import SudokuGrid
from example_puzzles import ExamplePuzzles
from tooltip import Tooltip


class SudokuApp(ctk.CTk):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.title("Sudoku Solver")
        self.geometry("700x900")

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

        self.next_cell_button = ctk.CTkButton(self.button_frame, text="Fill Next Cell", command=self.get_next)
        self.next_cell_button.grid(row=0, column=1, padx=40, pady=5)

        self.hint_button = ctk.CTkButton(self.button_frame, text="Hint", command=self.hint)
        self.hint_button.grid(row=1, column=1, padx=40, pady=5)

        self.help_button = ctk.CTkButton(self, text="?", width=30, height=30, corner_radius=15,
                                         fg_color="gray", text_color="white", hover_color="darkgray")
        self.help_button.place(x=10, rely=0.92, anchor="sw")

        self.tooltip = Tooltip(self, text=(
            f"Click into cells to place digits and customize a puzzle, or use the dropdown menu to\nchange the "
            f"difficulty of example puzzles, and click 'Show {self.example_difficulty_options.get()} Example' to "
            f"generate an\nexample puzzle. 'Clear Grid' to remove all digits. 'Solve Puzzle' to find a solution "
            f"instantly."
        ))

        self.help_button.bind("<Enter>", self.tooltip.show)  # Show on hover
        self.help_button.bind("<Leave>", self.tooltip.hide)  # Hide when leaving

        self.log_text = ctk.CTkLabel(self, text="", font=("Roboto", 14))
        self.log_text.pack()

        self.sudoku_grid = None

    def show_candidates(self):
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

    def update_grid(self, update: bool = False):
        if not self.sudoku_grid:
            self.sudoku_grid = Sudoku.make_sudoku(list_of_rows=[
                [int(cell.get()) if cell.get() != '' else 0 for cell in row] for row in self.grid_frame.cells
            ])
        elif update:
            self.sudoku_grid.update_sudoku(list_of_rows=[
                [int(cell.get()) if cell.get() != '' else 0 for cell in row] for row in self.grid_frame.cells
            ])

    def clear_grid(self, delete: bool = True):
        self.log_text.configure(text="")
        if delete:
            self.sudoku_grid = None
        for row in self.grid_frame.cells:
            for cell in row:
                if delete:
                    cell.delete(0, "end")
                    cell.configure(placeholder_text="")
                cell.configure(text_color="black", fg_color="white")

    def solve_sudoku(self):
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
                    if not cell.get() and result[row][col].value != 0:  # if cell wasn't inputted, and was found, update
                        cell.insert(0, str(result[row][col].value))
                    cell.configure(text_color=colour)
        self.show_candidates()

    def get_next(self):
        """Fill the next logical cell to fill, and display an explanation message"""
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

    def hint(self):
        """Highlight the next logical cell to fill"""
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

    def difficulty_changed(self, _):
        difficulty_colours = {
            "Easy": "green",
            "Medium": "orange",
            "Hard": "red"
        }
        button_colour = difficulty_colours[self.example_difficulty_options.get()]
        self.example_button.configure(
            text=f"Show {self.example_difficulty_options.get()} Example",
            fg_color=button_colour,
            hover_color=f"dark {button_colour}"
        )
        self.tooltip.configure(text=(
            f"Click into cells to place digits and customize a puzzle, or use the dropdown menu to\nchange the "
            f"difficulty of example puzzles, and click 'Show {self.example_difficulty_options.get()} Example' to "
            f"generate an\nexample puzzle. 'Clear Grid' to remove all digits. 'Solve Puzzle' to find a solution "
            f"instantly."
        ))

    def show_example(self):
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

    def display_invalid_cells(self, result):
        invalid_cells = [c for c in result if not c.is_empty()]
        unfillable_cells = [c for c in result if c.is_empty()]
        ex_unfillable_cell_txt = "" if not unfillable_cells else (
            f" based on the inputted digits, it is impossible to place a digit in row "
            f"{unfillable_cells[0].row + 1}, column {unfillable_cells[0].col + 1}")
        ex_invalid_cell_txt = "" if not invalid_cells else (
            f" the digit {invalid_cells[0].value} is duplicated in the cells ({invalid_cells[0].row + 1}, "
            f"{invalid_cells[0].col + 1}) and ({invalid_cells[1].row + 1}, {invalid_cells[1].col + 1})."
            f"{' Also,\n' if ex_unfillable_cell_txt else ''}")

        err_text = (f"Invalid board! Digits must appear once in every row, column, and box. For example,\n"
                    f"{ex_invalid_cell_txt}{ex_unfillable_cell_txt}")
        self.log_text.configure(
            text_color="red", text=err_text
        )
        for c in invalid_cells:
            invalid_cell = self.grid_frame.cells[c.row][c.col]
            invalid_cell.configure(text_color="red")
        for c in unfillable_cells:
            unfillable_cell = self.grid_frame.cells[c.row][c.col]
            unfillable_cell.configure(fg_color="red")

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = SudokuApp()
    app.mainloop()