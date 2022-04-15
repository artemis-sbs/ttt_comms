from enum import Enum

class EndGame(Enum):
    UNKNOWN = 0
    X_WINS =1
    O_WINS =2
    DRAW = 99

class Turn(Enum):
    X_TURN = 1
    O_TURN = -1

class Board:
    checks = [
            # rows
            [0,1,2],
            [3,4,5],
            [6,7,8],
            #cols
            [0,3,6],
            [1,4,7],
            [2,5,8],
            #diag
            [0,4,8],
            [6,4,2]
        ]
    turn : Turn = Turn.X_TURN

    def __init__(self):
        self.clear()
        self.turn = Turn.X_TURN
        self.winning_loc = None

    def clear(self):
        self.grid = []
        for i in range(9):
            self.grid.append(EndGame.UNKNOWN)
        self.winning_loc = None

    def check_winner(self):
        g = self.grid
        draw = g[0].value
        for index, check in enumerate(Board.checks):
            draw *= g[index+1].value
            sum = g[check[0]].value+g[check[1]].value+g[check[2]].value
            if sum == 3:
                self.winning_loc = check
                return EndGame.X_WINS
            if sum == -3:
                self.winning_loc = check
                return EndGame.O_WINS
        
        # if any zero on grid draw would = 0
        # so non zero means draw        
        if draw != 0:
            return EndGame.DRAW

        return EndGame.UNKNOWN

    def set_grid(self, slot):
        if slot <0 or slot >8:
            return "Bad slot"
        elif (self.grid[slot] != EndGame.UNKNOWN):
            return "Slot already taken"
        else:
            self.grid[slot] = self.turn
            if self.turn == Turn.X_TURN:
                self.turn = Turn.O_TURN
            else:
                self.turn = Turn.X_TURN
        return None




