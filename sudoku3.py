import time
import copy

class Cell:

    def __init__(self, row, col, value=0):
        self.value  = value                 # current value
        self.solved = False                 # this cell is solved
        self.row = row                      # cell row position
        self.col = col                      # cell column position
        self.exceptions = []                # list of values not allowed in cell due to position
        self.possibilities = []             # list of allows possible values

class Puzzle:

    def __init__(self, puzzle):
        self.move = 0
        self.index = 0
        self.bookmark = 0
        self.board = []             # array of boards
        self.CurrentBoard = puzzle.copy()  # simple array representation of the board

        #self.branch = {
        #
        #}


        self.board.append([])       # add first primary board

        for i in range(0,9):
            self.board[self.index].append([])   # cN    eate new row
            for j in range (0,9):
                # self.board[i].append(puzzle[i][j]) # add column
                self.board[self.index][i].append(Cell(i,j,puzzle[i][j]))
                self.board[self.index][i][j].solved = puzzle[i][j] != 0
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
        tmp = set(self.getBlock(row, col) + self.getCol(col) + self.getRow(row))
        tmp = [elem for elem in tmp if elem != 0]  # remove all zeros
        return tmp

    def getPossibleNumbers(self, row, col):
        allNumbers =  [1, 2, 3, 4, 5, 6, 7, 8, 9]
        exceptionList = self.getExceptions(row, col)
        return list(set(allNumbers) - set(exceptionList))

    def setAllSpecials(self):
        for i in range(0, 9):
            for j in range (0,9):
                self.board[self.index][i][j].exceptions = self.getExceptions(i, j)
                self.board[self.index][i][j].possibilities = self.getPossibleNumbers(i, j)

    def SetAllSinglePossibilities(self):
        #count = []
        for i in range(0, 9):
            for j in range (0,9):
                if ( (not self.board[self.index][i][j].solved)) and (len(self.board[self.index][i][j].possibilities) == 1):
                    self.board[self.index][i][j].value =  self.board[self.index][i][j].possibilities[0]  # set the only possibility as a value
                    self.CurrentBoard[i][j] = self.board[self.index][i][j].value # maintain simple board copy
                    self.move += 1
                    self.board[self.index][i][j].solved = True
                    self.setAllSpecials()  # recalculate all exceptions and possibilities
                    #count.append((i,j))
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
        self.move = 0

        while (not solved):
            myPuz.Show()
            solved = myPuz.isSolved()                       # is is solved yet?
            saved = myPuz.getCurrentBoard()                 # save arrays of the current board
            current = myPuz.SetAllSinglePossibilities()     # set all singular possibilities and save array again

            if (current == saved) and (not solved):         # if nothing changes and still unsolved
                print("Ran out of options SinglePossibility options")
                # use additional algorithm
                break

            if self.move > 1000:  # safety pin
                break
            else:
                self.move += 1
        return solved


# main module

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
my_puzzle = [[1, 0, 4, 0, 0, 8, 0, 0, 6],
             [0, 0, 0, 0, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 6, 9, 0, 1, 0],
             [3, 0, 8, 9, 5, 0, 7, 0, 0],
             [5, 2, 0, 0, 0, 0, 0, 4, 3],
             [0, 0, 1, 0, 4, 3, 9, 0, 8],
             [0, 5, 0, 8, 2, 0, 0, 0, 0],
             [0, 0, 0, 0, 3, 0, 0, 0, 0],
             [4, 0, 0, 6, 0, 0, 1, 0, 7]]

'''

myPuz = Puzzle(my_puzzle)

start_time = time.time()

solved = myPuz.Solve()

if (solved):
    print("Sudoku is solved in %s seconds,  and %s placements" % (round(time.time() - start_time,2), myPuz.move))
else:
    print("Sudoku is still UNSOLVED  in %s seconds, %s board iteration and %s placements" % (round(time.time() - start_time,2), i, myPuz.move))

print("The End.")

# currently solves simple puzzles
# need to explore more options