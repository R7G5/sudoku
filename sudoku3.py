import time
import copy
# import sys
import itertools


class Cell:

    def __init__(self, row, col, value=0):
        self.value = value  # current value
        self.solved = False  # this cell is solved
        self.given = False  # initial given
        self.exceptions = []  # list of values not allowed in cell due to position
        self.candidates = []  # list of possible values
        self.row = row
        self.col = col
        self.box = self.getBoxNum(row, col)

    @staticmethod
    def getBoxNum(row, col):
        box = 0
        if row in [0, 1, 2]:
            if col in [0, 1, 2]:
                box = 1
            if col in [3, 4, 5]:
                box = 2
            if col in [6, 7, 8]:
                box = 3

        if row in [3, 4, 5]:
            if col in [0, 1, 2]:
                box = 4
            if col in [3, 4, 5]:
                box = 5
            if col in [6, 7, 8]:
                box = 6

        if row in [6, 7, 8]:
            if col in [0, 1, 2]:
                box = 7
            if col in [3, 4, 5]:
                box = 8
            if col in [6, 7, 8]:
                box = 9
        return box

    def setCellValue(self, value):
        self.value = value
        self.solved = True
        self.exceptions = []  # [1, 2, 3, 4, 5, 6, 7, 8, 9]  #self.exceptions.remove(value)
        self.candidates = []

    def RemoveCellExceptions(self, exceptions):  # removes provided exceptions
        for exception in exceptions:
            self.exceptions.remove(exception)


class Grid:

    def __init__(self, puzzle):
        self.board = []  # array of boards
        self.CurrentBoard = copy.deepcopy(puzzle)  # simple array representation of the board
        self.moves = []  # list of moves r3c1=9 (assing), r4c9-4 (remove candidate), r8c1+1379 (add candidates), r347c4-6 (remove candidates
        self.twinList = {}  # list of identical possibilities per row or col.
        # key = tuple of possible numbers
        # value = list of touple coordinates
        for i in range(0, 9):
            self.board.append([])  # create new row
            for j in range(0, 9):
                self.board[i].append(Cell(row=i, col=j, value=puzzle[i][j]))  # copy the value to the cell
                self.board[i][j].solved = puzzle[i][j] != 0  # Marked solved if not 0
        self.RecalculateAllCandidates()

    def setGivens(self, givens):
        # Sample format: 6....23..1256.......47...2.73....84...........46....15.5...81.......3472..72....8
        x = 0
        for i in range(0, 9):
            for j in range(0, 9):
                self.board[i][j].value = givens[x]
                self.board[i][j].given = True
                x += 1

    def getGivens(self):
        # Sample format:  6....23..1256.......47...2.73....84...........46....15.5...81.......3472..72....8
        res = ""
        for i in range(0, 9):
            for j in range(0, 9):
                res += str(self.board[i][j].value) if self.board[i][j].value != 0 else "."
        return res

    # Coordinates method
    @staticmethod
    def getHouseRow_coordinates(cell_coord):  # get list of house row coordinates. param (r,c)
        return [(cell_coord[0], clm) for clm in range(0, 9)]  # if clm !=cell.col ] # excluding current cell

    @staticmethod
    def getHouseCol_coordinates(cell_coord):  # get list of house col coordinates
        return [(rw, cell_coord[1]) for rw in range(0, 9)]  # if rw !=cell.row ] # , excluding current cell

    @staticmethod
    def getHouseBox_coordinates(boxnum):
        rows, cols = [], []

        if boxnum in [1, 2, 3]:
            rows = [0, 1, 2]
        elif boxnum in [4, 5, 6]:
            rows = [3, 4, 5]
        elif boxnum in [7, 8, 9]:
            rows = [6, 7, 8]

        if boxnum in [1, 4, 7]:
            cols = [0, 1, 2]
        elif boxnum in [2, 5, 8]:
            cols = [3, 4, 5]
        elif boxnum in [3, 6, 9]:
            cols = [6, 7, 8]

        return [(r, c) for r in rows for c in cols]
        # [(x,c) for x in range(0,5) if x !=3 for c in range(0,5) if c !=3]

    # Candidate methods
    def getAllCandidates(self):
        # Returns list of candidates in multi-row text foramat. Could be pasted in most sudoku apps
        res = ""
        for i in range(0, 9):
            for j in range(0, 9):
                cur = self.board[i][j].candidates if self.board[i][j].candidates else [self.board[i][j].value]
                cur.sort()
                res += "".join([str(elem) for elem in cur]) + " "
            res += "\n"
        return res

    def getBoxRowCandidates(self, cell):
        ROW, COL = 0, 1
        houseCoords = self.getHouseBox_coordinates(cell.box)  # get list cell coordinates of the box
        cols = [coord[COL] for coord in houseCoords if coord[ROW] == cell.row]  # extract column numbers

        # assemble list of candidates from the row,col(n)
        cand = [self.board[cell.row][col].candidates for col in cols if len(self.board[cell.row][col].candidates) != 0]
        cand = [item for items in cand for item in items]  # expand list into single list
        return cand

    def getBoxColCandidates(self, cell):
        ROW, COL = 0, 1
        houseCoords = self.getHouseBox_coordinates(cell.box)  # get list cell coordinates of the box
        rows = [coord[ROW] for coord in houseCoords if coord[COL] == cell.col]  # extract row numbers

        # assemble list of candidates from the row(n),col
        cand = [self.board[row][cell.col].candidates for row in rows if len(self.board[row][cell.col].candidates) != 0]
        cand = [item for items in cand for item in items]  # expand list into single list
        return cand

    # Solve methods
    def solveBy_LockedCandidateType1(self):
        # Locked Candidates Type 1(Pointing)
        #   If in a box all candidates of a certain digit are confined to a row or column,
        #   that digit cannot appear outside of that box in that row or column.

        # Structure used to re-group find candidates that reside in the same row or col
        # { candidate# :
        #               {
        #                   coordinates: [(x1,y1),(x1,y2])
        #                   matchBy    : [False, True]      # [IsRow,IsCol]
        #               }
        # }

        ROW, COL = 0, 1
        changesMade = False

        for box in range(1, 10):  # for each box 1..9 (ignoring 0)

            coords = self.getHouseBox_coordinates(box)  # get list of box cells
            confined_box_candidates = {}

            for coord in coords:
                currentCell = self.board[coord[ROW]][coord[COL]]

                if not currentCell.solved:  # if cell is not solved

                    for candidate in currentCell.candidates:  # look for candidates that are confined to a row or column

                        if candidate not in confined_box_candidates:  # if candidate is not already in the list
                            confined_box_candidates[candidate] = {}
                            confined_box_candidates[candidate]["coordinates"] = [coord]  # Add newly found to the list
                            confined_box_candidates[candidate]["matchBy"] = [False, False]
                            continue
                        elif (-1, -1) in confined_box_candidates[candidate]["coordinates"]:
                            continue

                        tmp_lst = confined_box_candidates[candidate]["coordinates"].copy()  # copy candiata coordinates
                        tmp_lst.append(coord)  # add current coordinates

                        # Unzip coord list [(r1,c1),(r2,c2),...(rN,cN)] to [(r1,r1,...rN),(c1,c2,...cN)]
                        # Convert each tuple to set() to eliminate duplicates. If single element left then all were the same.
                        # Returns [True, False] if all ROW indexes match, [False, True] for Column
                        RowOrColmatch = [len(set(elem)) == 1 for elem in zip(*tmp_lst)]

                        if any(RowOrColmatch):
                            if (-1, -1) not in confined_box_candidates[candidate]["coordinates"]:  # if not set to be ignored
                                confined_box_candidates[candidate]["coordinates"] += [coord]   # good candidate, add coord to the list
                                confined_box_candidates[candidate]["matchBy"] = RowOrColmatch
                        else:
                            confined_box_candidates[candidate]["coordinates"] = [(-1, -1)]  # Ignore this canddate
                            confined_box_candidates[candidate]["matchBy"] = [False, False]  # [Row,Col]

            # Remove all items containing (0,0)
            confined_box_candidates = {key: value for (key, value) in confined_box_candidates.items() if
                                       (-1, -1) not in value["coordinates"]}
            print("DEBUG: Box %s confined_box_candidates: %s" % (box, confined_box_candidates))

            for candidate in confined_box_candidates:
                if confined_box_candidates[candidate]["matchBy"][ROW]:
                    cells = self.getHouseRow_coordinates(confined_box_candidates[candidate]["coordinates"][0])
                elif confined_box_candidates[candidate]["matchBy"][COL]:
                    cells = self.getHouseCol_coordinates(confined_box_candidates[candidate]["coordinates"][0])
                else:
                    continue

                # remove cells where confined candidate resides
                cells = [elem for elem in cells if elem not in confined_box_candidates[candidate]["coordinates"]]

                # remove confined candidate from other cells in the row or col
                candidate_diff = []
                for cell in cells:
                    if self.board[cell[ROW]][cell[COL]].solved:
                        continue
                    new_candidates = [elem for elem in self.board[cell[ROW]][cell[COL]].candidates if elem != candidate]
                    candidate_diff += list(set(self.board[cell[ROW]][cell[COL]].candidates) ^ set(new_candidates))
                    self.board[cell[ROW]][cell[COL]].candidates = new_candidates
                    changesMade = changesMade or candidate_diff != []  # if not equal empty list
                print("       removed candidates: %s" % (list(candidate_diff)))

        return changesMade

    def solveBy_LockedCandidatesType2(self):

        # Locked Candidates Type 2 (Claiming)
        #   If in a row (or column) all candidates of a certain digit are confined to one box,
        #   that candidate can be eliminated from all other cells in that box.

        # Structure used to re-group find candidates that reside in the same row or col
        # { candidate# :
        #               {
        #                   box         : []
        #                   coordinates : [(x1,y1),(x1,y2])
        #                   matchBy     : [False, True]      # [IsRow,IsCol]
        #               }
        # }

        ROW, COL = 0, 1

        changesMade = False

        for i in range(0, 9):
            for j in range(0, 9):

                if self.board[i][j].solved:  # skip if solved
                    continue

                currentCell = self.board[i][j]

                for candidate in currentCell.candidates:  # get next candidate

                    # save current candidate
                    current_candidate = {candidate: {}}
                    current_candidate[candidate]["box"] = [currentCell.box]
                    current_candidate[candidate]["coordinates"] = [(i, j)]

                    confined_box_candidates = copy.deepcopy(current_candidate)

                    # Check all cells in the ROW
                    for col in range(0, 9):
                        if col == j:  # skip if it's the same cell
                            continue

                        if candidate in self.board[i][col].candidates:

                            if self.board[i][j].solved:  # skip if solved
                                continue

                            if candidate not in confined_box_candidates:  # if candidate is not already in the list
                                confined_box_candidates[candidate] = {}
                                confined_box_candidates[candidate]["box"] = [self.board[i][col].box]
                                confined_box_candidates[candidate]["coordinates"] = [(i, col)]
                            else:
                                if self.board[i][col].box not in confined_box_candidates[candidate]["box"]:
                                    confined_box_candidates = {}  # copy.deepcopy(current_candidate)
                                    break  # stop looping COL cells for this candidate
                                else:  # add if its the same box
                                    confined_box_candidates[candidate]["coordinates"].append((i, col))

                    if confined_box_candidates:  # if found

                        coords = self.getHouseBox_coordinates(currentCell.box)  # get list of box cells

                        for coord in coords:
                            if coord in confined_box_candidates[candidate]['coordinates']:
                                continue  # skip if original cell with candidate

                            if self.board[coord[ROW]][coord[COL]].solved:
                                continue  # skip if solved cell

                            cell_candidates = set(
                                self.board[coord[ROW]][coord[COL]].candidates)  # set of currnet cell candidates
                            conf_candidates = confined_box_candidates.keys()  # set of confined candidates

                            if candidate in cell_candidates:
                                self.board[coord[ROW]][coord[COL]].candidates = list(
                                    cell_candidates - conf_candidates)  # remove configned from cell candidates
                                changesMade = changesMade or True
                        continue  # go to the next candidate

                    # save current candidate
                    current_candidate = {candidate: {}}
                    current_candidate[candidate]["box"] = [currentCell.box]
                    current_candidate[candidate]["coordinates"] = [(i, j)]

                    confined_box_candidates = copy.deepcopy(current_candidate)

                    # Check all cells in the COL
                    for row in range(0, 9):
                        if row == i:  # skip if it's the same cell
                            continue

                        if candidate in self.board[row][j].candidates:

                            if self.board[i][j].solved:  # skip if solved
                                continue

                            if candidate not in confined_box_candidates:  # if candidate is not already in the list
                                confined_box_candidates[candidate] = {}
                                confined_box_candidates[candidate]["box"] = [self.board[row][j].box]
                                confined_box_candidates[candidate]["coordinates"] = [(row, j)]
                            else:
                                if self.board[row][j].box not in confined_box_candidates[candidate]["box"]:
                                    confined_box_candidates = {}  # copy.deepcopy(current_candidate)
                                    break  # stop looping cells for this candidate
                                else:  # add if its the same box
                                    confined_box_candidates[candidate]["coordinates"].append((row, j))

                    if confined_box_candidates:  # if found
                        # Remove candidate from all other cells in the box

                        coords = self.getHouseBox_coordinates(currentCell.box)  # get list of box cells

                        for coord in coords:
                            if coord in confined_box_candidates[candidate]['coordinates']:
                                continue  # skip if original cell with candidate

                            if self.board[coord[ROW]][coord[COL]].solved:
                                continue  # skip if solved cell

                            cell_candidates = set(
                                self.board[coord[ROW]][coord[COL]].candidates)  # set of currnet cell candidates
                            conf_candidates = confined_box_candidates.keys()  # set of confined candidates

                            if candidate in cell_candidates:
                                self.board[coord[ROW]][coord[COL]].candidates = list(
                                    cell_candidates - conf_candidates)  # remove configned from cell candidates
                                changesMade = changesMade or True
                        continue  # go to the next candidate

        return changesMade

    def solveBy_NakedTriple(self):  # ToDo: Work on Grid.solveBy_NakedTriple method

        """
         If you can find three cells, all in the same house, that have only the same three candidates left,
         you can eliminate that candidates from all other cells in that house. It is important to note
         that not all cells must contain all three candidates, but there must not be more than three
         candidates in the three cells all together.
         Ref: http://hodoku.sourceforge.net/en/tech_naked.php#n3

         Example:

           General rules:
           - Ignore all cells with more than 3 candidates
           - There should be only three cells
           - Cells should have same 3 candidates
           - Not all of 3 cells must have all candidates

           Method:
            Building table of house candidates. Then verifying each triplet of candidates using following rule
            Each triplet member must share cell with two other members. The end cell list must have 3 unique cells.

            candidate_matrix:
            1 : (0,0) (0,1)
            2 :             (0,2) (0,5)
            4 :                   (0,5) (0,7)
            7 :       (0,1) (0,2)       (0,7)
            9 : (0,0) (0,1)

            candidate_final:
            (1,2,4)                         (1,7,9)                        (2,4,7)
            1 & 2 share 0 cells             1 & 7 share (0,1)               2 & 4 share (0,5)
            1 & 4 share 0 cells             1 & 9 share (0,0) (0,1)         2 & 7 share (0,2)
            2 & 4 share (0,5)               7 & 9 share (0,1)               4 & 7 share (0,7)
            Total unique shared cells       Total unique shared cells 2     Total unique shared cells 3
            across this triplet is 1        (0,0) & (0,1).
            It is less that required 3      It is less that required 3      This tripled meets requirement!
            Discard triplet                 Discard triplet                 Keep triplet
        """

        ROW, COL = 0, 1  # row and col corrdinate positions for better code readability

        # ToDo: Loop through each cell and check each house cell belonws too (Row,Col,Box)

        coords = self.getHouseRow_coordinates((0, 0))  # get list of House-Row coordinates

        all_candidates = []  # list of all house cell candidates
        candidate_matrix = {}  # matrix of eligible candidates and cells
        candidate_final = {}  # final list for NakedTriple

        for coord in coords:  # iterate each house coordinate
            if 0 < len(self.board[coord[ROW]][coord[COL]].candidates) <= 3:  # allow cells with 2 or 3 candidates
                currnet_candidates = self.board[coord[ROW]][coord[COL]].candidates  # read current candidates
                all_candidates.append(currnet_candidates)  # add to the list of all candidates

                for cand in currnet_candidates:  # iterate all current candidates
                    if cand not in candidate_matrix.keys():  # and build candidate_matrix
                        candidate_matrix[cand] = []
                    candidate_matrix[cand].append(coord)

        all_candidates = [item for items in all_candidates for item in
                          items]  # [[1,2],[3,4]]=[1,2,3,4] make a flat list
        unique_candidates = list(set(all_candidates))  # keep only unique numbers

        for current_triple in itertools.combinations(unique_candidates, 3):  # iterate by triples (1, 7, 9),...
            for pair in itertools.combinations(current_triple, 2):  # iterate by pairs (1, 7),(1, 9),(7, 9)

                a = candidate_matrix[pair[0]]  # read first pair member
                b = candidate_matrix[pair[1]]  # read second pair member

                res = list(set(a) & set(b))  # is there common cell?
                if not res:
                    break  # if no common cells then break and skip to next triple
                else:  # if there are a common cells
                    if current_triple not in candidate_final.keys():  # if not in the dictionary yet
                        candidate_final[current_triple] = []  # add key and empty list value
                    candidate_final[current_triple].append(res)  # append to the final list for now

            if current_triple in candidate_final.keys():  # if key exists
                candidate_final[current_triple] = [item for items in candidate_final[current_triple] for item in
                                                   items]  # make list flat
                if len(set(candidate_final[current_triple])) < 3:  # are there less than 3 cells?
                    candidate_final.pop(current_triple, "")  # remove triple

        for cand in candidate_final:  # iterare all house coordinates
            coords = list(set(coords) - set(candidate_final[cand]))  # only keep cells that are not in candidate_final

        for coord in coords:  # iterate remaining candidates
            for triplet in candidate_final:  # iterate all triplets
                # Remove candidates that are in candidate_final.keys()
                self.board[coord[ROW]][coord[COL]].candidates = \
                    list(set(self.board[coord[ROW]][coord[COL]].candidates) - set(triplet))

        return False

    def getBoardSnapshot(self):  # returns an array copy of the grid
        tmp = copy.deepcopy(self.CurrentBoard)
        return tmp

    def getColValues(self, col):  # returns list of values from the Col where provided cell resides
        tmp = []
        for i in range(0, 9):
            tmp.append(self.board[i][col].value)
        return tmp

    def getRowValues(self, row):  # returns list of values from the Row where provided cell resides
        tmp = []
        for j in range(0, 9):
            tmp.append(self.board[row][j].value)
        return tmp

    def getBoxValues(self, row, col):  # returns list of values from the Box where provided cell resides

        b_row, b_col = 0, 0

        if row in range(0, 3):
            b_row = 0
        elif row in range(3, 6):
            b_row = 3
        elif row in range(6, 9):
            b_row = 6

        if col in range(0, 3):
            b_col = 0
        elif col in range(3, 6):
            b_col = 3
        elif col in range(6, 9):
            b_col = 6

        tmp = []
        for i in range(b_row, b_row + 3):
            for j in range(b_col, b_col + 3):
                tmp.append(self.board[i][j].value)
        return tmp

    def setCellExceptions(self, row=0, col=0):
        exceptionList = set(self.getBoxValues(row, col) + self.getColValues(col) + self.getRowValues(
            row))  # create unique list of candidates
        exceptionList = [elem for elem in exceptionList if elem != 0]  # remove all zeros
        self.board[row][col].exceptions = exceptionList
        return exceptionList

    def setCellCandidates(self, row=0, col=0):
        allNumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        exceptionList = self.setCellExceptions(row, col)  # set and return cell exceptions
        candidateList = list(set(allNumbers) - set(exceptionList))
        candidateList.sort()
        self.board[row][col].candidates = candidateList
        return candidateList  # list of numbers not in exception list

    def RecalculateAllCandidates(self):
        for i in range(0, 9):
            for j in range(0, 9):
                if not self.board[i][j].solved:
                    self.setCellCandidates(i, j)  # candidates = self.getCandidates(i, j)

    def RowHiddenSingleValue(self, row, col):  # Checks if cell has Hidden Single candidate withint a Row
        HiddenSingle = 0
        row_candidates = []
        for candidate in self.board[row][col].candidates:  # iterate each candidate in specified cell
            for otherCol in list({0, 1, 2, 3, 4, 5, 6, 7, 8} - {col}):  # iterate through each column except specified
                row_candidates += self.board[row][otherCol].candidates  # collect candidates from other cells in the row
                row_candidates = list(set(row_candidates))  # remove duplicates

            if candidate in row_candidates:  # if current candidate is in the list of row candidates
                HiddenSingle = 0  # set to 0 to reset if it was previously saved
                continue  # get next candidate
            else:
                HiddenSingle = candidate  # save candidate of the current cell
                break  # found it
        return HiddenSingle

    def ColHiddenSingleValue(self, row, col):  # Checks if cell has Hidden Single candidate withint a Cow
        HiddenSingle = 0
        col_candidates = []
        for candidate in self.board[row][col].candidates:  # iterate each candidate in specified cell
            for otherRow in list({0, 1, 2, 3, 4, 5, 6, 7, 8} - {row}):  # iterate through each column except specified
                col_candidates += self.board[otherRow][col].candidates  # collect candidates from other cells in the row
                col_candidates = list(set(col_candidates))  # remove duplicates

            if candidate in col_candidates:  # if current candidate of provided cell is in the list of candidates of another cell
                HiddenSingle = 0  # set to 0 to reset is was previously saved
                continue  # get next candidate
            else:
                HiddenSingle = candidate  # save candidate of the current cell
                break
        return HiddenSingle

    def BoxHiddenSingleValue(self, row, col):  # Checks if cell has Hidden Single candidate withint a Box

        b_row, b_col = 0, 0

        if row in range(0, 3):  # set box row
            b_row = 0
        elif row in range(3, 6):
            b_row = 3
        elif row in range(6, 9):
            b_row = 6

        if col in range(0, 3):  # set box column
            b_col = 0
        elif col in range(3, 6):
            b_col = 3
        elif col in range(6, 9):
            b_col = 6

        HiddenSingle = 0
        box_candidates = []

        for candidate in self.board[row][col].candidates:  # iterate each candidate in specified cell
            # row_list = list(set(range(b_row, b_row + 3)) - {row})
            # col_list = list(set(range(b_col, b_col + 3)) - {col})

            for i in range(b_row, b_row + 3):  # iterate each row except specified
                for j in range(b_col, b_col + 3):  # iterate each col except specified

                    if (i == row) and (j == col):
                        continue

                    box_candidates += self.board[i][j].candidates  # collect candidates from other cells in the row
                    box_candidates = list(set(box_candidates))  # remove duplicates

            if candidate in box_candidates:  # if current candidate of provided cell is in the list of candidates of another cell
                HiddenSingle = 0  # set to 0 to reset is was previously saved
                continue  # get next candidate
            else:
                HiddenSingle = candidate  # save candidate of the current cell
                break

        return HiddenSingle

    def SetAllHiddenSingleCandidates(self):

        for i in range(0, 9):
            for j in range(0, 9):

                # if cell is not solved and candidate list has more than one number
                if (not self.board[i][j].solved) and (len(self.board[i][j].candidates) > 1):
                    row_hs = self.RowHiddenSingleValue(i, j)
                    col_hs = self.ColHiddenSingleValue(i, j)
                    box_hs = self.BoxHiddenSingleValue(i, j)

                    tmp = [row_hs, col_hs, box_hs]  # make list
                    tmp = [elem for elem in tmp if elem != 0]  # remove 0's to reveal any real values

                    if len(tmp) > 0:
                        old_Value = self.board[i][j].value  # save previous cell value
                        new_Value = tmp[0]  # set to single possible number

                        self.board[i][j].setCellValue(new_Value)
                        self.CurrentBoard[i][j] = new_Value

                        self.moves.append({"row": i, "col": j, "value_before": old_Value,
                                           "value_after": new_Value})  # append move to the moves list
                        print("r%sc%s=%s" % (i, j, new_Value))

                        self.RecalculateAllCandidates()  # recalculate all candidates

        cp = copy.deepcopy(self.CurrentBoard)
        return cp

    def SetAllSingleCandidates(self):  # sets all cells with the only possible number to that number
        # Covered methods: Full House; Naked Single
        for i in range(0, 9):
            for j in range(0, 9):
                if (not self.board[i][j].solved) and (
                        len(self.board[i][j].candidates) == 1):  # if cell has only one possible number

                    old_Value = self.board[i][j].value  # save previous cell value
                    new_Value = self.board[i][j].candidates[0]  # set to single possible number

                    self.moves.append({"row": i, "col": j, "value_before": old_Value,
                                       "value_after": new_Value})  # append move to the moves list
                    print("MOVE: Row:%s  Col:%s  Before:%s  After:%s" % (i, j, old_Value, new_Value))

                    # self.board[i][j].value =  new_Value     # set the only possibility as a value
                    self.board[i][j].setCellValue(new_Value)
                    # self.board[i][j].solved = True          # mark cell solved
                    self.CurrentBoard[i][j] = new_Value  # maintain array copy of the board

                    self.board[i][j].solved = True  # set board solved attribute True
                    self.RecalculateAllCandidates()  # recalculate all candidates

        tmp = copy.deepcopy(self.CurrentBoard)  # return array
        return tmp

    def Show(self, message=''):
        print("-" * 17)
        print("Message: %s" % message)
        for i in range(0, 9):
            for j in range(0, 9):
                print(self.board[i][j].value, end=" "),
            print("")
        print("=" * 17)

    def isSolved(self):
        res = False
        for i in range(0, 9):
            for j in range(0, 9):
                if self.board[i][j].value == 0:
                    return False
                else:
                    res = True
        return res

    def Solve(self):
        solved = False

        while not solved:

            saved = self.getBoardSnapshot()  # save arrays of the current board
            saved_m = self.getBoardSnapshot()

            AllowedToRun = True
            print(">>> Starting Single Candidate method...")
            while AllowedToRun:
                current = self.SetAllSingleCandidates()
                self.Show()
                AllowedToRun = (current != saved)  # or (not self.isSolved())
                saved = copy.deepcopy(current)

            AllowedToRun = True
            print(">>> Starting Hidden Single Candidate method...")
            while AllowedToRun:
                current = self.SetAllHiddenSingleCandidates()
                self.Show()
                AllowedToRun = (current != saved)  # or (not self.isSolved())
                saved = copy.deepcopy(current)

            # if solveBy_LockedCandidateType1 made any changes repeate solving cycle
            res = self.solveBy_LockedCandidateType1()
            if res:
                continue

            res = myGame.grid.solveBy_LockedCandidatesType2()
            if res:
                continue

            res = myGame.grid.solveBy_NakedTriple()

            solved = self.isSolved()  # is it solved yet?
            current = self.getBoardSnapshot()  # set all single candidates and save array again

            if (current == saved_m) and (not solved):  # if nothing changes and still unsolved
                print(">>> Ran out of all methods. Quitting! ")
                break

        return solved, self.moves


class SudokuGame:

    def __init__(self, init_puzzle):
        self.index = 0
        self.solved = False
        self.moves = []
        self.grid = Grid(init_puzzle)

    def Solve(self):
        print(">>> Starting...")
        self.solved, self.moves = self.grid.Solve()  # solve using simple method
        print(">>> Finished!")

        return self.solved


# main module

# CLEAN FIELD
my_clean = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]]

# simple one
my_simple_01 = [[7, 0, 5, 2, 0, 0, 0, 0, 4],
                [0, 8, 0, 0, 0, 0, 7, 0, 0],
                [0, 0, 0, 0, 0, 3, 2, 9, 0],
                [0, 9, 7, 4, 3, 0, 0, 0, 0],
                [3, 0, 0, 1, 0, 2, 0, 0, 8],
                [0, 0, 0, 0, 9, 5, 6, 7, 0],
                [0, 4, 8, 9, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 8, 0],
                [5, 0, 0, 0, 0, 8, 1, 0, 9]]

# complex1
my_complex_01 = [[1, 0, 4, 0, 0, 8, 0, 0, 6],
                 [0, 0, 0, 0, 1, 0, 0, 0, 0],
                 [0, 0, 0, 0, 6, 9, 0, 1, 0],
                 [3, 0, 8, 9, 5, 0, 7, 0, 0],
                 [5, 2, 0, 0, 0, 0, 0, 4, 3],
                 [0, 0, 1, 0, 4, 3, 9, 0, 8],
                 [0, 5, 0, 8, 2, 0, 0, 0, 0],
                 [0, 0, 0, 0, 3, 0, 0, 0, 0],
                 [4, 0, 0, 6, 0, 0, 1, 0, 7]]

# from https://dev.to/willamesoares/what-i-learned-from-implementing-a-sudoku-solver-in-python-3a3g
my_william = [[0, 0, 0, 2, 6, 0, 7, 0, 1],
              [6, 8, 0, 0, 7, 0, 0, 9, 0],
              [1, 9, 0, 0, 0, 4, 5, 0, 0],
              [8, 2, 0, 1, 0, 0, 0, 4, 0],
              [0, 0, 4, 6, 0, 2, 9, 0, 0],
              [0, 5, 0, 0, 0, 3, 0, 2, 8],
              [0, 0, 9, 3, 0, 0, 0, 7, 4],
              [0, 4, 0, 0, 5, 0, 0, 3, 6],
              [7, 0, 3, 0, 1, 8, 0, 0, 0]]

# 1. The World's Hardest Sudoku
my_hardest = [[8, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 3, 6, 0, 0, 0, 0, 0],
              [0, 7, 0, 0, 9, 0, 2, 0, 0],
              [0, 5, 0, 0, 0, 7, 0, 0, 0],
              [0, 0, 0, 0, 4, 5, 7, 0, 0],
              [0, 0, 0, 1, 0, 0, 0, 3, 0],
              [0, 0, 1, 0, 0, 0, 0, 6, 8],
              [0, 0, 8, 5, 0, 0, 0, 1, 0],
              [0, 9, 0, 0, 0, 0, 4, 0, 0]]

# Hard
my_hudoku_game0 = [[1, 0, 0, 0, 0, 0, 0, 0, 7],
                   [0, 6, 0, 0, 0, 0, 0, 4, 3],
                   [0, 4, 3, 0, 5, 0, 2, 0, 0],
                   [0, 0, 2, 0, 4, 8, 1, 0, 0],
                   [0, 0, 0, 1, 9, 6, 0, 0, 0],
                   [0, 0, 4, 2, 7, 0, 3, 0, 0],
                   [0, 0, 6, 0, 2, 0, 7, 3, 0],
                   [7, 3, 0, 0, 0, 0, 0, 9, 0],
                   [2, 0, 0, 0, 0, 0, 0, 0, 1]]

# Test game - LockedCandidatesType2 COL
my_hudoku_game1 = [[0, 0, 0, 5, 0, 0, 0, 3, 0],
                   [0, 2, 0, 0, 4, 3, 0, 0, 0],
                   [0, 0, 0, 0, 0, 6, 2, 0, 9],
                   [0, 8, 0, 3, 6, 0, 0, 0, 4],
                   [0, 6, 0, 0, 7, 4, 0, 1, 0],
                   [3, 0, 0, 0, 0, 1, 0, 6, 0],
                   [9, 7, 8, 4, 0, 0, 0, 0, 0],
                   [0, 0, 0, 1, 9, 0, 0, 7, 0],
                   [0, 5, 0, 6, 0, 7, 0, 0, 0]]

# Test game - LockedCandidatesType2 ROW
my_hudoku_game2 = [[0, 0, 0, 6, 5, 0, 3, 0, 8],
                   [0, 0, 0, 0, 1, 9, 0, 5, 6],
                   [5, 6, 0, 0, 0, 7, 0, 0, 9],
                   [0, 5, 0, 9, 3, 0, 4, 0, 0],
                   [2, 0, 1, 4, 6, 8, 5, 9, 0],
                   [0, 0, 9, 0, 7, 5, 0, 8, 0],
                   [3, 0, 5, 7, 0, 0, 0, 2, 4],
                   [7, 8, 4, 5, 2, 0, 9, 0, 1],
                   [0, 2, 6, 0, 0, 0, 0, 0, 5]]

my_puzzle = my_hudoku_game2  # my_complex_01 #my_simple_01

myGame = SudokuGame(my_puzzle)  # create puzzle
myGame.grid.Show(message="Before")

time_start = time.time()  # get current time
resolved = myGame.Solve()  # solve puzzle
time_dlt = round(time.time() - time_start, 2)  # get time difference
myGame.grid.Show(message="After")

if resolved:
    print("Sudoku is solved in %s seconds,  and %s placements" % (time_dlt, len(myGame.moves)))
else:
    print("Sudoku is still UNRESOLVED in %s seconds,  and %s placements" % (time_dlt, len(myGame.moves)))

print("The End.")

# Links:
#   Sudoku methods
#    http://hodoku.sourceforge.net/en/tech_intro.php
#
# currently solves simple puzzles
# need to explore more options
