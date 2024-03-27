import numpy as np

first_player = "red"
RED_PIECE = 1
YELLOW_PIECE = -1

# convert 2D array into solver format string
def convert_board(board):
    board = np.flipud(board)
    pending_moves = []
    next = first_player
    finalString = ""
    for row in board:
        for i in range(len(row)):
            if row[i] == 0:
                continue
            elif next == "red" and row[i] == RED_PIECE:
                finalString = "".join([finalString, str(i + 1)])
                if len(pending_moves) != 0:
                    finalString = "".join([finalString, str(pending_moves[0])])
                    pending_moves[0] = pending_moves[-1]
                    pending_moves.pop()
                else:
                    next = "yellow"
            elif next == "yellow" and row[i] == YELLOW_PIECE:
                finalString = "".join([finalString, str(i + 1)])
                if len(pending_moves) != 0:
                    finalString = "".join([finalString, str(pending_moves[0])])
                    pending_moves[0] = pending_moves[-1]
                    pending_moves.pop()
                else:
                    next = "red"
            else:
                pending_moves.append(str(i + 1))
    finalString = "".join([finalString] + pending_moves)
    return finalString

board = np.zeros((6,7))

board[5, 6] = RED_PIECE
board[5, 5] = RED_PIECE
board[5, 4] = RED_PIECE

board[4, 6] = YELLOW_PIECE
board[4, 5] = YELLOW_PIECE
board[5, 0] = YELLOW_PIECE

print(convert_board(board))