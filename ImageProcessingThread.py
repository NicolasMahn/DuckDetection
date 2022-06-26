"""
:author NicolasMahn
"""

import json
from google.cloud import vision
import io


def analyse_image(filename, number):
    """
    The image is analysed for text in it which is saved
    :param filename: the name of the image where text is to be found
    :param number: the number of the image where text is to be found
    """
    t = detect_text(filename)

    jsonObject = json.dumps(t, indent=4)

    with open(f"data/framejsons/frame{number}.json", "w") as outfile:
        outfile.write(jsonObject)
    pass


def detect_text(path):
    """
    Detects text in the file with the help of Google Image detection.
    :param path: The path to the image with the text
    :return: the text in the image is returned
    """

    client_options = {'api_endpoint': 'eu-vision.googleapis.com'}

    client = vision.ImageAnnotatorClient(client_options=client_options)

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    t = list()
    first = True
    for text in texts:
        if not first:
            t.append(text.description)
        else:
            first = False

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return t
