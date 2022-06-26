"""
This File analyses the detected numbers
:author: NicolasMahn
"""
import json
import os.path
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from os.path import exists

from Problems import *
from Util import *

last20 = dict()
last6 = dict()
detectedDucks = set()
currentPlace = 1

clock = time.time()
requestPossible = True
publishOverdraft = dict()


def updateLast20():
    """
    This method simply updates last20 by one iteration
    """
    delNums = list()
    global last20
    print(f"last20: {last20}")
    for num in last20:
        if last20[num] > 20:
            delNums.append(num)
        else:
            last20[num] = last20[num] + 1

    for num in delNums:
        del last20[num]
    pass


def updateLast6():
    """
    This method simply updates last6 by one iteration
    """
    delNums = list()
    global last6
    print(f"last6: {last6}")
    for num in last6:
        if last6[num]["age"] > 6:
            delNums.append(num)
        else:
            last6[num]["age"] += 1

    for num in delNums:
        del last6[num]
    pass


def addToWebsite(publish):
    """
    This methode publishes the results to a goggle spreadsheet, which is then automatically publicised on the website
    :param publish: the results to be published
    """
    global publishOverdraft
    global requestPossible
    global clock
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("entennrennen-furtwangen-5365c29884ee.json", scope)
    client = gspread.authorize(creds)
    publish.update(publishOverdraft)
    if requestPossible:
        try:
            sheet = client.open('Gewinner').sheet1

            for place in publish:
                sheet.update_cell(place + 1, 2, publish[place])
        except:
            print("To many requests in a minute")
            requestPossible = False
            clock = time.time()
            publishOverdraft.update(publish)
    else:
        publishOverdraft.update(publish)
        if time.time() - clock >= 60:
            requestPossible = True
    pass


def saveResults(toBeAdded):
    """
    This method saves the analysed results to a json-file
    :param toBeAdded: results that need to be added to the json and website
    """
    publish = dict()

    if len(toBeAdded) > 0:

        if exists(f"data/results.json"):
            file = open(f"data/results.json")
            results = json.load(file)
            file.close()
        else:
            results = dict()

        for num in toBeAdded:
            results[str(currentPlace)] = num
            publish[currentPlace] = num
            currentPlace += 1

        print(f"results: {results}")

        with open(f"data/results.json", "w") as outfile:
            outfile.write(json.dumps(results))

        addToWebsite(publish)
    pass


def analyseData(currentData, frameNumber):
    """
    This Methode analyses the results from the number detection.
    There are 4 possible Problems, that can happen when the numbers on the duck are detected

    POSSIBLE PROBLEMS:
    1: No Numbers detected but Letters / Weird Numbers
    2: Singularity - Number detected in only one Frame
    3: Mirrored - Number contains only 6,9,0 or 8
    4: Numbers appear at the same time, so no order can be found

    For now we will ignore sponsored Ducks like the MHP-Duck.


    The Binomial probability of Problem 1 and 2 can be reduced greatly.
    We will categorise all detections into 4 groups:
    1. false positive: a Duck is detected that isn't really there   -> assumed to be 16,6% * 1/n
    2. true positive: a Duck is detected                            -> assumed to be 75%
    3. false negative: a Duck isn't detected that is actually there -> assumed to be 20%
    4. true negative: no duck is there no duck is detected          -> assumed to be 1 - (16,6% * 1/n)
    We will want to achieve a maximum false positive rate of fewer than 5%
    (less than 5% of none existent ducks are detected)
    The minimum true positive rate has to be at least 99%
    (99% of ducks need to be detected)
    It is better to wrongly detect a none existing duck as long as all ducks are detected. It is better for ones duck
    to move up a place than down a place.
    We will assume that the false positive probability changes, with the number of frames (n) as it is unlikely
    that a non existing random number is detected twice (in a set amount of frames). On the other hand, a duck
    with the number 002 might be detected with a higher likelihood as 200 several times.
    So this does not reflect reality, but i have found it to be a good approximation.

    Now we want to find out how many frames a duck needs to be detectable, with the above defined probability.
    Formula to identify the probability h amounts of positive detections: P(h) = n!/(h!*(n-h)!)*p^h*(1-p)^(n-h)
    p = probability of positive detection
    n = number of frames
    h = number of detections

    1 Frame to detect Duck:
        False Positive Rate:
            1FP(0) = 1!/(0!*(1-0)!)*(.166/1)^0*(1-.166/1)^1 = .834 = 83.4%
            1FP(1) = 1!/(1!*(1-1)!)*(.166/1)^1*(1-.166/1)^0 = .166 = 16.6%
        True Positive Rate:
            1TP(0) = 1!/(0!*(1-0)!)*.75^0*.25^1             = .250 = 25.0%
            1TP(1) = 1!/(1!*(1-1)!)*.75^1*.25^0             = .750 = 75.0%

    2 Frames to detect Duck:
        False Positive Rate:
            2FP(0) = 2!/(0!*(2-0)!)*(.166/2)^0*(1-.166/2)^2 = .841 = 84.1%
            2FP(1) = 2!/(1!*(2-1)!)*(.166/2)^1*(1-.166/2)^1 = .152 = 15.2%
            2FP(2) = 2!/(2!*(2-2)!)*(.166/2)^2*(1-.166/2)^0 = .007 = 00.7%
        True Positive Rate:
            2TP(0) = 2!/(0!*(2-0)!)*.75^0*.25^2             = .063 = 06.3%
            2TP(1) = 2!/(1!*(2-1)!)*.75^1*.25^1             = .375 = 37.5%
            2TP(2) = 2!/(2!*(2-2)!)*.75^2*.25^0             = .562 = 56.2%

    3 Frames to detect Duck:
        False Positive Rate:
            3FP(0) = 3!/(0!*(3-0)!)*(.166/3)^0*(1-.166/3)^3 = .843 = 84.3%
            3FP(1) = 3!/(1!*(3-1)!)*(.166/3)^1*(1-.166/3)^2 = .148 = 14.8%
            3FP(2) = 3!/(2!*(3-2)!)*(.166/3)^2*(1-.166/3)^1 = .009 = 00.9%
            3FP(3) = 3!/(3!*(3-3)!)*(.166/3)^3*(1-.166/3)^0 = .000 = 00.0%
        True Positive Rate:
            3TP(0) = 3!/(0!*(3-0)!)*.75^0*.25^3             = .016 = 01.6%
            3TP(1) = 3!/(1!*(3-1)!)*.75^1*.25^2             = .141 = 14.1%
            3TP(2) = 3!/(2!*(3-2)!)*.75^2*.25^1             = .422 = 42.2%
            3TP(3) = 3!/(3!*(3-3)!)*.75^3*.25^0             = .422 = 42.2%

    4 Frames to detect Duck:
        False Positive Rate:
            4FP(0) = 4!/(0!*(4-0)!)*(.166/4)^0*(1-.166/4)^4 = .843 = 84.3%
            4FP(1) = 4!/(1!*(4-1)!)*(.166/4)^1*(1-.166/4)^3 = .146 = 14.6%
            4FP(2) = 4!/(2!*(4-2)!)*(.166/4)^2*(1-.166/4)^2 = .009 = 00.9%
            4FP(3) = 4!/(3!*(4-3)!)*(.166/4)^3*(1-.166/4)^1 = .000 = 00.0%
            4FP(4) = 4!/(4!*(4-4)!)*(.166/4)^4*(1-.166/4)^0 = .000 = 00.0%
        True Positive Rate:
            4TP(0) = 4!/(0!*(4-0)!)*.75^0*.25^4             = .004 = 00.4%
            4TP(1) = 4!/(1!*(4-1)!)*.75^1*.25^3             = .047 = 04.7%
            4TP(2) = 4!/(2!*(4-2)!)*.75^2*.25^2             = .211 = 21.1%
            4TP(3) = 4!/(3!*(4-3)!)*.75^3*.25^1             = .422 = 42.2%
            4TP(4) = 4!/(4!*(4-4)!)*.75^4*.25^0             = .316 = 31.6%

    5 Frames to detect Duck:
        False Positive Rate:
            5FP(0) = 5!/(0!*(5-0)!)*(.166/5)^0*(1-.166/5)^5 = .845 = 84.5%
            5FP(1) = 5!/(1!*(5-1)!)*(.166/5)^1*(1-.166/5)^4 = .145 = 14.5%
            5FP(2) = 5!/(2!*(5-2)!)*(.166/5)^2*(1-.166/5)^3 = .010 = 01.0%
            5FP(3) = 5!/(3!*(5-3)!)*(.166/5)^3*(1-.166/5)^2 = .000 = 00.0%
            5FP(4) = 5!/(4!*(5-4)!)*(.166/5)^4*(1-.166/5)^1 = .000 = 00.0%
            5FP(5) = 5!/(5!*(5-5)!)*(.166/5)^5*(1-.166/5)^0 = .000 = 00.0%
        True Positive Rate:
            5TP(0) = 5!/(0!*(5-0)!)*.75^0*.25^5             = .001 = 00.1%
            5TP(1) = 5!/(1!*(5-1)!)*.75^1*.25^4             = .015 = 01.5%
            5TP(2) = 5!/(2!*(5-2)!)*.75^2*.25^3             = .088 = 08.8%
            5TP(3) = 5!/(3!*(5-3)!)*.75^3*.25^2             = .263 = 26.3%
            5TP(4) = 5!/(4!*(5-4)!)*.75^4*.25^1             = .396 = 39.6%
            5TP(5) = 5!/(5!*(5-5)!)*.75^5*.25^0             = .237 = 23.7%

    6 Frames to detect Duck:
        False Positive Rate:
            6FP(0) = 6!/(0!*(6-0)!)*(.166/6)^0*(1-.166/6)^6 = 0.845 = 84.5%
            6FP(1) = 6!/(1!*(6-1)!)*(.166/6)^1*(1-.166/6)^5 = 0.144 = 14.4%
            6FP(2) = 6!/(2!*(6-2)!)*(.166/6)^2*(1-.166/6)^4 = 0.010 = 01.0%
            6FP(3) = 6!/(3!*(6-3)!)*(.166/6)^3*(1-.166/6)^3 = 0.000 = 00.0%
            6FP(4) = 6!/(4!*(6-4)!)*(.166/6)^4*(1-.166/6)^2 = 0.000 = 00.0%
            6FP(5) = 6!/(5!*(6-5)!)*(.166/6)^5*(1-.166/6)^1 = 0.000 = 00.0%
            6FP(6) = 6!/(6!*(6-6)!)*(.166/6)^6*(1-.166/6)^0 = 0.000 = 00.0%
        True Positive Rate:
            6TP(0) = 6!/(0!*(6-0)!)*.75^0*.25^6             = .000 = 00.0%
            6TP(1) = 6!/(1!*(6-1)!)*.75^1*.25^5             = .004 = 00.4%
            6TP(2) = 6!/(2!*(6-2)!)*.75^2*.25^4             = .032 = 03.2%
            6TP(3) = 6!/(3!*(6-3)!)*.75^3*.25^3             = .132 = 13.2%
            6TP(4) = 6!/(4!*(6-4)!)*.75^4*.25^2             = .296 = 29.6%
            6TP(5) = 6!/(5!*(6-5)!)*.75^5*.25^1             = .356 = 35.6%
            6TP(6) = 6!/(6!*(6-6)!)*.75^6*.25^0             = .178 = 17.8%

    To achieve our self set quotas we will use 6 frames and expect at least 2 positive detections.
    This will set our...
    ... false positive rate to: 6FP(6)+6FP(5)+6FP(4)+6FP(3) = 1%
    ... true positive rate to:  6TP(6)+6TP(5)+6TP(4)+6TP(3) = 99.4%

    It thus needs to be assured that the duck can be processed in 6 different frames.
    For this purpose the main.main.ProcessedFPS per minute can be adapted. The speed of the ducks travelling through
    the finish line can also be adapted.

    It would be very interesting to collect more Data, to affirm the above made assumptions.


    Problem 3 has to be solved with User interaction, the Google API simply can't tell the difference.
    Luckily there are only 12 Numbers from 0 to 750 than can be mirrored (and produce a different number)
    Though if two mirrable numbers enter at a similar time only one will be detected

    Problem 4s probability can be reduced with more main.main.ProcessedFPS
    This though has an upper limit.
    No sophisticated solution to this problem was implemented!

    :param currentData: The Data which is analysed at the moment
    :param frameNumber: The Frame that is being analysed
    """
    updateLast20()
    updateLast6()

    global last6
    global last20
    global currentPlace
    global detectedDucks

    newNums = list()
    currentNums = list()
    toBeAdded = list()

    minPositive = 2
    numbers = 0

    print(f"Analysing Frame{frameNumber}")

    for cd in currentData:

        # is cd number?
        try:
            num = int(cd)
            numbers += 1
        except:
            continue

        # is cd number within 0 to 750
        if num < 10:
            if cd[:1] != '0':
                numbers -= 1
                continue
        if num < 100:
            if cd[1:2] != '0':
                numbers -= 1
                continue
        if num > 750 or num < 1:
            numbers -= 1
            continue
        if len(cd) > 3 or len(cd) < 3:
            numbers -= 1
            continue

        # is cd Mirrored?
        mirrorableNumbs = ['6', '9', '0', '8']
        if cd[0:1] in mirrorableNumbs and cd[1:2] in mirrorableNumbs and cd[2:3] in mirrorableNumbs:

            possibleTo750 = [9, 69, 89, 90, 99, 600, 690, 680, 60, 660, 669, 699]
            if num in possibleTo750:

                mirroredNum = mirrorNum(num)

                l6 = num not in last6 and mirroredNum not in last6 and mirroredNum != num
                l20 = num not in last20 and mirroredNum not in last20 and mirroredNum != num
                # last 20 ensures that if the duk lingers on the finish line that the user isn't asked twice
                # One could consider to shorten this, if ducks have been shown not to linger

                if l6 or l20:
                    num = problem3(num, mirroredNum,
                                   frameNumber)
                elif num not in last20 and num not in last6:
                    num = mirroredNum

        # is cd new?
        if num not in detectedDucks:
            newNums.append(num)

        currentNums.append(num)

    if last6 is not None:
        for num in newNums:

            if num in last6:
                last6[num]["age"] = 0
                last6[num]["count"] += 1
                if last6[num]["count"] >= minPositive:
                    last20[num] = 0
                    toBeAdded.append(num)
                    detectedDucks.add(num)
            else:
                last6[num] = {"age": 0, "count": 1}

    saveResults(toBeAdded)
    pass


def manage_results(answer):
    """
    This method is started at the beginning of the Software to analyse the numbers that are detected by the
    Google image processing
    """

    global currentPlace
    global detectedDucks
    number = 1

    for root, dirs, files in os.walk("data/framejsons/"):
        for file in files:
            os.remove(os.path.join(root, file))

        if answer.lower()[:1] == 'y':
            os.remove(f"data/results.json")
        else:
            file = open(f"data/results.json")
            results = json.load(file)
            for cp in results:
                cpNum = int(cp)
                if cpNum > currentPlace:
                    currentPlace = cpNum
                detectedDucks.add(results[cp])

    while True:
        while not exists(f"data/framejsons/frame{number}.json"):
            pass

        time.sleep(1)

        f = open(f"data/framejsons/frame{number}.json")
        currentData = json.load(f)
        f.close()

        print(f"Current Data: {currentData}")
        analyseData(currentData, number)

        number += 1
    pass
