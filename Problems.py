"""
:author NicolasMahn
"""


def problem3(num, mirroredNum, frameNum):
    """
    This method deals with problem 3 of the json processing.
    It asks the user if the number was detected mirrored
    :param num: number
    :param mirroredNum: mirrored number
    :param frameNum: number of the frame where this was detected
    :return: the correct number
    """
    filename = f"frame{frameNum}.jpg"

    print(filename)

    while True:
        returnData = input(f"What Number do you see {num} or {mirroredNum}?")
        try:
            returnNum = int(returnData)
            break
        except:
            print("Oh this was not a valid number, please try again")

    return returnNum
