"""
:author NicolasMahn
"""

import threading

from ColorDetection import *
from ImageProcessingThread import *
from InteractionThread import *
from JsonProcessingThread import *


def startJsonProcessingThread(answer):
    """
    This method starts the JsonProcessingThread
    """
    x = threading.Thread(target=manage_results, args=(answer))
    x.start()
    return x


def startImageProcessingThread(filename, currentImage):
    """
    This method starts the ImageProcessingThread
    """
    x = threading.Thread(target=analyse_image, args=(filename, currentImage))
    x.start()
    pass


def main():
    """
    The main methode initialises everything
    """
    if exists(f"data/results.json"):
        answer = input("Should I delete the existing results file (N/y)? ")
    running = startJsonProcessingThread(answer)

    firstSicle = True
    justCropped = False
    Cropped = False
    Started = False

    ProcessedFPS = 60
    currentImage = 1

    cnt = None

    cap = cv2.VideoCapture(0)

    lastTime = time.time()

    while True:
        ret, frame = cap.read()

        if not Cropped:
            roi = frame
        else:
            roi = frame[300:700, 700:frame.shape[1]]

        if time.time() - lastTime >= 1/ProcessedFPS:
            lastTime = time.time()
            cnt = colorDetection(roi, ORANGE)

            if Started and len(cnt) > 0:
                for c in cnt:
                    if cv2.contourArea(c) > 100:
                        filename = 'data/image/frame' + str(currentImage) + '.jpg'
                        cv2.imwrite(filename, roi)
                        startImageProcessingThread(filename, currentImage)
                        currentImage += 1
                        break

        cv2.drawContours(roi, cnt, -1, (0, 0, 255), 3)
        roi = cv2.resize(roi, (int(roi.shape[1] / 2), int(roi.shape[0] / 2)), interpolation=cv2.INTER_AREA)
        cv2.imshow('Region of Interest', roi)
        cv2.waitKey(10)

        if not running.is_alive():
            break

        elif not Cropped:
            if firstSicle:
                firstSicle = False
                c = threading.Thread(target=beforeWeCrop, args=())
                c.start()
            if not c.is_alive():
                Cropped = True
                justCropped = True

        elif not Started:
            if justCropped:
                justCropped = False
                s = threading.Thread(target=beforeWeStart, args=())
                s.start()
            if not s.is_alive():
                Started = True
                print("STARTING")


if __name__ == "__main__":
    main()
