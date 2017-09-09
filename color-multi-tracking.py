import cv2
import numpy as np

video_file = 'GOPR0579.MP4'

capture = cv2.VideoCapture(video_file)
while(True):
    # get the frame
    ret, frame = capture.read()

    #convert colors to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #clothes color range
    tq_lower = np.array([60, 37, 27], np.uint8)
    tq_upper = np.array([79, 144, 176], np.uint8)

    # finding the range of tq color in the image
    tq = cv2.inRange(hsv, tq_lower, tq_upper)

    # Morphological transformation, Dilation
    kernal = np.ones((5, 5), "uint8")

    tq = cv2.dilate(tq, kernal)
    cv2.bitwise_and(frame, frame, mask=tq)

    # Tracking the tq Color
    (_, contours, hierarchy) = cv2.findContours(tq, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # go through list of all found contours
    #TODO find way to join contours, if one contains the other, if two of them are close to each other they become one
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        # minimal contour size for it to be drawn
        if (area > 300):
            x, y, w, h = cv2.boundingRect(contour)
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
            cv2.putText(frame, "TQ color, area: " + str(area), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))

    cv2.imshow("Color Tracking", frame)
    #quit on q
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()