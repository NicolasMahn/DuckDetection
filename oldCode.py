from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import matplotlib.pyplot as plt
import numpy as np
from pyzbar.pyzbar import decode
import cvlog as log
import cv2
import imutils
import time


def templateMatching(image):
    # converting image into grayscale image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # setting threshold of gray image
    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # using a findContours() function
    contours, _ = cv2.findContours(
        threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    i = 0

    # list for storing names of shapes
    for contour in contours:

        # here we are ignoring first counter because
        # findcontour function detects whole image as shape
        if i == 0:
            i = 1
            continue

        # cv2.approxPloyDP() function to approximate the shape
        approx = cv2.approxPolyDP(
            contour, 0.01 * cv2.arcLength(contour, True), True)

        # using drawContours() function
        cv2.drawContours(image, [contour], 0, (0, 0, 255), 5)


def qrCodeDecoder(image):
    gray_img = cv2.cvtColor(image, 2)
    barcode = decode(gray_img)

    for obj in barcode:
        points = obj.polygon
        (x, y, w, h) = obj.rect
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (0, 255, 0), 3)

        barcodeData = obj.data.decode("utf-8")
        barcodeType = obj.type
        string = "Data " + str(barcodeData) + " | Type " + str(barcodeType)

        cv2.putText(image, string, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        print("Barcode: " + barcodeData + " | Type: " + barcodeType)


def dataMatrixDecoder(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    plt.subplot(151)
    plt.title('A')
    plt.imshow(image)

    harris = cv2.cornerHarris(image, 4, 1, 0.00)
    plt.subplot(152)
    plt.title('B')
    plt.imshow(harris)

    x, thr = cv2.threshold(harris, 0.1 * harris.max(), 255, cv2.THRESH_BINARY)
    thr = thr.astype('uint8')
    plt.subplot(153)
    plt.title('C')
    plt.imshow(thr)

    contours, hierarchy = cv2.findContours(thr.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    areas = map(lambda x: cv2.contourArea(cv2.convexHull(x)), contours)
    areas = list(areas)
    max_i = areas.index(max(areas))
    d = cv2.drawContours(np.zeros_like(thr), contours, max_i, 255, 1)
    plt.subplot(154)
    plt.title('D')
    plt.imshow(d)

    rect = cv2.minAreaRect(contours[max_i])
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    e = cv2.drawContours(image, [box], 0, 1, 1)
    plt.subplot(155)
    plt.title('E')
    plt.imshow(e)

    plt.show()