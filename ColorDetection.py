
import numpy as np
import cv2


BLUE = np.array([np.array([98, 50, 50]), np.array([139, 255, 255])])
YELLOW = np.array([np.array([20, 80, 80]), np.array([30, 255, 255])])
ORANGE = np.array([np.array([0, 50, 50]), np.array([10, 255, 255])])


def colorDetection(image, color):
    """
    detects colors in the image
    :return: the contours of the color
    """
    kernel = np.ones((7, 7), np.uint8)

    into_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(into_hsv, color[0], color[1])

    # Remove unnecessary noise from mask
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours from the mask
    cntrs, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return cntrs
