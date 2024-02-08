from ultralytics import YOLO
import cv2
import time
# start webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# model
model = YOLO("best.pt")

# object classes
classNames = ["Board", "Red Piece", "Yellow Piece"]

# Choose how often frames are read
frame_rate = 1
prev = 0

while True:
    time_elapsed = time.time() - prev
    success, img = cap.read()
    results = model(img, stream=True)

    # gather information to create board
    board = [['o']*7, ['o']*7, ['o']*7,
                ['o']*7, ['o']*7, ['o']*7]
    pieces = []
    board_found = False

    # coordinates
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

            # put box in cam
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # class name
            cls = int(box.cls[0])

            # object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2

            # place label
            cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)

            # save locations of pieces and board
            if classNames[cls] == "Board":
                board_dims = (x1, y1, x2, y2)
                board_found = True
            else:
                pieces.append((classNames[cls], x1, y1, x2, y2))
                    
        if time_elapsed > 1./frame_rate:
            prev = time.time()
            
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

                    #print(mid_x, "in", rows, "and", mid_y, "in", columns)

                    row = min(range(len(rows)), key = lambda i: abs(rows[i]-mid_y))
                    col = min(range(len(columns)), key = lambda i: abs(columns[i]-mid_x))

                    if piece[0] == "Red Piece":
                        board[row][col] = "r"
                    else:
                        board[row][col] = "y"

                for x in range(len(board)):
                    for y in range(len(board[x])):
                        print(board[x][y], end=" ")
                    print("")


    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()