import itertools
import numpy as np
from cell import Cell


class Sudoku:
    # DONE!

    # TODO: WHENEVER THE BOARD IS SOLVED, TURN THE DIGITS GREEN, NOT JUST WHEN THE SOLVE BUTTON IS PRESSED
    # TODO: IE. WHEN THE LAST DIGIT IS MANUALLY PLACED OR THE LAST 'GET NEXT CELL' -> 'GET NEXT STEP' IS PRESSED
    def __init__(self, board: list[list[Cell]]):
        self.board = board
        self.board_assigned_to_cells = False
        self.cells = [c for row in self.board for c in row]
        self.cols = None
        self.boxes = None
        self.solved = None
        self.pairs = {}

    @staticmethod
    def make_sudoku(list_of_rows: list[list[int]]) -> "Sudoku":
        board = []
        for r in range(len(list_of_rows)):  # iterate through the number of rows
            row = []
            for c in range(len(list_of_rows[r])):  # iterate through the number of columns
                row.append(Cell(c=c, r=r, value=list_of_rows[r][c]))
            board.append(row)
        return Sudoku(board=board)

    def update_sudoku(self, list_of_rows: list[list[int]]) -> list[Cell] | None:
        """Update the Sudoku instance based on any changes made by the user"""
        self._assign_board_to_cells()
        updated = False
        reset_candidates = False
        for r in range(9):
            for c in range(9):
                existing_cell = self.get_cell_from_cord(row_num=r, col_num=c)
                ui_value = list_of_rows[r][c]
                if ui_value != existing_cell.value:
                    if existing_cell.value != 0:
                        # since the user replaced an existing val, previously removed candidates may have been incorrect
                        reset_candidates = True
                    existing_cell.fill(ui_value)
                    updated = True
        if reset_candidates:
            self.reset_candidates()
        if updated:
            invalid_cells, unfillable_cells = self._validate_input()
            if invalid_cells or unfillable_cells:
                return invalid_cells + unfillable_cells

    def reset_candidates(self) -> None:
        """Resets the candidates for each unfilled cell back to default"""
        for cell in [c for c in self.cells if c.is_empty()]:
            cell.candidates = list(range(9))
        self.update_candidates([c for c in self.cells if not c.is_empty()])

    def _assign_board_to_cells(self):
        if not self.board_assigned_to_cells:
            for c in self.cells:
                c.set_board(self)
            self.board_assigned_to_cells = True

    def _validate_input(self) -> tuple[list[Cell], list[Cell]]:
        invalid_cells = []
        unfillable_cells = []
        for rcb in self.get_all_rows() + self.get_all_cols() + self.get_all_boxes():
            for c in rcb:
                if c.is_empty() and len(c.candidates) == 0:
                    unfillable_cells.append(c)
            cell_dict = {num: [cell for cell in rcb if cell.value == num] for num in range(1,10)}
            for num, cells in cell_dict.items():
                if len(cells) > 1:
                    invalid_cells.extend(cells)
            for invalid_cell in [cell for cell in rcb if cell.value not in range(0,10)]:
                invalid_cells.append(invalid_cell)
        return list(set(invalid_cells)), list(set(unfillable_cells))

    def get_full_row(self, cell: Cell) -> list[Cell]:
        # return a list of cells in the row of the given cell, including the cell
        return self.board[cell.row]

    def get_full_col(self, cell: Cell) -> list[Cell]:
        # return a list of cells in the column of the given cell, including the cell
        return [row[cell.col] for row in self.board]

    def get_full_box(self, cell: Cell) -> list[Cell]:
        # return a list of cells in the row of the given cell, including the cell
        return [c for c in self.cells if c.box == cell.box]

    def get_all_rows(self) -> list[list[Cell]]:
        return self.board

    def get_all_cols(self) -> list[list[Cell]]:
        if not self.cols:
            self.cols = [[row[col] for row in self.board] for col in list(range(9))]
        return self.cols

    def get_all_boxes(self) -> list[list[Cell]]:
        if not self.boxes:
            self.boxes = []
            for row_num in list(range(3)):
                for col_num in list(range(3)):
                     self.boxes.append(self.get_full_box(self.get_cell_from_cord(row_num=row_num*3, col_num=col_num*3)))
        return self.boxes

    def get_cell_from_cord(self, row_num: int, col_num: int) -> Cell:
        return self.cells[row_num * 9 + col_num]

    def update_candidates(self, new_cells: list[Cell]):
        # remove each new cells value as a candidate from every cell in its row, col, and box
        for new_cell in new_cells:
            cells_to_update = list(set(
                self.get_full_row(new_cell) + self.get_full_col(new_cell) + self.get_full_box(new_cell)
            ))
            cells_to_update.remove(new_cell)  # unique list not including the new cell itself
            for c in [ce for ce in cells_to_update if ce.is_empty()]:
                c.remove_candidates([new_cell.value])

    def find_ntuples(self, one_step: bool = False, fill: bool = True) -> list[Cell | list[Cell]] | list[Cell, list[Cell], str] | None:
        """
            Returns either
                - the filled cells resulting from finding tuples of cells within rcb where a number must go
                - the empty cells whose candidates were updated as a result of finding n-tuples

        """
        found_cells = []
        removed_candidates = []
        all_units = self.get_all_boxes() + self.get_all_rows() + self.get_all_cols()
        for rcb in all_units:
            candidate_dict = {num: [cell for cell in rcb if num in cell.candidates] for num in range(1,10)}
            for num, cells in candidate_dict.items():
                if len(cells) == 1:
                    if fill:
                        cells[0].fill(num)  # this cell is the only one in its row, col, and/or box where num can go
                    found_cells.append(cells[0])
                    if one_step:
                        found_cells.append(rcb)
                        return found_cells

        if found_cells:
            return found_cells

        for rcb in all_units:
            candidate_dict = {num: [cell for cell in rcb if num in cell.candidates] for num in range(1,10)}
            for num, cells in candidate_dict.items():
                if len(cells) == 2:
                    if cells[0].row == cells[1].row or cells[0].col == cells[1].col:  # ignore diagonal pairs
                        if rcb == self.get_full_box(cells[0]):  # if the cells are in the same box
                            if cells[0].row == cells[1].row:
                                # digit can only go in one row in a box, it cannot go anywhere else in the row
                                for cell in [c for c in self.get_full_row(cells[0])
                                             if c not in cells and num in c.candidates]:
                                    cell.remove_candidates([num])
                                    info_str = (f"The digit {num} in box {cells[0].box} can only go in row "
                                                f"{cells[0].row + 1}, therefore (r{cell.row + 1}, c{cell.col + 1}) cannot "
                                                f"be {num}")
                                    removed_candidates.append((cell, cells, info_str))
                                    if one_step:
                                        return removed_candidates
                            else:
                                # digit can only go in one col in a box, it cannot go anywhere else in that col
                                for cell in [c for c in self.get_full_col(cells[0])
                                             if c not in cells and num in c.candidates]:
                                    cell.remove_candidates([num])
                                    info_str = (f"The digit {num} in box {cells[0].box} can only go in column "
                                                f"{cells[0].col}, therefore ({cell.row + 1}, {cell.col + 1}) cannot be"
                                                f"{num}")
                                    removed_candidates.append((cell, cells, info_str))
                                if one_step and removed_candidates:
                                    return removed_candidates
                        if cells_w_removed_candidates := self.add_pair(cells[0], cells[1], num):
                            removed_candidates.extend(cells_w_removed_candidates)
                            if one_step and removed_candidates:
                                return removed_candidates
        return removed_candidates

    def find_ncandidates(self, one_step: bool = False, fill: bool = True, max_n: int = 3):
        """
        Arguments:
            - one_step: if True, return the found information after only one logical step
            - fill: if True, fill the cell with the found value
            - max_n: the greatest size set of candidates to check for
        Returns either:
            - the filled cells resulting from finding cells with only one candidate, or
            - a list containing a tuple (cell, naked_subset, info_str) where an elimination was performed to a naked
            subset found in a row, column, or box.
        """
        removed_candidates = []
        found_cells = []
        # Combine rows, columns, and boxes into a single list of units.
        all_units = self.get_all_boxes() + self.get_all_rows() + self.get_all_cols()

        for rcb in all_units:
            # Determine the unit identifier (e.g., box, row, or column)
            if rcb[0].box == rcb[8].box:
                unit = f"box {rcb[0].box}"
            elif rcb[0].row == rcb[8].row:
                unit = f"row {rcb[0].row + 1}"
            else:
                unit = f"column {rcb[0].col + 1}"

            # Consider all subsets of cells within this unit
            # Since a unit has at most 9 cells, iterating through all subsets is acceptable
            for n in range(1, max_n + 1):
                # Only consider cells that are not already filled
                candidate_cells = [cell for cell in rcb if cell.is_empty()]
                for cell_subset in itertools.combinations(candidate_cells, n):
                    # Create the union of candidates in this subset
                    union_candidates = set()
                    for cell in cell_subset:
                        union_candidates.update(cell.candidates)
                    # Check for a naked subset: the union size equals the number of cells in the subset
                    if len(union_candidates) == n:
                        if n == 1:
                            # This is a cell with a single candidate.
                            for cell in cell_subset:
                                if fill:
                                    cell.fill(cell.candidates[0])
                                found_cells.append(cell)
                                if one_step:
                                    return found_cells
                        else:
                            # If the current unit is a box, and the naked subset cells all lie in one row or one column,
                            # then they "point" to that row or column. Thus, remove union_candidates from the entire row
                            # or column
                            if unit.startswith("box"):
                                rows_in_subset = {cell.row for cell in cell_subset}
                                cols_in_subset = {cell.col for cell in cell_subset}
                                if len(rows_in_subset) == 1:
                                    # Pointing row elimination: remove union_candidates from all cells in the row, except cell_subset
                                    for cell in [c for c in self.get_full_row(cell_subset[0]) if c not in cell_subset]:
                                        for cand in union_candidates:
                                            if cand in cell.candidates:
                                                cell.remove_candidates([cand])
                                                info_str = (
                                                    f"Due to a pointing naked subset {union_candidates} in {unit} "
                                                    f"confined to row {cell.row + 1}, the cell in row {cell.row + 1} "
                                                    f"column {cell.col + 1} cannot be {cand}")
                                                removed_candidates.append((cell, cell_subset, info_str))
                                                if one_step:
                                                    return removed_candidates
                                elif len(cols_in_subset) == 1:
                                    # Pointing column elimination: remove union_candidates from all cells in the col, except cell_subset
                                    for cell in [c for c in self.get_full_col(cell_subset[0]) if c not in cell_subset]:
                                        for cand in union_candidates:
                                            if cand in cell.candidates:
                                                cell.remove_candidates([cand])
                                                info_str = (
                                                    f"Due to a pointing naked subset {union_candidates} in {unit} "
                                                    f"confined to column {cell.col + 1}, the cell in row "
                                                    f"{cell.row + 1} column {cell.col + 1} cannot be {cand}")
                                                removed_candidates.append((cell, cell_subset, info_str))
                                                if one_step:
                                                    return removed_candidates
                            # Naked subset: eliminate these candidates from all other cells in the unit
                            for cell in [c for c in rcb if c not in cell_subset]:
                                # Only remove if the candidate is present
                                for cand in union_candidates:
                                    if cand in cell.candidates:
                                        cell.remove_candidates([cand])
                                        info_str = (
                                            f"Due to a naked subset {union_candidates} in {unit}, the cell in row "
                                            f"{cell.row + 1} column {cell.col + 1} cannot be {cand}"
                                        )
                                        removed_candidates.append((cell, cell_subset, info_str))
                                        if one_step:
                                            return removed_candidates
        if found_cells:
            return found_cells

        return removed_candidates

    def add_pair(self, c1: Cell, c2: Cell, val: int) -> list[tuple[Cell, list[Cell], str]]:
        """
           Adds a pair (c1, c2) with the associated value 'val' into the dictionary. Returns the cells where at least
           one candidate was removed from it due to the new pair.

           If the pair exists (in either order) with the same value, returns [] since no new cells were found.
           If the pair exists with a different value, val2, the pair of cells must be the digits val and val2 in some
           order.
           If no pair exists, adds the new pair

           In the latter cases, we check if the new pair has created an X-wing pattern, and return the cells where we
           are able to remove at least one candidate
        """
        removed_candidates = []
        key = (c1, c2)
        reverse_key = (c2, c1)
        _sentinel = object()
        current_val = self.pairs.get(key, self.pairs.get(reverse_key, _sentinel))

        def check_xwing():
            rmvd_candidates = []
            for existing_pair_key, existing_pair_val in self.pairs.items():
                cells = set(key + existing_pair_key)
                rows = {cell.row for cell in cells}
                cols = {cell.col for cell in cells}
                if val == existing_pair_val and len(rows) == 2 and len(cols) == 2 and len(cells) == 4:
                    # found x-wing pattern
                    cells_to_update = [
                        c for c in self.get_full_col(key[0]) +
                                   self.get_full_col(key[1]) +
                                   self.get_full_row(key[0]) +
                                   self.get_full_row(key[1]) if c not in cells and c.is_empty()
                    ]
                    for cell in cells_to_update:
                        if val in cell.candidates:
                            cell.remove_candidates([val])
                            info_str = (f"An X-wing in rows {tuple([r + 1 for r in rows])} and columns "
                                        f"{tuple([c + 1 for c in cols])} does not allow (r{cell.row + 1}, "
                                        f"c{cell.col + 1}) to be the digit {val}")
                            rmvd_candidates.append((cell, cells, info_str))
                    return rmvd_candidates
            return []

        if current_val is not _sentinel:
            # Pair already exists (in one of the orders)
            if current_val == val:
                # The pair has already been found
                return []
            else:
                # The pair exists but with a different digit, these two cells MUST be val and current_val
                candidates_to_remove = [cand for cand in range(1,10) if cand not in (current_val, val)]
                for cell in [c for c in [c1, c2] if any(cand in candidates_to_remove for cand in c.candidates)]:
                    info_str = (f"The pair of cells (r{c1.row + 1}, c{c1.col + 1}), (r{c2.row + 1}, c{c2.col + 1}) "
                                f"must contain the digits {current_val} and {val}, therefore (r{cell.row + 1}, "
                                f"c{cell.col + 1}) cannot be any other digit")
                    removed_candidates.append((cell, [c1 ,c2], info_str))  # at least one candidate will be removed from c1 and/or c2
                c1.remove_candidates(candidates_to_remove=candidates_to_remove)
                c2.remove_candidates(candidates_to_remove=candidates_to_remove)

                if removed_candidates:
                    return removed_candidates
                else:
                    return check_xwing()
        else:
            removed_candidates = check_xwing()
            self.pairs[key] = val  # Pair does not exist in either order, so add it
            return removed_candidates

    def check_ywing(self, one_step: bool = False) -> list[tuple[Cell, Cell, Cell, Cell, Cell]]:
        """Searches for Y-wing patterns across the puzzle. For each Y-wing that is found, return the pivot cell, its
        two wing cells, the value c, and the cell that can no longer have the value c as a candidate
        """
        removed_candidates = []
        doubles = [c for c in self.cells if len(c.candidates) == 2]  # any cell with exactly 2 candidates
        y_wings = []

        for pivot in doubles:
            pivot_cand_a, pivot_cand_b = pivot.candidates

            # WingA: must share a rcb with pivot AND share the candidate a, but NOT b
            wing_a_candidates = [c for c in doubles
                                 if c is not pivot and c.shares_unit(pivot)
                                 and pivot_cand_a in c.candidates and pivot_cand_b not in c.candidates]

            # WingB: must share a rcb with pivot AND share the candidate b, but NOT a
            wing_b_candidates = [c for c in doubles
                                 if c is not pivot and c.shares_unit(pivot)
                                 and pivot_cand_b in c.candidates and pivot_cand_a not in c.candidates]

            for wing_a in wing_a_candidates:
                # wing_a has candidates [a,c], we need wing_b such that it has candidates [b,c]
                c = wing_a.candidates[0] if wing_a.candidates[0] != pivot_cand_a else wing_a.candidates[1]
                for wing_b in wing_b_candidates:
                    # a, b, c are unique, thus if c is in wing_b.candidates, wing_a and wing_b form a Y-wing
                    if c in wing_b.candidates and not wing_a.shares_unit(wing_b):
                        y_wings.append((pivot, wing_a, wing_b, c))

        for y_wing in y_wings:
            # any cell that can see both wing_a and wing_b CANNOT have the value c, since one of A or B is c
            pivot, wingA, wingB, c = y_wing
            for cell in [c for c in self.cells if c.is_empty()]:
                if cell.shares_unit(wingA) and cell.shares_unit(wingB) and c in cell.candidates:
                    cell.remove_candidates([c])
                    removed_candidates.append((pivot, wingA, wingB, c, cell))
            if one_step and removed_candidates:
                return removed_candidates

        return removed_candidates

    def solve(self) -> None | list[Cell] | list[list[Cell]]:
        # returns a solved Sudoku board
        self.update_candidates([c for c in self.cells if not c.is_empty()])  # the whole board is new at the start
        invalid_cells, unfillable_cells = self._validate_input()
        if invalid_cells or unfillable_cells:
            return invalid_cells + unfillable_cells
        self._assign_board_to_cells()
        # repeat solving strategies until failure, then move to next, always restarting after a success

        while True:
            if self.board_solved():
                return self.board
            elif self.find_ntuples() or self.check_ywing() or self.find_ncandidates(max_n=8):
                continue
            else:
                # board could not be solved, return as much as was done
                return self.board

    def get_next_step(self, fill: bool = False) -> tuple[Cell, str] | list[Cell] | list[tuple[Cell, list[Cell], str]] | str | None:
        """
            Gets the next logical step in solving the puzzle

            fill: If True, fill in the found cell

            returns:
                - A list of cells if there are invalid and/or unfillable cells
                - A tuple (Cell, str) if a new cell can be filled
                - A list of tuples (Cell, list[Cell], str) if at least one cell has had candidates removed from it
                - A string if no next step could be found
        """
        self.update_candidates([c for c in self.cells if not c.is_empty()])
        invalid_cells, unfillable_cells = self._validate_input()
        if invalid_cells or unfillable_cells:
            return invalid_cells + unfillable_cells
        self._assign_board_to_cells()

        if not self.board_solved():
            if new_cells:= self.find_ncandidates(one_step=True, fill=fill):
                new_cell = new_cells[0]
                if type(new_cell) == Cell:
                    return new_cell, (f"{new_cell.value} is the only digit that can go in row {new_cell.row + 1}, column "
                                  f"{new_cell.col + 1}!")
                else:
                    return new_cells
            elif new_cell:= self.find_ntuples(one_step=True, fill=fill):
                new_c = new_cell[0]
                if type(new_c) == tuple:
                    # we have a list of tuples containing an updated cell, helper cells, and an info string
                    return new_cell
                else:
                    # since new_c is not a tuple, we must have a filled cell since its digit could not go anywhere else
                    # in rcb
                    rcb = new_cell[1]
                    if all(cell.row == new_c.row for cell in rcb):  # if new_c is in the row rcb
                        rcb = f"row {new_c.row + 1}"
                        position = f"column {new_c.col + 1}"
                    elif all(cell.col == new_c.col for cell in rcb):  # if new_c is in the col rcb
                        rcb = f"col {new_c.col + 1}"
                        position = f"row {new_c.row + 1}"
                    else:  # new_c is in the box rcb
                        rcb = f"box {new_c.box}"
                        position = f"row {new_c.row + 1}, column {new_c.col + 1}"
                    return new_c, f"The only cell in {rcb} where {new_c.value} can go is {position}"
            elif new_cells:= self.check_ywing(one_step=True):
                update_packages = []
                for cell in new_cells:
                    pivot = cell[0]
                    wingA = cell[1]
                    wingB = cell[2]
                    c = cell[3]
                    updated_cell = cell[4]
                    return_str = (f"{c} can no longer go in (r{updated_cell.row + 1}, c{updated_cell.col + 1}) "
                                  f"due to a Y-wing pattern with a pivot at (r{pivot.row + 1}, c{pivot.col + 1}) "
                                  f"which forces one of (r{wingA.row + 1}, c{wingA.col + 1}) and "
                                  f"(r{wingB.row + 1}, c{wingB.col + 1}) to be the digit {c}!")
                    update_packages.append((updated_cell, [pivot, wingA, wingB], return_str))
                return update_packages
            else:
                return "No next cell could be found for the given configuration, ensure the board is unique!"

    def board_solved(self) -> bool:
        if self.solved or all([sorted([cell.value for cell in rcb]) == list(range(1,10)) for rcb in (
            self.get_all_rows() + self.get_all_cols() + self.get_all_boxes()
        )]):
            self.solved = True
            return True
        else:
            return False

    def __str__(self):
        return str(np.matrix([[cell.value for cell in row] for row in self.board]))

