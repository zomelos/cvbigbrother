import argparse
import time
import cv2


def find_object_by_coords(_objects, coords, threshold):
    for obj in _objects:
        if abs(obj[0] - coords[0]) < threshold and abs(obj[0] - coords[0]) < threshold:
            return _objects.index(obj)
    return None


def is_new_object_allowed_by_coords(width, height, coords):
    min_width = width / 5
    min_height = height / 5
    return (coords[0] < min_width or coords[0] > width - min_width) \
        and (coords[1] < min_height or coords[1] > height - min_height)


def get_command_arguments():

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
    ap.add_argument("-z", "--max-area", type=int, default=50000, help="maximum area size")
    ap.add_argument("-t", "--same-object-threshold", type=int, default=50, help="threshold for treating moves as same object")
    return vars(ap.parse_args())


def draw_objects(_objects):
    for obj in _objects:
        cv2.circle(frame, (obj[0], obj[1]), 10, (0, 255, 0), -1)
        cv2.putText(frame, "object {}".format(_objects.index(obj)), (obj[0] - 15, obj[1] - 15), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 0, 255))
        #print(frameCount, objects.index(obj), obj[0], obj[1], sep=";")


args = get_command_arguments()

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)

# otherwise, we are reading from a video file
else:
    camera = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None
previousFrame = None

objects = []

frameCount = 0

if camera.isOpened():
    width = camera.get(3)
    height = camera.get(4)

# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break
    frameCount += 1
    # convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue
    if previousFrame is None:
        previousFrame = gray

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta1 = cv2.absdiff(gray, previousFrame)
    frameDelta2 = cv2.absdiff(previousFrame, firstFrame)
    frameDelta = cv2.bitwise_and(frameDelta1, frameDelta2)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_TRIANGLE)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=4)

    (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        area = cv2.contourArea(c)
        if area < args["min_area"] or area > args["max_area"]:
            continue
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        centerX = int((x + w / 2))
        centerY = int((y + h / 2))
        index = find_object_by_coords(objects, [centerX, centerY], args["same_object_threshold"])
        if index is None:
            if is_new_object_allowed_by_coords(width, height, [centerX, centerY]):
                print("New object detected!")
                objects.append([centerX, centerY])
            else:
                print("New object not allowed here, not creating", centerX, centerY, width, height)
        else:
            objects[index] = [centerX, centerY]

    draw_objects(objects)

    previousFrame = gray

    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the loop
    if key == ord("q"):
        break

    # too fast, we should wait a bit
    time.sleep(0.009)
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
