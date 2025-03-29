"""
board.py

This module implements the core Sudoku logic including board creation, candidate management,
and solving strategies such as naked subsets, n-tuples, X-wing, and Y-wing techniques.
The Sudoku class encapsulates the board state and provides methods to update the board,
validate input, and apply solving strategies.
"""

import itertools
import numpy as np
from cell import Cell


class Sudoku:
    """
    Represents a Sudoku puzzle and provides methods for board manipulation and solving.

    Attributes:
        board (list[list[Cell]]): A 9x9 grid of Cell instances representing the Sudoku board; each list[Cell] is a row
        board_assigned_to_cells (bool): Flag indicating if the board has been assigned to each cell.
        cells (list[Cell]): Flattened list of all Cell instances from the board.
        cols (list[list[Cell]] | None): List of columns; each column is a list of Cell instances.
        boxes (list[list[Cell]] | None): List of 3x3 boxes; each box is a list of Cell instances.
        solved (bool): Indicates whether the board is solved. The value is saved so it isn't rechecked once True
        pairs (dict): Dictionary for tracking cell pairs and their associated candidate values. A pair is defined to be
        two cells in a row, column, or box where a digit must go
    """
    def __init__(self, board: list[list[Cell]]):
        """
        Initialize a new Sudoku instance with a given board.

        Args:
            board (list[list[Cell]]): A 2D list of Cell instances representing the initial Sudoku board.
        """
        self.board = board
        self.board_assigned_to_cells = False
        self.cells = [c for row in self.board for c in row]
        self.cols = None
        self.boxes = None
        self.solved = False
        self.pairs = {}

    @staticmethod
    def make_sudoku(list_of_rows: list[list[int]]) -> "Sudoku":
        """
        Create a Sudoku instance from a list of rows containing integer values.

        Each integer represents the initial value of a cell (0 indicates an empty cell).

        Args:
            list_of_rows (list[list[int]]): A 2D list of integers representing the Sudoku board.

        Returns:
            Sudoku: A new Sudoku instance with the corresponding Cell objects.
        """
        board = []
        for r in range(len(list_of_rows)):  # iterate through the number of rows
            row = []
            for c in range(len(list_of_rows[r])):  # iterate through the number of columns
                row.append(Cell(c=c, r=r, value=list_of_rows[r][c]))
            board.append(row)
        return Sudoku(board=board)

    def update_sudoku(self, list_of_rows: list[list[int]]) -> list[Cell] | None:
        """
        Update the Sudoku instance based on any changes made by the user.

        This method synchronizes the Sudoku board with the new input values from the UI.
        It updates each cell accordingly and resets candidates if necessary.
        If invalid or unfillable cells are detected, those cells are returned.

        Args:
            list_of_rows (list[list[int]]): A 2D list of integers representing the new board state.

        Returns:
            list[Cell] | None: A list of cells that are invalid or unfillable, or None if no issues are found.
        """
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
        """
        Reset the candidates for each unfilled cell back to the default range (1-9).

        After resetting, the method updates candidates based on the current filled cells.
        """
        for cell in [c for c in self.cells if c.is_empty()]:
            cell.candidates = list(range(9))
        self.update_candidates([c for c in self.cells if not c.is_empty()])

    def _assign_board_to_cells(self) -> None:
        """
        Assign the current Sudoku instance (board) to each cell if not already assigned.

        This ensures that each cell has a reference to the board it belongs to.
        """
        if not self.board_assigned_to_cells:
            for c in self.cells:
                c.set_board(self)
            self.board_assigned_to_cells = True

    def _validate_input(self) -> tuple[list[Cell], list[Cell]]:
        """
        Validate the current board input for Sudoku rule violations.

        Checks each row, column, and box for duplicate values and cells with no possible candidates.
        Invalid cells or cells that cannot be filled are returned.

        Returns:
            tuple[list[Cell], list[Cell]]:
                - The first list contains invalid cells.
                - The second list contains cells that are unfillable, i.e. there is no digit that fits in the cell.
        """
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
        """
        Return the full row of cells that the specified cell belongs to.

        Args:
            cell (Cell): The reference cell.

        Returns:
            list[Cell]: A list of Cell instances in the same row.
        """
        return self.board[cell.row]

    def get_full_col(self, cell: Cell) -> list[Cell]:
        """
        Return the full column of cells that the specified cell belongs to.

        Args:
            cell (Cell): The reference cell.

        Returns:
            list[Cell]: A list of Cell instances in the same column.
        """
        return [row[cell.col] for row in self.board]

    def get_full_box(self, cell: Cell) -> list[Cell]:
        """
        Return the full box of cells that the specified cell belongs to.

        Args:
            cell (Cell): The reference cell.

        Returns:
            list[Cell]: A list of Cell instances in the same box.
        """
        return [c for c in self.cells if c.box == cell.box]

    def get_all_rows(self) -> list[list[Cell]]:
        """
        Retrieve all rows of the Sudoku board.

        Returns:
            list[list[Cell]]: The board represented as a list of rows.
        """
        return self.board

    def get_all_cols(self) -> list[list[Cell]]:
        """
        Retrieve all columns of the Sudoku board. Stores the result in self.cols so we don't have to loop again

        Returns:
            list[list[Cell]]: The board represented as a list of columns.
        """
        if not self.cols:
            self.cols = [[row[col] for row in self.board] for col in list(range(9))]
        return self.cols

    def get_all_boxes(self) -> list[list[Cell]]:
        """
        Retrieve all boxes of the Sudoku board. Stores the result in self.boxes so we don't have to loop again

        Returns:
            list[list[Cell]]: The board represented as a list of boxes.
        """
        if not self.boxes:
            self.boxes = []
            for row_num in list(range(3)):
                for col_num in list(range(3)):
                     self.boxes.append(self.get_full_box(self.get_cell_from_cord(row_num=row_num*3, col_num=col_num*3)))
        return self.boxes

    def get_cell_from_cord(self, row_num: int, col_num: int) -> Cell:
        """
        Get a cell from the board instance based on its row and column coordinates.

        Args:
            row_num (int): The row number (0-indexed).
            col_num (int): The column number (0-indexed).

        Returns:
            Cell: The cell at the specified coordinates.
        """
        return self.cells[row_num * 9 + col_num]

    def update_candidates(self, new_cells: list[Cell]) -> None:
        """
        Update candidate digits for cells based on new cell values.

        For each new cell provided, remove its value from the candidates of all cells in its row, column, and box.

        Args:
            new_cells (list[Cell]): A list of cells that have been filled.
        """
        for new_cell in new_cells:
            cells_to_update = list(set(
                self.get_full_row(new_cell) + self.get_full_col(new_cell) + self.get_full_box(new_cell)
            ))
            cells_to_update.remove(new_cell)  # unique list not including the new cell itself
            for c in [ce for ce in cells_to_update if ce.is_empty()]:
                c.remove_candidates([new_cell.value])

    def find_ntuples(self, one_step: bool = False, fill: bool = True) -> list[Cell | list[Cell]] | list[Cell, list[Cell], str] | None:
        """
        Find n-tuple patterns in rows, columns, or boxes where a digit must go.

        This method first attempts to find cells where a digit has only one possible location in a row, column or box.
        If such a scenario is found, the cells are filled. Otherwise, it searches for
        n-tuple candidate patterns that allow candidate elimination.

        Args:
            one_step (bool): If True, return after the first logical deduction.
            fill (bool): If True, fill in the cell with the determined digit.

        Returns:
            list[Cell] | list[Cell, list[Cell], str] | None:
            Either a list of filled cells, a list of tuples with elimination info, or None if no deductions were made.
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

    def find_ncandidates(self, one_step: bool = False, fill: bool = True, min_n: int = 1, max_n: int = 3) -> (
            list[Cell] | list[tuple[Cell, list[Cell], str]]):
        """
        Find naked candidate subsets (n-candidates) within rows, columns, or boxes.

        A naked subset is found when a group of n empty cells in a unit have a union of candidates
        exactly of size n. In such a case, these candidates can be eliminated from all other cells in the unit.
        Additionally, if the naked subset is in a box and confined to one row or column (pointing technique),
        the candidates can be eliminated from the entire row or column.

        Args:
            one_step (bool): If True, return after the first deduction.
            fill (bool): If True, fill the cell when a single candidate is found.
            min_n (int): Minimum number of cells to consider in a subset.
            max_n (int): Maximum number of cells to consider in a subset.

        Returns:
            list[Cell] | list[tuple[Cell, list[Cell], str]]:
            Either a list of filled cells, or a list of tuples containing
            the cell updated, the naked subset, and an explanation string.
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
            for n in range(min_n, max_n + 1):
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
        Add a pair of cells with an associated candidate value and apply X-wing elimination if applicable.

        This method adds the pair (c1, c2) to the internal dictionary of pairs. If the pair already exists
        with the same value, no new candidates are removed. If the pair exists with a different value,
        candidates that are not part of the pair are removed from the cells since c1 and c2 must be exactly
        those two values. It also checks for and applies the X-wing strategy based on existing pairs.

        Args:
            c1 (Cell): The first cell of the pair.
            c2 (Cell): The second cell of the pair.
            val (int): The value that must be contained in one of c1 or c2.

        Returns:
            list[tuple[Cell, list[Cell], str]]:
            A list of tuples where each tuple contains a cell from which
            a candidate was removed, the pair of cells involved, and an explanatory string.
        """
        removed_candidates = []
        key = (c1, c2)
        reverse_key = (c2, c1)
        _sentinel = object()
        current_val = self.pairs.get(key, self.pairs.get(reverse_key, _sentinel))

        def check_xwing() -> list[tuple[Cell, list[Cell], str]]:
            """
            Identifies and applies the X-Wing pattern in a Sudoku grid to eliminate invalid candidates.

            The X-Wing pattern occurs when a digit appears in exactly two cells in two separate rows
            and those cells are aligned in the same two columns (or vice versa with columns and rows).
            This forms a rectangle of four cells, where the digit must be placed in one of the two
            cells in each row (or column), effectively locking its position.

            Since the digit must occupy one of these positions in each row (or column), it cannot
            appear elsewhere in those rows (or columns). This allows us to eliminate the digit from
            other candidates in the affected rows and columns.

            Returns:
                list[tuple[Cell, list[Cell], str]]:
                A list of tuples, each containing:
                    - The cell where a candidate was removed.
                    - The set of four cells forming the X-Wing pattern.
                    - A string describing the reason for removal.
            """
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

    def check_ywing(self, one_step: bool = False) -> list[tuple[Cell, Cell, Cell, int, Cell]]:
        """
        Search for Y-Wing patterns in the puzzle and eliminate invalid candidates.

        The Y-Wing pattern is a type of chain that involves three cells, where:
        - A "pivot" cell contains exactly two candidates (X and Y).
        - Two "wing" cells, each sharing one candidate with the pivot, and one with each other (X-Z and Y-Z).
        - The wing cells do not share a row, column, or box with each other

        Since the pivot cell must contain either X or Y, one of the wing cells must contain Z.
        Therefore, any other cell that shares a unit with both wing cells cannot contain Z, allowing
        for candidate elimination.

        Args:
            one_step (bool): If True, return after the first Y-Wing deduction.

        Returns:
            list[tuple[Cell, Cell, Cell, Cell, int]]:
            A list of tuples containing:
                - The pivot cell.
                - The first wing cell.
                - The second wing cell.
                - The cell from which a candidate is removed.
                - The eliminated candidate value.
        """
        removed_candidates = []
        doubles = [c for c in self.cells if len(c.candidates) == 2]  # any cell with exactly 2 candidates
        y_wings = []

        for pivot in doubles:
            pivot_cand_x, pivot_cand_y = pivot.candidates

            # WingX: must share a rcb with pivot AND share the candidate x, but NOT y
            wing_x_candidates = [c for c in doubles
                                 if c is not pivot and c.shares_unit(pivot)
                                 and pivot_cand_x in c.candidates and pivot_cand_y not in c.candidates]

            # WingY: must share a rcb with pivot AND share the candidate y, but NOT x
            wing_y_candidates = [c for c in doubles
                                 if c is not pivot and c.shares_unit(pivot)
                                 and pivot_cand_y in c.candidates and pivot_cand_x not in c.candidates]

            for wing_x in wing_x_candidates:
                # wing_x has candidates [x,z], we need wing_y such that it has candidates [y,z]
                z = wing_x.candidates[0] if wing_x.candidates[0] != pivot_cand_x else wing_x.candidates[1]
                for wing_y in wing_y_candidates:
                    # x, y, z are unique, thus if z is in wing_y.candidates, wing_x and wing_y form a Y-wing
                    if z in wing_y.candidates and not wing_x.shares_unit(wing_y):
                        y_wings.append((pivot, wing_x, wing_y, z))

        for y_wing in y_wings:
            # any cell that can see both wing_x and wing_y CANNOT have the value z, since one of X or Y is z
            pivot, wingx, wingy, z = y_wing
            for cell in [c for c in self.cells if c.is_empty()]:
                if cell.shares_unit(wingx) and cell.shares_unit(wingy) and z in cell.candidates:
                    cell.remove_candidates([z])
                    removed_candidates.append((pivot, wingx, wingy, z, cell))
            if one_step and removed_candidates:
                return removed_candidates

        return removed_candidates

    def solve(self) -> list[Cell] | list[list[Cell]]:
        """
        Solve the Sudoku puzzle using available strategies.

        The method first updates candidates and validates the input. It then repeatedly applies
        solving strategies (n-tuple finding, Y-wing, and naked candidate elimination) until the board
        is solved or no further progress can be made.

        Returns:
            list[Cell] | list[list[Cell]]:
                - A solved board if successful.
                - A list of cells if there are invalid or unfillable cells.
                - Otherwise, the board state after exhausting solving strategies.
        """
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
        Get the next logical step in solving the puzzle.

        This method updates candidates, validates input, and then attempts to find the next move
        using various strategies. Depending on the deduction, it returns one of the following:
          - A tuple (Cell, str) if a new cell can be filled with an explanation.
          - A list of cells if invalid or unfillable cells are found.
          - A list of tuples (Cell, list[Cell], str) if candidate elimination occurred.
          - A string if no logical next step can be determined.
          - None if the board is already solved.

        Args:
            fill (bool): If True, fill in the found cell with the deduced digit.

        Returns:
            tuple[Cell, str] | list[Cell] | list[tuple[Cell, list[Cell], str]] | str | None: The next step information.
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
            elif new_cells:= self.find_ncandidates(one_step=True, fill=fill, min_n=4, max_n=8):
                new_cell = new_cells[0]
                if type(new_cell) == Cell:
                    return new_cell, (f"{new_cell.value} is the only digit that can go in row {new_cell.row + 1}, column "
                                  f"{new_cell.col + 1}!")
                else:
                    return new_cells
            else:
                return "No next step could be found for the given configuration, ensure the board is unique!"

    def board_solved(self) -> bool:
        """
        Check if the Sudoku board is solved.

        The board is considered solved if every row, column, and box contains the digits 1 through 9 exactly once.

        Returns:
            bool: True if the board is solved, False otherwise.
        """
        if self.solved or all([sorted([cell.value for cell in rcb]) == list(range(1,10)) for rcb in (
            self.get_all_rows() + self.get_all_cols() + self.get_all_boxes()
        )]):
            self.solved = True
            return True
        else:
            return False

    def __str__(self) -> str:
        """
        Return a string representation of the Sudoku board.

        The board is formatted as a NumPy matrix with each cell's value.

        Returns:
            str: The string representation of the board.
        """
        return str(np.matrix([[cell.value for cell in row] for row in self.board]))

