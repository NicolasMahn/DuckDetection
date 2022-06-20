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
import imageProcessingThread
import interactionThread

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
    # segmented_img = cv2.bitwise_and(image, image, mask=mask)

    # Find contours from the mask
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours


def startImageProcessingThread(c, filename, currentImage):
    x = threading.Thread(target=imageProcessingThread.analyse_image, args=(c, filename, currentImage))
    x.start()


def main():
    firstSicle = True
    startingSicles = True

    fmt = "%(asctime)s: %(message)s"
    logging.basicConfig(format=fmt, level=logging.INFO, datefmt="%H:%M:%S")

    currentImage = 1

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

        if startingSicles:
            roi = frame
        else:
            roi = frame[300:700, 700:frame.shape[1]]

        if time.time() - lastTime >= 1:
            lastTime = time.time()
            cnt = colorDetection(roi, ORANGE, 'Beak Detection')
            if startingSicles is False:
                filename = 'data/image/frame' + str(currentImage) + '.jpg'
                cv2.imwrite(filename, roi)
                logging.info("Image %s Saved", currentImage)
                startImageProcessingThread(cnt, filename, currentImage)
                currentImage += 1

        cv2.drawContours(roi, cnt, -1, (0, 0, 255), 3)
        roi = cv2.resize(roi, (int(roi.shape[1] / 2), int(roi.shape[0] / 2)), interpolation=cv2.INTER_AREA)
        cv2.imshow('Region of Interest', roi)
        code = cv2.waitKey(10)

        if code == ord('q'):
            break

        elif startingSicles:
            if firstSicle:
                firstSicle = False
                x = threading.Thread(target=interactionThread.beforeWeStart, args=())
                x.start()
            if not x.is_alive():
                startingSicles = False



if __name__ == "__main__":
    main()
