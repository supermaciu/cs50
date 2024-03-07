"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if terminal(board):
        return None
    
    xcount = 0
    ocount = 0

    for i in range(3):
        for j in range(3):
            if board[i][j] == "X":
                xcount += 1
            elif board[i][j] == "O":
                ocount += 1

    if xcount == ocount:
        return "X"
    else:
        return "O"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if terminal(board):
        return None

    possible_actions = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))
    
    return possible_actions
                

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if terminal(board):
        return None

    if action is None or type(action) is not tuple:
        raise Exception("invalid action type")

    i, j = action
    if not (0 <= i <= 3 and 0 <= j <= 3):
        raise Exception("invalid action")

    if board[i][j] != EMPTY:
        raise Exception("move taken")

    board_copy = copy.deepcopy(board)

    p = player(board_copy)
    board_copy[i][j] = p

    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # horizontal
    xcount = 0
    ocount = 0

    for i in range(3):
        xcount = board[i].count("X")
        ocount = board[i].count("O")

        if xcount == 3:
            return "X"
        elif ocount == 3:
            return "O"
    
    # vertical
    for i in range(3):
        xcount = 0
        ocount = 0

        for j in range(3):
            xcount += (board[j][i] == "X")
            ocount += (board[j][i] == "O")
            
        if xcount == 3:
            return "X"
        elif ocount == 3:
            return "O"
    
    #diagonal
    if board[0][0] == "X" and board[1][1] == "X" and board[2][2] == "X" or board[0][2] == "X" and board[1][1] == "X" and board[2][0] == "X":
        return "X"
    elif board[0][0] == "O" and board[1][1] == "O" and board[2][2] == "O" or board[0][2] == "O" and board[1][1] == "O" and board[2][0] == "O":
        return "O"

    return None
    

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    filled = sum([board[i].count(EMPTY) for i in range(3)])
    return winner(board) != None or filled == 0


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    w = winner(board)
    if w == "X":
        return 1
    elif w == "O":
        return -1
    else:
        return 0


def max_value(board, alpha=-math.inf, beta=math.inf):
    """
    "X / The maximizing player". Returns the max value of all possible actions (utility(action)).
    Alpha and beta parameters for alpha-beta pruning.
    """
    if terminal(board):
        return utility(board)
    
    v = -math.inf

    for a in actions(board):
        v = max(v, min_value(result(board, a), math.inf, alpha))
        
        alpha = max(alpha, v)

        if (v > beta):
            return v

    return v


def min_value(board, alpha=math.inf, beta=-math.inf):
    """
    "O / The minimizing player". Returns the min value of all possible actions (utility(action)).
    Alpha and beta parameters for alpha-beta pruning.
    """
    if terminal(board):
        return utility(board)
    
    v = math.inf

    for a in actions(board):
        v = min(v, max_value(result(board, a), -math.inf, alpha))

        alpha = min(alpha, v)

        if (v < beta):
            return v

    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    ai = player(board)
    
    if ai == "X":
        max = (-math.inf, None)
        for action in actions(board):
            value = min_value(result(board, action))

            if value >= max[0]:
                max = (value, action)
        
        return max[1]
    elif ai == "O":
        min = (math.inf, None)
        for action in actions(board):
            value = max_value(result(board, action))

            if value <= min[0]:
                min = (value, action)

        return min[1]

