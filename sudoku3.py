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
        self.index = 0
        self.bookmark = 0
        self.board = []                     # array of boards
        self.CurrentBoard = puzzle.copy()   # simple array representation of the board
        self.board.append([])               # add first primary board
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
            self.board[self.index].append([])   # create new row
            for j in range (0,9):
                self.board[self.index][i].append(Cell(i,j,puzzle[i][j]))        # copy the value to the cell
                self.board[self.index][i][j].solved = puzzle[i][j] != 0         # Marked solved is not 0
        self.setAllSpecials()

    def getCurrentBoard(self):
        tmp = copy.deepcopy(self.CurrentBoard)
        return tmp

    def getCol(self, col):
        tmp = []
        for i in range(0, 9):
            tmp.append(self.board[self.index][i][col].value)
        return tmp

    def getRow(self, row):
        tmp = []
        for j in range(0, 9):
            tmp.append(self.board[self.index][row][j].value)
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
                tmp.append(self.board[self.index][i][j].value)
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
                if not self.board[self.index][i][j].solved:
                    self.board[self.index][i][j].exceptions = self.getExceptions(i, j)
                    self.board[self.index][i][j].possibilities = self.getPossibleNumbers(i, j)


    # Populates attribute twinList with identical possibiities
    def seTwinList(self):
        self.twinList = {}  # clear existing data

        for i in range(0, 9):
            for j in range (0,9):
                if not self.board[self.index][i][j].solved:
                    tpl = tuple(sorted(self.board[self.index][i][j].possibilities))     # get list of current possibilities
                    if tpl not in self.twinList.keys():                         # if does not exist
                        self.twinList[tpl] = []                                 # create one
                    self.twinList[tpl].append((i,j))                            # add (row,col) tuple to the list

        self.twinList = dict(filter(lambda item: len(item[1]) > 1, self.twinList.items()))  # only keep items with two or more cell coordinates
        self.twinList = sorted(self.twinList.items(), key=lambda item: len(item[0]))        # sort by length of possibility list
    #return ?

    def SetAllSinglePossibilities(self):

        for i in range(0, 9):
            for j in range (0,9):
                if ( (not self.board[self.index][i][j].solved)) and (len(self.board[self.index][i][j].possibilities) == 1):

                    old_Value = self.board[self.index][i][j].value
                    new_Value = self.board[self.index][i][j].possibilities[0]

                    self.moves.append({"row":i, "col":j, "value_before":old_Value, "value_after": new_Value })

                    self.board[self.index][i][j].value =  new_Value     # set the only possibility as a value
                    self.board[self.index][i][j].solved = True          # mark cell solved
                    self.CurrentBoard[i][j] = new_Value                 # maintain simple board copy

                    self.board[self.index][i][j].solved = True
                    self.setAllSpecials()  # recalculate all exceptions and possibilities

        tmp = copy.deepcopy(self.CurrentBoard)
        return tmp

    def Show(self):
        for i in range(0, 9):
            for j in range (0,9):
                print(self.board[self.index][i][j].value, end = " "),
            print("")
        print("="*20)


    def isSolved(self):
        res = False
        for i in range(0, 9):
            for j in range (0,9):
                if self.board[self.index][i][j].value == 0:
                    return False
                else:
                    res = True
        return res

    def Solve(self):
        solved = False

        while (not solved):
            myPuz.Show()
            solved = myPuz.isSolved()                       # is is solved yet?
            saved = myPuz.getCurrentBoard()                 # save arrays of the current board
            current = myPuz.SetAllSinglePossibilities()     # set all singular possibilities and save array again

            if (current == saved) and (not solved):         # if nothing changes and still unsolved
                print("Ran out of options SinglePossibility options")
                # use additional algorithm
                break

            if len(self.moves) > 500:  # safety pin
                print("Safety pin triggered. Too many moves")
                break

        return solved


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
'''
# complex
my_puzzle = [[1, 0, 4, 0, 0, 8, 0, 0, 6],
             [0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 6, 9, 0, 1, 0],
             [3, 0, 8, 9, 5, 0, 7, 0, 0],
             [5, 2, 0, 0, 0, 0, 0, 4, 3],
             [0, 0, 1, 0, 4, 3, 9, 0, 8],
             [0, 5, 0, 8, 2, 0, 0, 0, 0],
             [0, 0, 0, 0, 3, 0, 0, 0, 0],
             [4, 0, 0, 6, 0, 0, 1, 0, 7]]



myPuz = Puzzle(my_puzzle)                       # create puzzle
time_start = time.time()                        # get current time
solved = myPuz.Solve()                          # solve puzzle
time_dlt = round(time.time() - time_start,2)    # get time difference

if (solved):
    print("Sudoku is solved in %s seconds,  and %s placements" % (time_dlt , len(myPuz.moves)))
else:
    print("Sudoku is still UNRESOLVED in %s seconds,  and %s placements" % (time_dlt , len(myPuz.moves)))
    myPuz.seTwinList()

print("The End.")

# ToDo:
#   [X] Create twinList - list of identical possibilities for the board
#   [X] fix issue: remove twinList items where list of coordinates in the value is shorter than 2 items
#   [ ] Sort twinList dictionary by the length of the key
#   -
#   [ ] for each number (N) in possibility dictionary key (twinList)
#       [ ] for each coordinate set (R,C) in the current possibility dictionary key.value
#           [ ] copy puzzle, and set cell (R,C) to N
#           [ ] try to .Solve puzzle

#
# currently solves simple puzzles
# need to explore more options

