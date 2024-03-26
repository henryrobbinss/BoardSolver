import pygame
from pygame.locals import *
import cv2
import numpy as np
import sys
from ultralytics import YOLO
import example

# CONSTANTS
ROWS = 6
COLUMNS = 7
RED_PIECE = 1
YELLOW_PIECE = -1
EMPTY = 0
CLASS_NAMES = ["Board", "Red Piece", "Yellow Piece", "No Piece"]
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
            elif CLASS_NAMES[cls] != "No Piece":
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
            for x in range(len(board)):
                for y in range(len(board[x])):
                    print(board[x][y], end=" ")
                print("")
            print("Move seq: " + convert_board(board))
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

    # Make this the 
    # red_prompt =  pygame.image.load("assets/red_prompt.png").convert_alpha()    
    # r_button = pygame.Rect((WIDTH/3)-(red_prompt.get_width()/2), (3*HEIGHT/4)-(red_prompt.get_height()/2), red_prompt.get_width(), red_prompt.get_height())
    # pygame.draw.rect(screen, GREY, r_button)
    # screen.blit(red_prompt, r_button)

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
    
    # col = example.solve(convert_board(board))
    col = 4 - 1
    for i in range(ROWS-1, -1, -1):
        if board[i, col] == 0:
            pygame.draw.circle(screen, GREEN, ((WIDTH/2)-(BOARD_W/2) +
                            ((col+.5)*BOARD_W/COLUMNS), (HEIGHT/2)-(BOARD_H/2) + ((i+.5)*BOARD_H/ROWS)), RADIUS)
            break
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

# convert 2D array into solver format string
def convert_board(board):
    pending_moves = []
    next = first_player
    finalString = ""
    for row in board:
        for i in range(len(row)):
            if row[i] == 0:
                continue
            elif next == "red" and row[i] == RED_PIECE:
                finalString = finalString.join(str(i + 1))
                if len(pending_moves) != 0:
                    finalString = finalString.join(str(pending_moves[0]))
                    pending_moves[0] = pending_moves[-1]
                    pending_moves.pop()
                else:
                    next = "yellow"
            elif next == "yellow" and row[i] == YELLOW_PIECE:
                finalString = finalString.join(str(i + 1))
                if len(pending_moves) != 0:
                    finalString = finalString.join(str(pending_moves[0]))
                    pending_moves[0] = pending_moves[-1]
                    pending_moves.pop()
                else:
                    next = "red"
            else:
                pending_moves.append(str(i + 1))
    finalString = finalString.join(pending_moves)
    return finalString

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