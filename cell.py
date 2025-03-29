"""
cell.py

This module defines the Cell class, which represents an individual cell in a Sudoku puzzle.
Each cell stores its value, position (row, column, and corresponding 3x3 box), and candidate values.
It also provides methods to update its state and interact with its parent Sudoku board.
"""

class Cell:
    """
    Represents a single cell in a Sudoku puzzle.

    Attributes:
        value (int): The current value of the cell (0 indicates empty).
        col (int): The column index of the cell (0-indexed).
        row (int): The row index of the cell (0-indexed).
        box (int): The 3x3 box number the cell belongs to (1-indexed).
        board (Sudoku or None): Reference to the parent Sudoku board. Initially None.
        candidates (list[int]): A list of possible candidate values for the cell.
            If the cell is empty, candidates are initialized to [1,2,...,9]; otherwise, it's empty.
    """

    def __init__(self, c: int, r: int, value: int = 0):
        """
        Initialize a new Cell instance.

        Args:
            c (int): The column index for the cell (0-indexed).
            r (int): The row index for the cell (0-indexed).
            value (int, optional): The initial value of the cell. Defaults to 0 (empty).
        """
        self.value = value
        self.col: int = c
        self.row: int = r
        self.box = int(c / 3) + 3 * int(r / 3) + 1
        self.board = None
        self.candidates = [] if value else list(range(1,10))

    def is_empty(self) -> bool:
        """
        Check if the cell is empty.

        Returns:
            bool: True if the cell's value is 0 (empty), False otherwise.
        """
        return self.value == 0

    def set_board(self, board: "Sudoku") -> None:
        """
        Set the parent Sudoku board for this cell.

        Args:
            board (Sudoku): The Sudoku board instance that this cell belongs to.
        """
        self.board = board

    def fill(self, val) -> None:
        """
        Fill the cell with a given value and update candidates in the corresponding row, column, and 3x3 box.

        Args:
            val (int): The digit to fill into the cell.
        """
        self.value = val
        self.candidates = []  # remove all candidates from the cell
        self.board.update_candidates([self])  # update all the cells in this cell's row, col, and box based on val

    def remove_candidates(self, candidates_to_remove: list[int]) -> None:
        """
        Remove specified candidates from the cell's candidate list.

        Args:
            candidates_to_remove (list[int]): A list of candidate digits to be removed.
        """
        for c in candidates_to_remove:
            if c in self.candidates:
                self.candidates.remove(c)

    def add_candidate(self, candidate_to_add: int) -> None:
        """
        Add a candidate digit to the cell's candidate list if not already present.

        Args:
            candidate_to_add (int): The candidate digit to add.
        """
        if candidate_to_add not in self.candidates:
            self.candidates.append(candidate_to_add)

    def shares_unit(self, cell: "Cell") -> bool:
        """
        Determine if this cell shares a common row, column, or box with another cell.

        Args:
            cell (Cell): The other cell to compare with.

        Returns:
            bool: True if both cells share the same row, column, or 3x3 box; otherwise, False.
        """
        return cell.row == self.row or cell.col == self.col or cell.box == self.box

    def __str__(self) -> str:
        """
        Return a string representation of the cell.

        Returns:
            str: The string representation of the cell's value.
        """
        return str(self.value)