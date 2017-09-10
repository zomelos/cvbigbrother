import argparse
import time
import cv2
import showProducts as sp
import numpy as np
import time


def find_object_by_coords(_objects, coords, threshold):
    for obj in _objects:
        if not obj[3]:
            continue
        if abs(obj[0] - coords[0]) < threshold and abs(obj[0] - coords[0]) < threshold:
            return _objects.index(obj)
    return None


def get_object_vector(_object, coords):
    return [coords[0] - _object[0], coords[1] - _object[1]]


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
        if not obj[3]:
            continue
        cv2.circle(frame, (obj[0], obj[1]), 10, (0, 255, 0), -1)
        cv2.putText(frame, "object {} ({},{})".format(_objects.index(obj), obj[0], obj[1]), (obj[0] - 15, obj[1] - 15), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (255, 255, 0))
        #print(frameCount, objects.index(obj), obj[0], obj[1], sep=";")


def is_looking_at_item(visitor_objects):
    #print(productPositions, visitor_objects)

    for product in productPositions:
        (productId, x1, y1, x2, y2, productName) = product
        for visIndex,visitor in enumerate(visitor_objects):
            (visitor_x, visitor_y, visitor_area, visitor_status) = visitor
            unique = str(productId) + '-' + str(visIndex)
            if visitor_x >= x1 and visitor_x <= x2 and visitor_y >= y1 and visitor_y <= y2:
                #has previous entry
                if unique in inside_of_product_zone:
                    if time.time() - inside_of_product_zone[unique]['timestamp'] >= 3 and inside_of_product_zone[unique]['visit_counted'] == False:
                        inside_of_product_zone[unique]['visit_counted'] = True
                        visits[productId]['visits'] += 1

                        #print(visits)
                #does not have previous entry
                else:
                    inside_of_product_zone[unique] = {'timestamp': time.time(), 'visit_counted': False}

            #outside of product zone
            else:
                if unique in inside_of_product_zone:
                    del inside_of_product_zone[unique]

def display_product_visits(frame):
    row_x_pos = int(video_width - 160)
    row_y_pos = 10
    cv2.putText(frame, "Product - Visits", (row_x_pos, row_y_pos), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (255, 255, 255))
    #print(visits)
    for index, v in visits.items():
        row_y_pos += 16
        cv2.putText(frame, str(v['name']) + ": " + str(v['visits']), (row_x_pos, row_y_pos), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (255, 255, 255))

        # cv2.putText(frame, "{} - {}".format(_objects.index(obj), obj[0], obj[1]), (obj[0] - 15, obj[1] - 15),
    #             cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (255, 255, 0))



# convert frame to grayscale
def frame_to_grayscale(_frame):
    _gray = cv2.cvtColor(_frame, cv2.COLOR_BGR2GRAY)
    _gray = cv2.GaussianBlur(_gray, (11, 11), 0)
    return _gray


def process_frame_diff(_frame, _previousFrame, _firstFrame):
    frameDelta1 = cv2.absdiff(_frame, _previousFrame)
    frameDelta2 = cv2.absdiff(_previousFrame, _firstFrame)
    frameDelta = cv2.bitwise_and(frameDelta1, frameDelta2)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_TRIANGLE)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    return cv2.dilate(thresh, None, iterations=4)


def detect_objects(_processed_frame):
    global nextDetectionFrame
    (_, cnts, _) = cv2.findContours(_processed_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # loop over the contours
    for c in cnts:
        area = cv2.contourArea(c)
        if area < args["min_area"] or area > args["max_area"]:
            continue
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        centerX = int((x + w / 2))
        centerY = int((y + h / 2))
        if frame_id >= nextDetectionFrame:
            index = find_object_by_coords(objects, [centerX, centerY], args["same_object_threshold"])
            if index is None:
                if is_new_object_allowed_by_coords(width, height, [centerX, centerY]):
                    objects.append([centerX, centerY, 0, True])
            else:
                vector = get_object_vector(objects[index], [centerX, centerY])
                objects[index] = [centerX, centerY, objects[index][2] + np.linalg.norm(vector), True]
                if centerX > width - 80 and centerY > height - 80:
                    if vector[0] > 0 and vector[1] > 0 and objects[index][2] > 200:
                        objects[index][3] = False
                        nextDetectionFrame = frame_id + 30


args = get_command_arguments()

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)

# otherwise, we are reading from a video file
else:
    camera = cv2.VideoCapture(args["video"])

productPositions = sp.getProducts()

visits = {}
for product in productPositions:
    visits[product[0]] = {'visits': 0, 'name': product[5]}

inside_of_product_zone = {}


# initialize the first frame in the video stream
firstFrame = None
previousFrame = None

objects = []

frameCount = 0
nextDetectionFrame = 0

if camera.isOpened():
    video_width = camera.get(3)
    video_height = camera.get(4)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 60.0, (848,480))

# loop over the frames of the video
frame_id = 0
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    frame_id += 1

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    gray = frame_to_grayscale(frame)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue
    if previousFrame is None:
        previousFrame = gray

    thresh = process_frame_diff(gray, previousFrame, firstFrame)

    detect_objects(thresh)

    draw_objects(objects)
    is_looking_at_item(objects)
    for obj_index, obj in enumerate(objects):
        #cv2.circle(frame, (obj[0], obj[1]), 10, (0, 255, 0), -1)
        sp.storePosition(frame_id, obj_index, obj[0], obj[1])
        #print(frameCount, objects.index(obj), obj[0], obj[1], sep=";")

    previousFrame = gray

    sp.drawProducts(frame, productPositions)
    display_product_visits(frame)

    out.write(frame)

    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)

    key = cv2.waitKey(10) & 0xFF

    # if the `q` key is pressed, break from the loop
    if key == ord("q"):
        break

    # too fast, we should wait a bit
    #time.sleep(0.009)
# cleanup the camera and close any open windows
out.release()
camera.release()
cv2.destroyAllWindows()
