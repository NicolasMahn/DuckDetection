"""
:author NicolasMahn
"""


def mirrorNum(normalNum):
    """
    mirrors numbers
    :param normalNum: 'unmirrored' number
    :return: mirrored number
    """

    cd = f'{normalNum:03d}'

    if cd[0:1] == '6':
        last = 9
    elif cd[0:1] == '9':
        last = 6
    else:
        last = cd[0:1]

    if cd[1:2] == '6':
        second = 9
    elif cd[1:2] == '9':
        second = 6
    else:
        second = cd[1:2]

    if cd[2:3] == '6':
        first = 9
    elif cd[2:3] == '9':
        first = 6
    else:
        first = cd[2:3]

    return int(f"{first}{second}{last}")