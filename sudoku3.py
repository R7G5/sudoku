import time
import copy
import sys

class Cell:

    def __init__(self, value=0):
        self.value  = value                 # current value
        self.solved = False                 # this cell is solved
        self.exceptions = []                # list of values not allowed in cell due to position
        self.candidates = []                # list of possible values

    def setCellValue(self,value):
        #if value in self.candidates:
            self.value = value                                      # set value
            self.solved = True
            self.exceptions = [1,2,3,4,5,6,7,8,9].remove(value)  #.append(value) # add to exceptions
            self.candidates = []  #remove(value)  # remove from candidates
        #else:
        #    print("Error: Trying to assign value (%s) that is not in the candidate list" % (value))
        #    sys.exit(1)

class Grid:

    def __init__(self, puzzle):
        self.board = []                             # array of boards
        self.CurrentBoard = copy.deepcopy(puzzle)   # simple array representation of the board
        self.moves = []                             # list of moves
        self.twinList = {}                  # list of identical possibilities per row or col.
                                            # key = tuple of possible numbers
                                            # value = list of touple coordinates

        for i in range(0,9):
            self.board.append([])                               # create new row
            for j in range (0,9):
                self.board[i].append(Cell(puzzle[i][j]))        # copy the value to the cell
                self.board[i][j].solved = puzzle[i][j] != 0     # Marked solved if not 0
        self.RecalculateAllCandidates()

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

    #def getCandidates(self, row=0, col=0):
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


    def RowHiddenSingleValue(self, row, col):                           # Checks if cell has Hidden Single candidate withint a Row
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

                if ((i==1) and (j==7)):   # ToDo: DEBUG all cells - BREAKPOINT
                    print("DEBUG")
                
                if ((not self.board[i][j].solved)) and (len(self.board[i][j].candidates) > 1):  # if cell is not solved and candidate list has more than one number
                    row_hs = self.RowHiddenSingleValue(i,j)
                    col_hs = self.ColHiddenSingleValue(i,j)
                    box_hs = self.BoxHiddenSingleValue(i,j)

                    tmp = [row_hs, col_hs, box_hs]              # make list
                    tmp = [elem for elem in tmp if elem != 0]   # remove 0's to reveal any real values

                    if len(tmp) > 0:

                        old_Value = self.board[i][j].value      # save previous cell value
                        new_Value = tmp[0]                      # set to single possible number

                        #self.board[i][j].value = new_Value         # tmp list MUST only have single element
                        self.board[i][j].setCellValue(new_Value)
                        self.CurrentBoard[i][j] = new_Value
                        #self.board[i][j].solved = True

                        self.moves.append({"row": i, "col": j, "value_before": old_Value, "value_after": new_Value})  # append move to the moves list
                        print("Row:%s  Col:%s  Before:%s  After:%s" % (i, j, old_Value, new_Value))

                        self.RecalculateAllCandidates()             # recalculate all candidates

        cp = copy.deepcopy(self.CurrentBoard)
        return cp

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

    def SetAllSingleCandidates(self):    # sets all cells with the only possible number to that number
                                         # Covered methods: Full House; Naked Single

        for i in range(0, 9):
            for j in range (0,9):
                if ((not self.board[i][j].solved)) and (len(self.board[i][j].candidates) == 1): # if cell has only one possible number

                    old_Value = self.board[i][j].value           # save previous cell value
                    new_Value = self.board[i][j].candidates[0]   # set to single possible number

                    self.moves.append({"row":i, "col":j, "value_before":old_Value, "value_after": new_Value }) # append move to the moves list
                    print("Row:%s  Col:%s  Before:%s  After:%s" % (i, j, old_Value, new_Value))

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
                self.Show("Debug: Singe Candidate")
                AllowedToRun =  (current != saved) #or (not self.isSolved())
                saved = copy.deepcopy(current)

            AllowedToRun = True
            print(">>> Starting Hidden Single Candidate method...")
            while AllowedToRun:
                current = self.SetAllHiddenSingleCandidates()
                self.Show("Debug: Hidden Singe")
                AllowedToRun = (current != saved) #or (not self.isSolved())
                saved = copy.deepcopy(current)

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

        '''
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
        return self.solved

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
''' # example


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


my_puzzle =  my_complex_01 #my_simple_01

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




# ToDo:
#   [X] Implemented Grid.ColHiddenSingleValue, Grid.RowHiddenSingleValue, Grid.BoxHiddenSingleValue methods
#   [X] Optimized Grid.getCandidate and Grid.buildExceptions methods
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

