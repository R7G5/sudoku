import time
import copy
#import sys

class Cell:

    def __init__(self, row, col, value=0):
        self.value  = value                 # current value
        self.solved = False                 # this cell is solved
        self.given  = False                 # initial given
        self.exceptions = []                # list of values not allowed in cell due to position
        self.candidates = []                # list of possible values
        self.row = row
        self.col = col
        self.box = self.getBoxNum(row,col)

    @staticmethod
    def getBoxNum(row,col):
        box = 0
        if (row in [0,1,2]):
            if (col in [0,1,2]):
                box = 1
            if (col in [3,4,5]):
                box = 2
            if (col in [6,7,8]):
                box = 3

        if (row in [3, 4, 5]):
            if (col in [0,1,2]):
                box = 4
            if (col in [3,4,5]):
                box = 5
            if (col in [6,7,8]):
                box = 6

        if (row in [6, 7, 8]):
            if (col in [0,1,2]):
                box = 7
            if (col in [3,4,5]):
                box = 8
            if (col in [6,7,8]):
                box = 9
        return box

    def setCellValue(self,value):
            self.value = value
            self.solved = True
            self.exceptions = [] #[1, 2, 3, 4, 5, 6, 7, 8, 9]  #self.exceptions.remove(value)
            self.candidates = []

    def RemoveCellExceptions(self,exceptions):      # removes provided exceptions
            for exception in exceptions:
                self.exceptions.remove(exception)

class Grid:

    def __init__(self, puzzle):
        self.board = []                             # array of boards
        self.CurrentBoard = copy.deepcopy(puzzle)   # simple array representation of the board
        self.moves = []                             # list of moves r3c1=9 (assing), r4c9-4 (remove candidate), r8c1+1379 (add candidates), r347c4-6 (remove candidates
        self.twinList = {}                  # list of identical possibilities per row or col.
                                            # key = tuple of possible numbers
                                            # value = list of touple coordinates
        for i in range(0,9):
            self.board.append([])           # create new row
            for j in range (0,9):
                self.board[i].append(Cell(row=i, col=j, value=puzzle[i][j]))        # copy the value to the cell
                self.board[i][j].solved = puzzle[i][j] != 0     # Marked solved if not 0
        self.RecalculateAllCandidates()

    # 6....23..1256.......47...2.73....84...........46....15.5...81.......3472..72....8
    def setGivens(self,givens):
        x = 0
        for i in range(0,9):
            for j in range(0,9):
                self.board[i][j].value = givens[x]
                self.board[i][j].given = True
                x += 1

    def getGivens(self):
        res = ""
        for i in range(0,9):
            for j in range(0,9):
                res += str(self.board[i][j].value) if self.board[i][j].value != 0 else "."
        return res

    def getCandidates(self): # ToDo: Added method grid.getCandidates
        # Returns list of candidates in multi-row text foramat. Could be pasted in most sudoku apps
        res = ""
        for i in range(0,9):
            for j in range(0,9):
                cur = self.board[i][j].candidates if self.board[i][j].candidates else [self.board[i][j].value]
                cur.sort()
                res += "".join([str(elem) for elem in cur]) + " "
            res += "\n"
        return res

    def getHouseRow_coordinates(self, cell_coord):   # get list of house row coordinates
        return [ (cell_coord[0], clm) for clm in range(0, 9) ] # if clm !=cell.col ] # excluding current cell

    def getHouseCol_coordinates(self, cell_coord):   # get list of house col coordinates
        return [ (rw, cell_coord[1]) for rw in range(0, 9) ] # if rw !=cell.row ] # , excluding current cell

    @staticmethod
    def getHouseBox_coordinates(BoxNum):
        rows, cols = [], []

        if BoxNum in [1,2,3]:
            rows = [0,1,2]
        elif BoxNum in [4,5,6]:
            rows = [3,4,5]
        elif BoxNum in [7,8,9]:
            rows = [6,7,8]

        if BoxNum in [1,4,7]:
            cols = [0,1,2]
        elif BoxNum in [2,5,8]:
            cols = [3,4,5]
        elif BoxNum in [3,6,9]:
            cols = [6,7,8]

        return [(r, c) for r in rows for c in cols]
        #[(x,c) for x in range(0,5) if x !=3 for c in range(0,5) if c !=3]

    def getBoxRowCandidates(self, cell): # ToDo: Need to test
        ROW, COL  = 0, 1
        houseCoords = self.getHouseBox_coordinates(cell.box)      # get list cell coordinates of the box
        cols = [coord[COL] for coord in houseCoords if coord[ROW] == cell.row]  # extract column numbers

        # assemble list of candidates from the row,col(n)
        cand = [ self.board[cell.row][col].candidates for col in cols if len(self.board[cell.row][col].candidates)!=0]
        cand = [item for items in cand for item in items]   # expand list into single list
        return cand

    def getBoxColCandidates(self, cell): # ToDo: Need to test
        ROW, COL  = 0, 1
        houseCoords = self.getHouseBox_coordinates(cell.box)      # get list cell coordinates of the box
        rows = [coord[ROW] for coord in houseCoords if coord[COL] == cell.col]  # extract row numbers

        # assemble list of candidates from the row(n),col
        cand = [self.board[row][cell.col].candidates for row in rows if len(self.board[row][cell.col].candidates)!=0]
        cand = [item for items in cand for item in items]  # expand list into single list
        return cand

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

        ROW, COL  = 0, 1
        changesMade = False

        for box in range(1,10):                             # for each box 1..9 (ignoring 0)

            coords = self.getHouseBox_coordinates(box)      # get list of box cells
            confined_box_candidates = {}

            for coord in coords:
                currentCell = self.board[coord[ROW]][coord[COL]]

                if not currentCell.solved:                                       # if cell is not solved

                    for candidate in currentCell.candidates:                     # look for candidates that are confined to a row or column

                        if candidate not in confined_box_candidates:             # if candidate is not already in the list
                            confined_box_candidates[candidate] = {}
                            confined_box_candidates[candidate]["coordinates"] = [coord]         # Add newly found to the list
                            confined_box_candidates[candidate]["matchBy"] = [False, False]
                            continue
                        elif (-1,-1) in confined_box_candidates[candidate]["coordinates"]:
                            continue

                        tmp_lst = confined_box_candidates[candidate]["coordinates"].copy()   # copy candiata coordinates
                        tmp_lst.append(coord)                                               # add current coordinates

                        # Unzip coord list [(r1,c1),(r2,c2),...(rN,cN)] to [(r1,r1,...rN),(c1,c2,...cN)]
                        # Convert each tuple to set() to eliminate duplicates. If single element left then all were the same.
                        # Returns [True, False] if all ROW indexes match, [False, True] for Column
                        RowOrColmatch = [len(set(elem))==1 for elem in zip(*tmp_lst)]

                        if any(RowOrColmatch):
                            if (-1, -1) not in confined_box_candidates[candidate]["coordinates"]:                                  # if not set to be ignored
                                confined_box_candidates[candidate]["coordinates"] += [coord]                                    # good candidate, add coord to the list
                                confined_box_candidates[candidate]["matchBy"] = RowOrColmatch
                        else:
                            confined_box_candidates[candidate]["coordinates"] = [(-1,-1)]     # Ignore this canddate
                            confined_box_candidates[candidate]["matchBy"] = [False,False]   # [Row,Col]

            # Remove all items containing (0,0)
            confined_box_candidates = {key: value for (key, value) in confined_box_candidates.items() if (-1, -1) not in value["coordinates"]}
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
                    new_candidates = [ elem for elem in self.board[cell[ROW]][cell[COL]].candidates if elem != candidate ]
                    candidate_diff += list(set(self.board[cell[ROW]][cell[COL]].candidates) ^ set(new_candidates))
                    self.board[cell[ROW]][cell[COL]].candidates = new_candidates
                    changesMade = changesMade or candidate_diff != []    # if not equal empty list
                print("       removed candidates: %s" % (list(candidate_diff)))

        return changesMade



    def solveBy_LockedCandidatesType2(self):
        # ToDo: Work on LockedCandidatesType2

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

        ROW, COL  = 0, 1

        final_res = {}
        confined_box_candidates = {}

        for i in range(0,9):
            for j in range(0,9):  # Debug

                if self.board[i][j].solved:   # skip if solved
                    continue

                currentCell = self.board[i][j]

                interrupted = False

                # get next candidate
                for candidate in currentCell.candidates:

                    # save current candidate
                    current_candidate = {}
                    current_candidate[candidate] = {}
                    current_candidate[candidate]["box"] = [currentCell.box]
                    current_candidate[candidate]["coordinates"] = [(i,j)]

                    confined_box_candidates = copy.deepcopy(current_candidate)

                    # Check all cells in the ROW
                    for col in range(0,9):
                        if col == j: # skip if it's the same cell
                            continue

                        if candidate in self.board[i][col].candidates:

                            if self.board[i][j].solved:  # skip if solved
                                continue

                            if candidate not in confined_box_candidates:  # if candidate is not already in the list
                                confined_box_candidates[candidate] = {}
                                confined_box_candidates[candidate]["box"] = [self.board[i][col].box]
                                confined_box_candidates[candidate]["coordinates"] = [(i,col)]
                            else:
                                if self.board[i][col].box not in confined_box_candidates[candidate]["box"]:
                                    interrupted = True                          # skip COL search if box is different
                                    confined_box_candidates = {} #copy.deepcopy(current_candidate)
                                    break                                       # stop looping COL cells for this candidate
                                else:                                           # add if its the same box
                                    confined_box_candidates[candidate]["coordinates"].append((i,col))

                    if not interrupted:  # not interrupted - same as found
                        # ToDo:Remove candidate from all other cells in the box
                        final_res.update(confined_box_candidates)  # temp
                        continue        # so we could go to the next candidate


                    # save current candidate
                    current_candidate = {}
                    current_candidate[candidate] = {}
                    current_candidate[candidate]["box"] = [currentCell.box]
                    current_candidate[candidate]["coordinates"] = [(i,j)]

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
                                confined_box_candidates[candidate]["coordinates"] = [(row,j)]
                            else:
                                if self.board[row][j].box not in confined_box_candidates[candidate]["box"]:
                                    interrupted = True                          # skip ROW search if box is different
                                    confined_box_candidates = {} #copy.deepcopy(current_candidate)
                                    break                                       # stop looping cells for this candidate
                                else:                                           # add if its the same box
                                    confined_box_candidates[candidate]["coordinates"].append((row,j))

                    if not interrupted:  # not interrupted - same as found
                        # ToDo:Remove candidate from all other cells in the box
                        final_res.update(confined_box_candidates) # temp
                        continue        # so we could go to the next candidate

        # DEBUG
        print(confined_box_candidates)





    def getBoardSnapshot(self):  # returns an array copy of the grid
        tmp = copy.deepcopy(self.CurrentBoard)
        return tmp

    def getColValues(self, col):      # returns list of values from the Col where provided cell resides
        tmp = []
        for i in range(0, 9):
            tmp.append(self.board[i][col].value)
        return tmp

    def getRowValues(self, row):      # returns list of values from the Row where provided cell resides
        tmp = []
        for j in range(0, 9):
            tmp.append(self.board[row][j].value)
        return tmp

    def getBoxValues(self, row, col): # returns list of values from the Box where provided cell resides

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
        exceptionList = []
        exceptionList = set(self.getBoxValues(row, col) + self.getColValues(col) + self.getRowValues(row))    # create unique list of candidates
        exceptionList = [elem for elem in exceptionList if elem != 0]                                 # remove all zeros
        self.board[row][col].exceptions = exceptionList
        return exceptionList

    def setCellCandidates(self, row=0, col=0):
        allNumbers =  [1, 2, 3, 4, 5, 6, 7, 8, 9]
        exceptionList = self.setCellExceptions(row, col)        # set and return cell exceptions
        candidateList = list(set(allNumbers) - set(exceptionList))
        self.board[row][col].candidates = candidateList
        return candidateList       # list of numbers not in exception list

    def RecalculateAllCandidates(self):
        for i in range(0, 9):
            for j in range (0,9):
                if not self.board[i][j].solved:
                    self.setCellCandidates(i,j) #candidates = self.getCandidates(i, j)

    def RowHiddenSingleValue(self, row, col): # Checks if cell has Hidden Single candidate withint a Row
        HiddenSingle = 0
        row_candidates = []
        for candidate in self.board[row][col].candidates:               # iterate each candidate in specified cell
            for otherCol in list({0, 1, 2, 3, 4, 5, 6, 7, 8} - {col}):  # iterate through each column except specified
                row_candidates += self.board[row][otherCol].candidates  # collect candidates from other cells in the row
                row_candidates = list(set(row_candidates))              # remove duplicates

            if candidate in row_candidates:                             # if current candidate is in the list of row candidates
                HiddenSingle = 0                                    # set to 0 to reset if it was previously saved
                continue                                            # get next candidate
            else:
                HiddenSingle = candidate                            # save candidate of the current cell
                break                                               # found it
        return HiddenSingle

    def ColHiddenSingleValue(self, row, col):                           # Checks if cell has Hidden Single candidate withint a Cow
        HiddenSingle = 0
        col_candidates = []
        for candidate in self.board[row][col].candidates:               # iterate each candidate in specified cell
            for otherRow in list({0, 1, 2, 3, 4, 5, 6, 7, 8} - {row}):  # iterate through each column except specified
                col_candidates += self.board[otherRow][col].candidates  # collect candidates from other cells in the row
                col_candidates = list(set(col_candidates))              # remove duplicates

            if candidate in col_candidates:                             # if current candidate of provided cell is in the list of candidates of another cell
                HiddenSingle = 0                                        # set to 0 to reset is was previously saved
                continue                                                # get next candidate
            else:
                HiddenSingle = candidate                                # save candidate of the current cell
                break
        return HiddenSingle

    def BoxHiddenSingleValue(self, row, col):                           # Checks if cell has Hidden Single candidate withint a Box

        b_row, b_col = 0, 0

        if row in range(0, 3):                                          # set box row
            b_row = 0
        elif row in range(3, 6):
            b_row = 3
        elif row in range(6, 9):
            b_row = 6

        if col in range(0, 3):                                          # set box column
            b_col = 0
        elif col in range(3, 6):
            b_col = 3
        elif col in range(6, 9):
            b_col = 6

        HiddenSingle = 0
        box_candidates = []

        for candidate in self.board[row][col].candidates:               # iterate each candidate in specified cell
            #row_list = list(set(range(b_row, b_row + 3)) - {row})
            #col_list = list(set(range(b_col, b_col + 3)) - {col})

            for i in range(b_row, b_row + 3):        # iterate each row except specified
                for j in range(b_col, b_col + 3):    # iterate each col except specified

                    if (i == row) and (j == col):
                        continue

                    box_candidates += self.board[i][j].candidates       # collect candidates from other cells in the row
                    box_candidates = list(set(box_candidates))          # remove duplicates

            if candidate in box_candidates:                     # if current candidate of provided cell is in the list of candidates of another cell
                HiddenSingle = 0                                # set to 0 to reset is was previously saved
                continue                                        # get next candidate
            else:
                HiddenSingle = candidate                        # save candidate of the current cell
                break

        return HiddenSingle

    def SetAllHiddenSingleCandidates(self):

        row_hs, col_hs, box_hs = 0, 0, 0

        for i in range(0, 9):
            for j in range (0,9):
                
                if ((not self.board[i][j].solved)) and (len(self.board[i][j].candidates) > 1):  # if cell is not solved and candidate list has more than one number
                    row_hs = self.RowHiddenSingleValue(i,j)
                    col_hs = self.ColHiddenSingleValue(i,j)
                    box_hs = self.BoxHiddenSingleValue(i,j)

                    tmp = [row_hs, col_hs, box_hs]              # make list
                    tmp = [elem for elem in tmp if elem != 0]   # remove 0's to reveal any real values

                    if len(tmp) > 0:

                        old_Value = self.board[i][j].value      # save previous cell value
                        new_Value = tmp[0]                      # set to single possible number

                        self.board[i][j].setCellValue(new_Value)
                        self.CurrentBoard[i][j] = new_Value

                        self.moves.append({"row": i, "col": j, "value_before": old_Value, "value_after": new_Value})  # append move to the moves list
                        print("r%sc%s=%s" % (i, j, new_Value))

                        self.RecalculateAllCandidates()             # recalculate all candidates

        cp = copy.deepcopy(self.CurrentBoard)
        return cp

    def SetAllSingleCandidates(self):    # sets all cells with the only possible number to that number
                                         # Covered methods: Full House; Naked Single
        for i in range(0, 9):
            for j in range (0,9):
                if ((not self.board[i][j].solved)) and (len(self.board[i][j].candidates) == 1): # if cell has only one possible number

                    old_Value = self.board[i][j].value           # save previous cell value
                    new_Value = self.board[i][j].candidates[0]   # set to single possible number

                    self.moves.append({"row":i, "col":j, "value_before":old_Value, "value_after": new_Value }) # append move to the moves list
                    print("MOVE: Row:%s  Col:%s  Before:%s  After:%s" % (i, j, old_Value, new_Value))

                    #self.board[i][j].value =  new_Value     # set the only possibility as a value
                    self.board[i][j].setCellValue(new_Value)
                    #self.board[i][j].solved = True          # mark cell solved
                    self.CurrentBoard[i][j] = new_Value     # maintain array copy of the board

                    self.board[i][j].solved = True          # set board solved attribute True
                    self.RecalculateAllCandidates()         # recalculate all candidates

        tmp = copy.deepcopy(self.CurrentBoard)              # return array
        return tmp

    def Show(self,message=''):
        print("-" * 17)
        print("Message: %s" % (message))
        for i in range(0, 9):
            for j in range (0,9):
                print(self.board[i][j].value, end = " "),
            print("")
        print("="*17)

    def isSolved(self):
        res = False
        for i in range(0, 9):
            for j in range (0,9):
                if self.board[i][j].value == 0:
                    return False
                else:
                    res = True
        return res

    def Solve(self):
        solved = False

        while (not solved):

            saved = self.getBoardSnapshot()                  # save arrays of the current board
            saved_m = self.getBoardSnapshot()

            AllowedToRun = True
            print(">>> Starting Single Candidate method...")
            while AllowedToRun:
                current = self.SetAllSingleCandidates()
                self.Show()
                AllowedToRun =  (current != saved) #or (not self.isSolved())
                saved = copy.deepcopy(current)



            AllowedToRun = True
            print(">>> Starting Hidden Single Candidate method...")
            while AllowedToRun:
                current = self.SetAllHiddenSingleCandidates()
                self.Show()
                AllowedToRun = (current != saved) #or (not self.isSolved())
                saved = copy.deepcopy(current)

            # if solveBy_LockedCandidateType1 made any changes repeate solving cycle
            res = self.solveBy_LockedCandidateType1()
            if res:
                continue


            # ToDo: Test / Debug
            a = myGame.grid.solveBy_LockedCandidatesType2()

            solved = self.isSolved()                        # is it solved yet?
            current = self.getBoardSnapshot()                # set all single candidates and save array again

            if (current == saved_m) and (not solved):         # if nothing changes and still unsolved
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
        i = self.index

        print(">>> Starting...")
        self.solved, self.moves = self.grid.Solve()         # solve using simple method
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
my_simple_01= [[7, 0, 5, 2, 0, 0, 0, 0, 4],
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
                   [0, 0 ,0 ,1, 9, 6, 0, 0, 0],
                   [0, 0, 4, 2, 7, 0, 3, 0, 0],
                   [0, 0, 6, 0, 2, 0, 7, 3, 0],
                   [7, 3, 0, 0 ,0, 0, 0, 9, 0],
                   [2, 0, 0, 0, 0, 0, 0, 0, 1]]

# Test game - LockedCandidatesType2 COL
my_hudoku_game1 = [[0, 0, 0, 5, 0, 0, 0, 3, 0],
                   [0, 2, 0, 0, 4, 3, 0, 0, 0],
                   [0, 0, 0, 0, 0, 6, 2, 0, 9],
                   [0, 8, 0, 3, 6, 0, 0, 0, 4],
                   [0, 6 ,0 ,0, 7, 4, 0, 1, 0],
                   [3, 0, 0, 0, 0, 1, 0, 6, 0],
                   [9, 7, 8, 4, 0, 0, 0, 0, 0],
                   [0, 0, 0, 1 ,9, 0, 0, 7, 0],
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

my_puzzle =  my_hudoku_game2 #my_complex_01 #my_simple_01

myGame = SudokuGame(my_puzzle)                  # create puzzle
myGame.grid.Show(message="Before")

time_start = time.time()                        # get current time
solved = myGame.Solve()                         # solve puzzle
time_dlt = round(time.time() - time_start,2)    # get time difference
myGame.grid.Show(message="After")

if (solved):
    print("Sudoku is solved in %s seconds,  and %s placements" % (time_dlt , len(myGame.moves)))
else:
    print("Sudoku is still UNRESOLVED in %s seconds,  and %s placements" % (time_dlt , len(myGame.moves)))

print("The End.")

# ToDo: Add to production cycle
#a = myGame.grid.getBoxRowCandidates(myGame.grid.board[0][0])
#a = myGame.grid.solveBy_LockedCandidateType1()



# ToDo:
#
#   Committed:
#   [X] Create twinList - list of identical possibilities for the board
#   [X] fix issue: remove twinList items where list of coordinates in the value is shorter than 2 items
#   [X] Sort twinList dictionary by the length of the key - shortest number of possibilities
#   [X] Rename method from getBlock to getBoxValues
#   [X] Rename Cell.possibilities attribute to Cell.candidates
#   [X] Rename object and variables from Puzzle/puzzle to Grid
#   [X] Rename Grid.SetAllSiglePossibilities method to Grid.SetAllSingleCandidates


# Links:
#   Sudoku methods
#    http://hodoku.sourceforge.net/en/tech_intro.php
#
# currently solves simple puzzles
# need to explore more options

'''
# Populates attribute twinList with identical possibiities
def setTwinList(self):
    self.twinList = {}  # clear existing data

    for i in range(0, 9):
        for j in range (0,9):
            if not self.board[i][j].solved:
                tpl = tuple(sorted(self.board[i][j].candidates))     # get list of current possibilities
                if tpl not in self.twinList.keys():                         # if does not exist
                    self.twinList[tpl] = []                                 # create one
                self.twinList[tpl].append((i,j))                            # add (row,col) tuple to the list

    self.twinList = dict(filter(lambda item: len(item[1]) > 1, self.twinList.items()))  # only keep items with two or more cell coordinates
    self.twinList = sorted(self.twinList.items(), key=lambda item: len(item[0]))         # sort by length of possibility list
#return ?
'''
''' from SudokuGame.Solve
while not self.grid.isSolved():   # or self.grid[i].solved
    self.grid.setTwinList()

    for key, value in self.grid.twinList:   # iterate key (possible numbers) and values cell coordinates
        for possibility in key:                  # iterate through all possible numbers in the key
            print("==>Exporing Possibility: %s" % (possibility))
            for row, col in value:               # iterate through all coordinates in value

                print("Possible # = %s   Coord:(%s,%s)" % (possibility, row, col))

                cur_board = copy.deepcopy(self.grid.CurrentBoard)   # make array copy of existing board
                cur_board[row][col] = possibility                     # replace cell with possibility
                tmp_game = SudokuGame(cur_board)                      # create new SudokuGame object
                tmp_game.Solve()                                      # try to solve it

                if tmp_game.solved:                                   # if solved: exit
                    self.grid.moves += tmp_game.grid.moves
                    print("Line 206: Grid solved!!!")
                    self.solved = True
                    return self.solved
'''

'''
for k,v in mydict.items():
	print(k,"=",v)
	for possibility in k:
		print(" |-",possibility)
		for row,col in v:
			print("    |--- row:",row," col:",col)


(2, 4, 7) = [(0, 1), (0, 7)]
 |- 2
    |--- row: 0  col: 1
    |--- row: 0  col: 7
 |- 4
    |--- row: 0  col: 1
    |--- row: 0  col: 7
 |- 7
    |--- row: 0  col: 1
    |--- row: 0  col: 7
(5, 8) = [(1, 4), (3, 0)]
 |- 5
    |--- row: 1  col: 4
    |--- row: 3  col: 0
 |- 8
    |--- row: 1  col: 4
    |--- row: 3  col: 0
'''  # example

# example
# n = len([i for i, value in enumerate(boxRowCandidates) if value == candidate])   # how many found in the box row
# print("   Candidate %s found %s times" % (candidate, n))
