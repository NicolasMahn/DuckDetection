from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import matplotlib.pyplot as plt
import numpy as np
from pyzbar.pyzbar import decode
import cvlog as log
import cv2
import imutils
import logging
import threading
import time

# changing the color format from BGr to HSV
# This will be used to create the mask
import imageProcessing

BLUE = np.array([np.array([98, 50, 50]), np.array([139, 255, 255])])
YELLOW = np.array([np.array([20, 80, 80]), np.array([30, 255, 255])])
ORANGE = np.array([np.array([0, 50, 50]), np.array([10, 255, 255])])


def colorDetection(image, color, name="Color Detection"):
    kernel = np.ones((7, 7), np.uint8)

    into_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(into_hsv, color[0], color[1])

    # Remove unnecessary noise from mask
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Segment only the detected region
    segmented_img = cv2.bitwise_and(image, image, mask=mask)

    # Find contours from the mask
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    '''contours = imutils.grab_contours(contours)'''

    # Draw contour on original image
    # output = cv2.drawContours(image, contours, -1, (0, 0, 255), 3)

    # sort the contours from left-to-right and initialize the
    '''# 'pixels per metric' calibration variable
    (contours, _) = contours.sort_contours(contours)
    pixelsPerMetric = None

    # loop over the contours individually
    for c in contours:
        # if the contour is not sufficiently large, ignore it
        if cv2.contourArea(c) < 100:
            continue

        # compute the rotated bounding box of the contour
        orig = image.copy()
        box = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")'''

    # color = cv2.bitwise_and(image, image, mask=mask)
    # color = cv2.resize(color, dimentions, interpolation=cv2.INTER_AREA)
    # cv2.imshow(name, color)

    return contours


def startThread():
    x = threading.Thread(target=imageProcessing.analyse_image, args=(1,))
    x.start()


def main():
    fmt = "%(asctime)s: %(message)s"
    logging.basicConfig(format=fmt, level=logging.INFO, datefmt="%H:%M:%S")

    width = 640
    height = 480
    dim = (width, height)
    cnt = None

    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 5120)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2880)

    lastTime = time.time()

    while True:
        ret, frame = cap.read()
        if time.time() - lastTime >= 1:
            lastTime = time.time()
            cnt = colorDetection(frame, ORANGE, 'Beak Detection')
            startThread(cnt)
        cv2.drawContours(frame, cnt, -1, (0, 0, 255), 3)
        frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        cv2.imshow('Image', frame)
        code = cv2.waitKey(10)
        if code == ord('q'):
            break


if __name__ == "__main__":
    main()
