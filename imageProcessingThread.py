import logging
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours as contoursLibrary
import numpy as np
import argparse
import imutils
import cv2
import json
import pytesseract
from google.cloud import vision
import io

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

YMIN = 70
YMAX = 270


def analyse_image(cnts, filename, number):
    detect_text(filename)

    '''image = cv2.imread(filename)

    # sort the contours from left-to-right and initialize the
    (cnts, _) = contoursLibrary.sort_contours(cnts)
    i = 0
    # loop over the contours individually
    for c in cnts:
        if cv2.contourArea(c) > 100:
            i += 1

            

            M = cv2.moments(c)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])

            cyMin = cy - 200
            cyMax = cy + 200
            cxMin = cx - 200
            cxMax = cx + 200

            if cyMin <= YMIN:
                cyMin = YMIN
            elif cyMin < 0:
                cyMin = 0

            if cyMax >= YMAX:
                cyMax = YMAX

            if cxMin < 0:
                cxMin = 0

            logging.info(f"x: {cxMin}-{cxMax} y: {cyMin}-{cyMax}")
            roi = image[cyMin:cyMax, cxMin:cxMax]

            rgb = cv2.pyrDown(roi)
            small = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)

            _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
            connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
            # using RETR_EXTERNAL instead of RETR_CCOMP
            cntrs, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            # For opencv 3+ comment the previous line and uncomment the following line
            # _, contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            mask = np.zeros(bw.shape, dtype=np.uint8)

            (cntrs, _) = contoursLibrary.sort_contours(cntrs)

            j = 0
            for idx in range(len(cntrs)):
                j += 1
                x, y, w, h = cv2.boundingRect(cntrs[idx])
                mask[y:y + h, x:x + w] = 0
                # cv2.drawContours(mask, cntrs, idx, (255, 255, 255), -1)
                r = float(cv2.countNonZero(mask[y:y + h, x:x + w])) / (w * h)

                if r > 0.45 and w > 8 and h > 8:
                    cv2.rectangle(rgb, (x, y), (x + w - 1, y + h - 1), (0, 255, 0), 2)

                cropGrad = grad[y: y + h, x: x + w]

                text = pytesseract.image_to_string(cropGrad)
                print(text)



                filename = 'data/croppedImage/' + str(text) + '_frame' + str(number) + '.' + str(i) + '.' + str(j) +'.jpg'
                cv2.imwrite(filename, cropGrad)
                logging.info(f"Cropped Image {number}.{i}.{j} Saved")

    numBeaks = len(cnts) - i'''

    logging.info(f"Image {number} has been processed")


def detect_text(path):
    """Detects text in the file."""

    client_options = {'api_endpoint': 'eu-vision.googleapis.com'}

    client = vision.ImageAnnotatorClient(client_options=client_options)

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))