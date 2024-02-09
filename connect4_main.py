import pygame
from pygame.locals import *
import cv2
import numpy as np
import sys
from ultralytics import YOLO
import time

# CONSTANTS
ROWS = 6
COLUMNS = 7
RED_PIECE = 1
YELLOW_PIECE = -1
EMPTY = 0
CLASS_NAMES = ["Board", "Red Piece", "Yellow Piece"]
WIDTH = 1280
HEIGHT = 720
RADIUS = 30
BOARD_H = 6*100
BOARD_W = 7*100
READ_EVENT = pygame.USEREVENT+1
WIN_LENGTH = 4

# color constants
BLUE = (0,0,255)
WHITE = (255,255,255)
RED = (255,0,0)
YELLOW = (255,255,0)
GREY = (214,214,214)
BLACK = (30,30,30)
GREEN = (0,255,0)

# init webcam, cv-model, and pygame
camera = cv2.VideoCapture(0)
pygame.init()
pygame.display.set_caption("Computer Vision Connect4")
screen = pygame.display.set_mode([WIDTH,HEIGHT])
model = YOLO("runs/detect/yolov8n_connect4/weights/best.pt")

# game states
state = "start_menu"
first_player = ""
playing_piece = 1
played_piece = -1

def read_frame(results):
    # init board
    board = np.zeros((ROWS,COLUMNS))

    # init pieces list
    pieces = []

    # board detected flag
    board_found = False

    # cycle through detected objects
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # get bounding box coords
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

            # get class name
            cls = int(box.cls[0])

            # save locations of pieces and board
            if CLASS_NAMES[cls] == "Board":
                board_dims = (x1, y1, x2, y2)
                board_found = True
            else:
                pieces.append((CLASS_NAMES[cls], x1, y1, x2, y2))
            
        if board_found:
            width = board_dims[2] - board_dims[0]
            height = board_dims[3] - board_dims[1]

            # may need to edit these value if mirroring is an issue on non webcam cameras
            columns = [int(width/14)+board_dims[0], int(width/14 + width/7)+board_dims[0],
                        int(width/14 + 2*width/7)+board_dims[0], int(width/14 + 3*width/7)+board_dims[0],
                        int(width/14 + 4*width/7)+board_dims[0], int(width/14 + 5*width/7)+board_dims[0],
                        int(width/14 + 6*width/7)+board_dims[0]]
            
            rows = [int(height/12) + board_dims[1], int(height/12 + height/6) + board_dims[1],
                    int(height/12 + 2*height/6) + board_dims[1], int(height/12 + 3*height/6) + board_dims[1],
                    int(height/12 + 4*height/6) + board_dims[1], int(height/12 + 5*height/6) + board_dims[1]]

            for piece in pieces:
                mid_x = int((piece[3] - piece[1]) / 2) + piece[1]
                mid_y = int((piece[4] - piece[2]) / 2) + piece[2]

                row = min(range(len(rows)), key = lambda i: abs(rows[i]-mid_y))
                col = min(range(len(columns)), key = lambda i: abs(columns[i]-mid_x))

                if piece[0] == "Red Piece":
                    board[row, col] = 1
                else:
                    board[row, col] = -1

            # print board for debugging purposes
            # for x in range(len(board)):
            #     for y in range(len(board[x])):
            #         print(board[x][y], end=" ")
            #     print("")
    return board

def draw_menu():
    # show menu
    screen.fill(GREY)
    prompt =  pygame.image.load("assets/prompt1.png").convert_alpha()
    screen.blit(prompt, ((WIDTH/2)-(prompt.get_width()/2), (HEIGHT/2)-(prompt.get_height()/2)-100))
    
    red_prompt =  pygame.image.load("assets/red_prompt.png").convert_alpha()
    yellow_prompt =  pygame.image.load("assets/yellow_prompt.png").convert_alpha()
    
    r_button = pygame.Rect((WIDTH/3)-(red_prompt.get_width()/2), (3*HEIGHT/4)-(red_prompt.get_height()/2), red_prompt.get_width(), red_prompt.get_height())
    y_button = pygame.Rect((2*WIDTH/3)-(yellow_prompt.get_width()/2), (3*HEIGHT/4)-(yellow_prompt.get_height()/2), yellow_prompt.get_width(), yellow_prompt.get_height())

    pygame.draw.rect(screen, GREY, r_button)
    pygame.draw.rect(screen, GREY, y_button)
    screen.blit(red_prompt, r_button)
    screen.blit(yellow_prompt, y_button)

    pygame.display.flip()

    return (y_button, r_button)                  

def draw_board(image, board):
    # create board
    screen.fill(GREY)
    pygame.draw.rect(screen, BLUE, pygame.Rect((WIDTH/2)-(BOARD_W/2), (HEIGHT/2)-(BOARD_H/2), BOARD_W, BOARD_H))
    for r in range(ROWS):
        for c in range(COLUMNS):
            color = BLACK
            if board[r, c] == 1:
                color = RED
            elif board[r, c] == -1:
                color = YELLOW
            
            pygame.draw.circle(screen, color, ((WIDTH/2)-(BOARD_W/2) +
                                                ((c+.5)*BOARD_W/COLUMNS), (HEIGHT/2)-(BOARD_H/2) + ((r+.5)*BOARD_H/ROWS)), RADIUS)
    # TODO : fix this to display properly
    # camera_surf = pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "BGR")
    # screen.blit(camera_surf, (0, 0))
    pygame.display.flip()

# Search the board to ensure it follows proper connect4 rules
def get_best_board(old_board, new_board):
    # check to make sure no 'floating' pieces
    for c in range(COLUMNS):
        found = False
        for r in range(ROWS):
            if new_board[r, c] != 0:
                found = True
                continue
            if found and new_board[r, c] == 0:
                return old_board

    # make sure there is the proper amount of pieces
    # count the number of unique entries and zip into dict
    unique, counts = np.unique(new_board, return_counts=True)
    piece_count = dict(zip(unique, counts))

    #detect if none or only piece type exists then only the player that went first has played or no one has played
    if piece_count.get(1) == None or piece_count.get(-1) == None:
        if (piece_count.get(1) == None and piece_count.get(-1) == None) or \
           (piece_count.get(1) == None and first_player == "yellow" and piece_count.get(-1) == 1) or \
           (piece_count.get(-1) == None and first_player == "red" and piece_count.get(1) == 1):
            return new_board
        else:
            return old_board
    # make sure proper number of pieces are present depending on who went first
    elif piece_count[1] == piece_count[-1] or \
        first_player == "red" and (piece_count[1]-1) == piece_count[-1] or \
        first_player == "yellow" and (piece_count[-1]-1) == piece_count[1]:
        return new_board
    else:
        return old_board
#-------------------------------------------------------------------------------------------------------------------------------
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMNS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_valid_location(board, col):
    return board[ROWS - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROWS):
        if board[r][col] == 0:
            return r    

def drop_piece(board, row, col, piece):
    board[row][col] = piece    

def score_position(board, piece):
    score = 0

    # Score centre column
    centre_array = [int(i) for i in list(board[:, COLUMNS // 2])]
    centre_count = centre_array.count(piece)
    score += centre_count * 3

    # Score horizontal positions
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMNS - 3):
            # Create a horizontal window of 4
            window = row_array[c:c + WIN_LENGTH]
            score += evaluate_window(window, piece)

    # Score vertical positions
    for c in range(COLUMNS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            # Create a vertical window of 4
            window = col_array[r:r + WIN_LENGTH]
            score += evaluate_window(window, piece)

    # Score positive diagonals
    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            # Create a positive diagonal window of 4
            window = [board[r + i][c + i] for i in range(WIN_LENGTH)]
            score += evaluate_window(window, piece)

    # Score negative diagonals
    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            # Create a negative diagonal window of 4
            window = [board[r + 3 - i][c + i] for i in range(WIN_LENGTH)]
            score += evaluate_window(window, piece)

    return score    

def evaluate_window(window, piece):
    score = 0
    # Switch scoring based on turn
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = BOT_PIECE

    # Prioritise a winning move
    # Minimax makes this less important
    if window.count(piece) == 4:
        score += 100
    # Make connecting 3 second priority
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    # Make connecting 2 third priority
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    # Prioritise blocking an opponent's winning move (but not over bot winning)
    # Minimax makes this less important
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score    

def winning_move(board, piece):
    # Check valid horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # Check valid vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check valid positive diagonal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # check valid negative diagonal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True    

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, BOT_PIECE) or len(get_valid_locations(board)) == 0    

def minimax(board, depth, alpha, beta, maximisingPlayer):
    valid_locations = get_valid_locations(board)

    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            # Weight the bot winning really high
            if winning_move(board, BOT_PIECE):
                return (None, 9999999)
            # Weight the human winning really low
            elif winning_move(board, PLAYER_PIECE):
                return (None, -9999999)
            else:  # No more valid moves
                return (None, 0)
        # Return the bot's score
        else:
            return (None, score_position(board, BOT_PIECE))

    if maximisingPlayer:
        value = -9999999
        # Randomise column to start
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            # Create a copy of the board
            b_copy = board.copy()
            # Drop a piece in the temporary board and record score
            drop_piece(b_copy, row, col, BOT_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                # Make 'column' the best scoring column we can get
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimising player
        value = 9999999
        # Randomise column to start
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            # Create a copy of the board
            b_copy = board.copy()
            # Drop a piece in the temporary board and record score
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                # Make 'column' the best scoring column we can get
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value
    

#-------------------------------------------------------------------------------------------------------------------------------

# Main
try:
    old_board = np.zeros((ROWS,COLUMNS))
    board = np.zeros((ROWS,COLUMNS))
    while True:
        # read frame and get predictions
        ret, image = camera.read()
        results = model(image, stream=True)

        # save old board, get new board
        old_board = board
        board = read_frame(results)

        ## Play connect4 here using refrenced board
        if state == "start_menu":
            buttons = draw_menu()

        if state == "board":
            board = get_best_board(old_board, board)
            draw_board(image, board)

        for event in pygame.event.get():
            if event.type == KEYDOWN or event.type == pygame.QUIT:
                  pygame.display.quit()
                  pygame.quit()
                  sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons[0].collidepoint(event.pos):
                    state = "board"
                    first_player = "yellow"
                elif buttons[1].collidepoint(event.pos):
                    state = "board"
                    first_player = "red"
                            
except KeyboardInterrupt or SystemExit:
    pygame.quit()
    cv2.destroyAllWindows()