from ultralytics import YOLO
import cv2

# start webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# model
model = YOLO('yolov8m.pt')

# object classes
classNames = ["person"
  ,"bicycle"
  ,"car"
  ,"motorcycle"
  ,"airplane"
  ,"bus"
  ,"train"
  ,"truck"
  ,"boat"
  ,"traffic light"
  ,"fire hydrant"
  ,"stop sign"
  ,"parking meter"
  ,"bench"
  ,"bird"
  ,"cat"
  ,"dog"
  ,"horse"
  ,"sheep"
  ,"cow"
  ,"elephant"
  ,"bear"
  ,"zebra"
  ,"giraffe"
  ,"backpack"
  ,"umbrella"
  ,"handbag"
  ,"tie"
  ,"suitcase"
  ,"frisbee"
  ,"skis"
  ,'snowboard'
  ,'sports ball'
  ,'kite'
  ,'baseball bat'
  ,'baseball glove'
  ,'skateboard'
  ,'surfboard'
  ,'tennis racket'
  ,'bottle'
  ,'wine glass'
  ,'cup'
  ,'fork'
  ,'knife'
  ,'spoon'
  ,'bowl'
  ,'banana'
  ,'apple'
  ,'sandwich'
  ,'orange'
  ,'broccoli'
  ,'carrot'
  ,'hot dog'
  ,'pizza'
  ,'donut'
  ,'cake'
  ,'chair'
  ,'couch'
  ,'potted plant'
  ,'bed'
  ,'dining table'
  ,'toilet'
  ,'tv'
  ,'laptop'
  ,'mouse'
  ,'remote'
  ,'keyboard'
  ,'cell phone'
  ,'microwave'
  ,'oven'
  ,'toaster'
  ,'sink'
  ,'refrigerator'
  ,'book'
  ,'clock'
  ,'vase'
  ,'scissors'
  ,'teddy bear'
  ,"hair drier",
  "toothbrush"]


while True:
    success, img = cap.read()
    results = model(img, stream=True)

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

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()