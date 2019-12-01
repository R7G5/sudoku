import time
import copy

class Cell:

    def __init__(self, row, col, value=0):
        self.value  = value                 # current value
        self.solved = False                 # this cell is solved
        self.row = row                      # cell row position
        self.col = col                      # cell column position
        self.exceptions = []                # list of values not allowed in cell due to position
        self.possibilities = []             # list of possible values

class Puzzle:

    def __init__(self, puzzle):
        self.bookmark = 0
        self.board = []                     # array of boards
        self.CurrentBoard = puzzle.copy()   # simple array representation of the board
        self.moves = []
        self.twinList = {}                  # list of identical possibilities per row or col.
                                            # key = tuple of possible numbers
                                            # value = list of touple coordinates

        '''
        mydict = {
            possibilities : ((row1,col1),...)
	        (2,4,7) : (0,1),
	        (5,8) : ((1,4),(3,0))
	        }
        '''

        for i in range(0,9):
            self.board.append([])   # create new row
            for j in range (0,9):
                self.board[i].append(Cell(i,j,puzzle[i][j]))        # copy the value to the cell
                self.board[i][j].solved = puzzle[i][j] != 0         # Marked solved is not 0
        self.setAllSpecials()

    def getCurrentBoard(self):
        tmp = copy.deepcopy(self.CurrentBoard)
        return tmp

    def getCol(self, col):
        tmp = []
        for i in range(0, 9):
            tmp.append(self.board[i][col].value)
        return tmp

    def getRow(self, row):
        tmp = []
        for j in range(0, 9):
            tmp.append(self.board[row][j].value)
        return tmp

    def getBlock(self, row, col):

        b_row = 0
        b_col = 0

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

    def getExceptions(self, row, col):
        tmp = []
        tmp = set(self.getBlock(row, col) + self.getCol(col) + self.getRow(row))    # create unique list of possibilities
        tmp = [elem for elem in tmp if elem != 0]                                   # remove all zeros
        return tmp

    def getPossibleNumbers(self, row, col):
        allNumbers =  [1, 2, 3, 4, 5, 6, 7, 8, 9]
        exceptionList = self.getExceptions(row, col)
        return list(set(allNumbers) - set(exceptionList))   # list of numbers not in exception list

    def setAllSpecials(self):
        for i in range(0, 9):
            for j in range (0,9):
                if not self.board[i][j].solved:
                    self.board[i][j].exceptions = self.getExceptions(i, j)
                    self.board[i][j].possibilities = self.getPossibleNumbers(i, j)


    # Populates attribute twinList with identical possibiities
    def setTwinList(self):
        self.twinList = {}  # clear existing data

        for i in range(0, 9):
            for j in range (0,9):
                if not self.board[i][j].solved:
                    tpl = tuple(sorted(self.board[i][j].possibilities))     # get list of current possibilities
                    if tpl not in self.twinList.keys():                         # if does not exist
                        self.twinList[tpl] = []                                 # create one
                    self.twinList[tpl].append((i,j))                            # add (row,col) tuple to the list

        self.twinList = dict(filter(lambda item: len(item[1]) > 1, self.twinList.items()))  # only keep items with two or more cell coordinates
        self.twinList = sorted(self.twinList.items(), key=lambda item: len(item[0]))        # sort by length of possibility list
    #return ?

    def SetAllSinglePossibilities(self):

        for i in range(0, 9):
            for j in range (0,9):
                if ( (not self.board[i][j].solved)) and (len(self.board[i][j].possibilities) == 1):

                    old_Value = self.board[i][j].value
                    new_Value = self.board[i][j].possibilities[0]

                    self.moves.append({"row":i, "col":j, "value_before":old_Value, "value_after": new_Value })

                    self.board[i][j].value =  new_Value     # set the only possibility as a value
                    self.board[i][j].solved = True          # mark cell solved
                    self.CurrentBoard[i][j] = new_Value                 # maintain simple board copy

                    self.board[i][j].solved = True
                    self.setAllSpecials()  # recalculate all exceptions and possibilities

        tmp = copy.deepcopy(self.CurrentBoard)
        return tmp

    def Show(self):
        for i in range(0, 9):
            for j in range (0,9):
                print(self.board[i][j].value, end = " "),
            print("")
        print("="*20)


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
            self.Show()
            solved = self.isSolved()                       # is is solved yet?
            saved = self.getCurrentBoard()                 # save arrays of the current board
            current = self.SetAllSinglePossibilities()     # set all singular possibilities and save array again

            if (current == saved) and (not solved):         # if nothing changes and still unsolved
                print("Ran out of options single possibility options")
                # use additional algorithm
                break

            #if len(self.moves) > 1000:  # safety pin
            #    print("Safety pin triggered. Too many moves")
            #    break

        return solved, self.moves

class SudokuGame:

    def __init__(self, init_puzzle):
        self.index = 0
        self.solved = False
        self.moves = []
        self.puzzle = []
        self.puzzle.append([])
        self.puzzle[self.index] = Puzzle(init_puzzle)

    def Solve(self):
        i = self.index

        #for i in range(0, len(self.puzzle[i])):

        self.solved, self.moves = self.puzzle[i].Solve()         # solve using simple method

        while not self.puzzle[i].isSolved():   # or self.puzzle[i].solved
            self.puzzle[i].setTwinList()

            for key, value in self.puzzle[i].twinList:   # iterate key (possible numbers) and values cell coordinates
                for possibility in key:                  # iterate through all possible numbers in the key
                    for row, col in value:               # iterate through all coordinates in value

                        cur_board = copy.deepcopy(self.puzzle[i].CurrentBoard)      # make array copy of existing board
                        cur_board[row][col] = possibility                           # replace cell with possibility
                        tmp_puzzle = Puzzle(cur_board)                              # create new Puzzle object
                        tmp_puzzle.Solve()                                          # try to solve it
                        if tmp_puzzle.isSolved():                                   # if solved: exit
                            self.puzzle[i].moves += tmp_puzzle.moves
                            print("Line 205: Puzzle solved!!!")
                            return True

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

'''
# simple one
my_puzzle = [[7, 0, 5, 2, 0, 0, 0, 0, 4],
             [0, 8, 0, 0, 0, 0, 7, 0, 0],
             [0, 0, 0, 0, 0, 3, 2, 9, 0],
             [0, 9, 7, 4, 3, 0, 0, 0, 0],
             [3, 0, 0, 1, 0, 2, 0, 0, 8],
             [0, 0, 0, 0, 9, 5, 6, 7, 0],
             [0, 4, 8, 9, 0, 0, 0, 0, 0],
             [0, 0, 1, 0, 0, 0, 0, 8, 0],
             [5, 0, 0, 0, 0, 8, 1, 0, 9]]

# complex1
my_puzzle = [[1, 0, 4, 0, 0, 8, 0, 0, 6],
             [0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 6, 9, 0, 1, 0],
             [3, 0, 8, 9, 5, 0, 7, 0, 0],
             [5, 2, 0, 0, 0, 0, 0, 4, 3],
             [0, 0, 1, 0, 4, 3, 9, 0, 8],
             [0, 5, 0, 8, 2, 0, 0, 0, 0],
             [0, 0, 0, 0, 3, 0, 0, 0, 0],
             [4, 0, 0, 6, 0, 0, 1, 0, 7]]


# CLEAN FIELD
my_puzzle = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0]]

'''
# complex
my_puzzle = [[8, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 3, 6, 0, 0, 0, 0, 0],
             [0, 7, 0, 0, 9, 0, 2, 0, 0],
             [0, 5, 0, 0, 0, 7, 0, 0, 0],
             [0, 0, 0, 0, 4, 5, 7, 0, 0],
             [0, 0, 0, 1, 0, 0, 0, 3, 0],
             [0, 0, 1, 0, 0, 0, 0, 6, 8],
             [0, 0, 8, 5, 0, 0, 0, 1, 0],
             [0, 9, 0, 0, 0, 0, 4, 0, 0]]

# 1. The World's Hardest Sudoku


myPuz = SudokuGame(my_puzzle)           # create puzzle

time_start = time.time()                # get current time

solved = myPuz.Solve()                  # solve puzzle

time_dlt = round(time.time() - time_start,2)    # get time difference

if (solved):
    print("Sudoku is solved in %s seconds,  and %s placements" % (time_dlt , len(myPuz.moves)))
else:
    print("Sudoku is still UNRESOLVED in %s seconds,  and %s placements" % (time_dlt , len(myPuz.moves)))

print("The End.")

# ToDo:
#   [X] Create twinList - list of identical possibilities for the board
#   [X] fix issue: remove twinList items where list of coordinates in the value is shorter than 2 items
#   [X] Sort twinList dictionary by the length of the key - shortest number of possibilities
#   ---
#   [ ] for each number (N) in possibility dictionary key (twinList)
#       [ ] for each coordinate set (R,C) in the current possibility dictionary key.value
#           [ ] copy puzzle, and set cell (R,C) to N
#           [ ] try to .Solve puzzle

#
# currently solves simple puzzles
# need to explore more options

