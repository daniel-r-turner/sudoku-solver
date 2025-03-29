class Cell:
    def __init__(self, c: int, r: int, value: int = 0):
        self.value = value
        self.col: int = c
        self.row: int = r
        self.box = int(c / 3) + 3 * int(r / 3) + 1
        self.board = None
        self.candidates = [] if value else list(range(1,10))

    def is_empty(self) -> bool:
        return self.value == 0

    def set_board(self, board: "Sudoku"):
        self.board = board

    def fill(self, val):
        self.value = val
        self.candidates = []  # remove all candidates from the cell
        self.board.update_candidates([self])  # update all the cells in this cell's row, col, and box based on val

    def remove_candidates(self, candidates_to_remove: list[int]) -> None:
        for c in candidates_to_remove:
            if c in self.candidates:
                self.candidates.remove(c)

    def add_candidate(self, candidate_to_add: int) -> None:
        if candidate_to_add not in self.candidates:
            self.candidates.append(candidate_to_add)

    def shares_unit(self, cell: "Cell") -> bool:
        return cell.row == self.row or cell.col == self.col or cell.box == self.box

    def __str__(self):
        return str(self.value)