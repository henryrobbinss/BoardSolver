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

BLUE = (0,0,255)
WHITE = (255,255,255)
RED = (255,0,0)
YELLOW = (255,255,0)
GREY = (214,214,214)
BLACK = (30,30,30)

# init webcam and pygame
camera = cv2.VideoCapture(0)
pygame.init()
pygame.display.set_caption("Computer Vision Connect4")
screen = pygame.display.set_mode([WIDTH,HEIGHT])
model = YOLO("best.pt")
in_game = False

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

            # may need to edit these value if mirroring is an issue
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

try:
    while True:
        # read frame and get predictions
        ret, image = camera.read()
        results = model(image, stream=True)

        # read image once every 3 seconds
        if pygame.time.get_ticks() % 3000 == 0:
            print("REACHED")#scanned_board = read_frame(results)

        ## Play connect4 here using refrenced board
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

        while not in_game:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if y_button.collidepoint(event.pos):
                        in_game = True
                    elif r_button.collidepoint(event.pos):
                        in_game = True
                elif event.type == KEYDOWN or event.type == pygame.QUIT:
                  pygame.display.quit()
                  pygame.quit()
                  sys.exit(0)

        # create board
        screen.fill(GREY)
        pygame.draw.rect(screen, BLUE, pygame.Rect((WIDTH/2)-(BOARD_W/2), (HEIGHT/2)-(BOARD_H/2), BOARD_W, BOARD_H))
        for c in range(COLUMNS):
            for r in range(ROWS):
                pygame.draw.circle(screen, BLACK, ((WIDTH/2)-(BOARD_W/2) +
                                                   ((c+.5)*BOARD_W/COLUMNS), (HEIGHT/2)-(BOARD_H/2) + ((r+.5)*BOARD_H/ROWS)), RADIUS)
        pygame.display.flip()

        for event in pygame.event.get():
              if event.type == KEYDOWN or event.type == pygame.QUIT:
                  pygame.display.quit()
                  pygame.quit()
                  sys.exit(0)
                            
except KeyboardInterrupt or SystemExit:
    pygame.quit()
    cv2.destroyAllWindows()