import logging
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2


def midpoint(ptA, ptB):
    return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5


def analyse_image(cnts, filename, place):
    image = cv2.imread(filename)

    # sort the contours from left-to-right and initialize the
    (cnts, _) = contours.sort_contours(cnts)

    # loop over the contours individually
    for c in cnts:
        if cv2.contourArea(c) < 100:
            continue



    logging.info("%s has been processed", filename)
