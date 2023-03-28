import datetime
import numpy as np
import compiler
import matplotlib.pyplot as plt
import cv2
import time
from PIL import Image
import math

colors = [
    ['#FFC0C0', '#FFFFC0', '#C0FFC0', '#C0FFFF', '#C0C0FF', '#FFC0FF'],
    ['#FF0000', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF', '#FF00FF'],
    ['#C00000', '#C0C000', '#00C000', '#00C0C0', '#0000C0', '#C000C0'],
    ['#FFFFFF', '#000000']
]

code_to_hex = {
    'PUSH': {'hue': 0, 'dark': 1},
    'POP': {'hue': 0, 'dark': 2},

    'ADD': {'hue': 1, 'dark': 0},
    'SUB': {'hue': 1, 'dark': 1},
    'MUL': {'hue': 1, 'dark': 2},

    'DIV': {'hue': 2, 'dark': 0},
    'MOD': {'hue': 2, 'dark': 1},
    'NOT': {'hue': 2, 'dark': 2},

    'GREATER': {'hue': 3, 'dark': 0},
    'POINTER': {'hue': 3, 'dark': 1},
    'SWITCH': {'hue': 3, 'dark': 2},

    'DUP': {'hue': 4, 'dark': 0},
    'ROLL': {'hue': 4, 'dark': 1},
    'IN_NUM': {'hue': 4, 'dark': 2},

    'IN_CHAR': {'hue': 5, 'dark': 0},
    'OUT_NUM': {'hue': 5, 'dark': 1},
    'OUT_CHAR': {'hue': 5, 'dark': 2},
}

image = []


def get_hue_and_dark(op, last_op=None, hue_index=0, dark_index=0):
    """
    If the last operation was a `PUSH` or the last operation was not the same as the current
    operation, then add the hue and dark values from the `code_to_hex` dictionary to the hue and dark
    indexes, and if either index is greater than 5 or 2, respectively, then set it to 0

    :param op: the current opcode
    :param last_op: The last opcode that was executed
    :param hue_index: 0-5, defaults to 0 (optional)
    :param dark_index: 0 = light, 1 = medium, 2 = dark, defaults to 0 (optional)
    :return: the hue_index and dark_index.
    """
    if last_op == 'PUSH' or last_op != op:
        change = code_to_hex[op]
        hue_index += change['hue']
        if hue_index > 5:
            hue_index -= 6
        dark_index += change['dark']
        if dark_index > 2:
            dark_index -= 3
    last_op = op
    return hue_index, dark_index


def my_hue_and_dark(op, hue_index=0, dark_index=0):
    hue_index = hue_index + code_to_hex[op]['hue']
    dark_index = dark_index + code_to_hex[op]['dark']

    if hue_index > 5:
        hue_index = hue_index - 6

    if dark_index > 2:
        dark_index = dark_index - 3

    return hue_index, dark_index


def getHexOrWhite(hexTab, hexInd):
    """
    Get the hex value at the given index in the hex table, or return white if the index is out of bounds

    :param hexTab: The hex table
    :param hexInd: The index of the hex value
    :return: The hex value at the given index, or white
    """
    if hexInd < len(hexTab):
        return hexTab[hexInd]
    else:
        return '#FFFFFF'


def construct_image_snake(hex_tab: list):
    width = math.ceil((math.sqrt(len(hex_tab)*2)))
    print(f"width: {width}")

    hex_ind = 0
    full = True
    left = False
    right = True

    img = []

    for i in range(0, width):
        row = []
        if full:
            for j in range(0, width):
                hex = getHexOrWhite(hex_tab, hex_ind)
                hex_ind += 1

                # convert hex value to rbg and add it to the color array
                # remove # from hex
                hex = hex[1:]
                r, g, b = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
                row.append([b, g, r])

            full = False

            if right == False:
                # reverse the row
                row.reverse()

        elif left:
            hex = getHexOrWhite(hex_tab, hex_ind)
            hex_ind += 1
            # convert hex value to rgb and add it to the color table
            hex = hex[1:]
            r, g, b = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
            row.append([b, g, r])

            for j in range(0, width-1):
                row.append([0, 0, 0])
            full = True
            left = False
            right = True
        elif right:
            for j in range(0, width-1):
                row.append([0, 0, 0])
            hex = getHexOrWhite(hex_tab, hex_ind)
            hex_ind += 1
            # convert hex value to rgb and add it to the color table
            # convert hex value to rgb and add it to the color table
            hex = hex[1:]
            r, g, b = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
            row.append([b, g, r])

            full = True
            left = True
            right = False

        img.append(row)

    img = np.array(img, dtype=np.uint8)
    cv2.imshow("Genrated PIET", img)
    cv2.waitKey()
    # Save the image to the current directory with the current date and time as the name
    cv2.imwrite(
        f'piet_{datetime.datetime.now().strftime("%d%m%y_%H%M%S")}.png', img)


def construct_image_spiral(hex_tab: list) -> None:
    '''
    Construct the piet image from the hex table

    :param hex_tab: The hex table
    :return: None
    '''
    width = (math.sqrt(len(hex_tab)*2))

    # if width - int(width) > 0.5 -> ceil, else floor
    if width - int(width) > 0.5:
        width = math.ceil(width)
    else:
        width = math.floor(width)

    img = np.zeros((width, width, 3), np.uint8)
    img.fill(255)

    coords = (0, 0)

    hex_ind = 0

    visited = []
    isFirst = True

    startX = 0
    startXBlack = 0

    startY = 0
    endX = width-1
    endY = width-1
    x = startX
    y = startY

    # for i in range(0, 4):
    while [x, y] not in visited:

        # color : left to right
        for j in range(startX, endX+1):
            x = j
            visited.append([x, y])

            hex = getHexOrWhite(hex_tab, hex_ind)
            hex = hex[1:]
            hex_ind += 1
            r, g, b = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
            img[y][x] = [b, g, r]

        # black : left to right
        y = startY+1
        for j in range(startXBlack, endX):
            x = j
            visited.append([x, y])
            img[y][x] = [0, 0, 0]

        # color : top right to bottom right
        x = endX
        for j in range(startY+1, endY+1):
            y = j
            visited.append([x, y])
            hex = getHexOrWhite(hex_tab, hex_ind)
            hex = hex[1:]
            hex_ind += 1
            r, g, b = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
            img[y][x] = [b, g, r]

        x = endX-1
        # black : top right to bottom right
        for j in range(startY+2, endY):
            y = j
            visited.append([x, y])
            img[y][x] = [0, 0, 0]

        # color : right to left
        y = endY
        for j in range(endX-1, startXBlack-1, -1):
            x = j
            visited.append([x, y])
            hex = getHexOrWhite(hex_tab, hex_ind)
            hex = hex[1:]
            hex_ind += 1
            r, g, b = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
            img[y][x] = [b, g, r]

        # black : right to left
        y = endY-1
        for j in range(endX-2, startXBlack, -1):
            x = j
            visited.append([x, y])
            img[y][x] = [0, 0, 0]

        # color : bottom left to top left
        x = startXBlack
        for j in range(endY-1, startY+1, -1):
            y = j
            visited.append([x, y])
            hex = getHexOrWhite(hex_tab, hex_ind)
            hex = hex[1:]
            hex_ind += 1
            r, g, b = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
            img[y][x] = [b, g, r]

        # black : bottom left to top left
        x = startXBlack+1
        for j in range(endY-2, startY+2, -1):
            y = j
            visited.append([x, y])
            img[y][x] = [0, 0, 0]

        if isFirst:
            startX = startX + 1
            isFirst = False
        else:
            startX = startX + 2

        startXBlack = startXBlack + 2
        startY = startY + 2
        endX = endX - 2
        endY = endY - 2

        x = startX
        y = startY

    # img = np.dstack([np.array(b, dtype=np.uint8), np.array(
    #   g, dtype=np.uint8), np.array(r, dtype=np.uint8)])  # Stack the channels together as a 3D numpy array for OpenCV

    # img = np.array(img, dtype=np.uint8)

    cv2.imshow("Generated PIET", img)  # Show the image
    cv2.waitKey()  # Wait for a key press
    cv2.imwrite(
        f'piet_{datetime.datetime.now().strftime("%d%m%y_%H%M%S")}.png', img)  # Save the image to the current directory with the current date and time as the name


def make_image(compiled: str) -> list:
    hue_index = 0
    dark_index = 0
    compiled = compiled.split("\n")
    previous = None
    for inst in compiled:
        inst = inst.split(" ")

        match inst[0]:
            case "PUSH":
                # push a value onto the stack
                value = int(inst[1])
                value = value * -1 if previous == "USUB" else value

                if value > 0:
                    instructions = []

                    while value > 1:
                        if value % 2 == 0:
                            value = value / 2
                            instructions.append("ADD")
                            instructions.append("DUP")
                        elif value % 2 == 1:
                            value = (value - 1)
                            instructions.append("ADD")
                            instructions.append("PUSH")

                    instructions.append("PUSH")
                    instructions.reverse()

                    if len(image) < 1:
                        image.append(colors[dark_index][hue_index])

                    for inst in instructions:
                        match inst:
                            case "PUSH":
                                (hue_index, dark_index) = my_hue_and_dark(
                                    "PUSH", hue_index, dark_index)
                            case "DUP":
                                (hue_index, dark_index) = my_hue_and_dark(
                                    "DUP", hue_index, dark_index)
                                pass
                            case "ADD":
                                (hue_index, dark_index) = my_hue_and_dark(
                                    "ADD", hue_index, dark_index)
                                pass
                        image.append(colors[dark_index][hue_index])

                elif value < 0:

                    posVal = -value

                    instructions = []

                    while posVal > 1:
                        if posVal % 2 == 0:
                            posVal = posVal / 2
                            instructions.append("ADD")
                            instructions.append("DUP")
                        elif posVal % 2 == 1:
                            posVal = (posVal - 1)
                            instructions.append("ADD")
                            instructions.append("PUSH")

                    instructions.append("PUSH")
                    instructions.reverse()

                    if len(image) < 1:
                        image.append(colors[dark_index][hue_index])

                    instructions.append("DUP")
                    instructions.append("DUP")
                    instructions.append("ADD")
                    instructions.append("SUB")

                    for inst in instructions:
                        match inst:
                            case "PUSH":
                                (hue_index, dark_index) = my_hue_and_dark(
                                    "PUSH", hue_index, dark_index)
                            case "DUP":
                                (hue_index, dark_index) = my_hue_and_dark(
                                    "DUP", hue_index, dark_index)
                                pass
                            case "ADD":
                                (hue_index, dark_index) = my_hue_and_dark(
                                    "ADD", hue_index, dark_index)
                                pass
                            case "SUB":
                                (hue_index, dark_index) = my_hue_and_dark(
                                    "SUB", hue_index, dark_index)
                        image.append(colors[dark_index][hue_index])

                elif value == 0:
                    if len(image) < 1:
                        image.append(colors[dark_index][hue_index])

                    (hue_index, dark_index) = my_hue_and_dark(
                        'PUSH', hue_index, dark_index)

                    image.append(colors[dark_index][hue_index])

                    (hue_index, dark_index) = my_hue_and_dark(
                        'DUP', hue_index, dark_index)

                    image.append(colors[dark_index][hue_index])

                    (hue_index, dark_index) = my_hue_and_dark(
                        'SUB', hue_index, dark_index)

                    image.append(colors[dark_index][hue_index])

            case ("ADD" | "SUB" | "MUL" | "DIV" | "DUP" | "POP" | "MOD"):
                (hue_index, dark_index) = get_hue_and_dark(
                    inst[0], previous, hue_index, dark_index)

                image.append(colors[dark_index][hue_index])

            case "PRINT":
                hue_index, dark_index = my_hue_and_dark(
                    'OUT_NUM', hue_index, dark_index)

                image.append(colors[dark_index][hue_index])

            case "PRINTC":
                hue_index, dark_index = my_hue_and_dark(
                    'OUT_CHAR', hue_index, dark_index)

                image.append(colors[dark_index][hue_index])
            case "USUB":
                previous = "USUB"

    return image


if __name__ == "__main__":
    from parser_1 import parse
    import sys

    print("Piet Interpreter")
    prog = open(sys.argv[1]).read()
    mode = sys.argv[2]
    if mode not in ["spiral", "snake"]:
        mode = "spiral"
    # prog = open("3-2-nombres-negatifs.txt").read()
    ast = parse(prog)
    # print(f"ast: {ast}")
    compiled = ast.compile()
    # print(f"type of compiled: {type(compiled)}")
    image = make_image(compiled)

    if mode == "spiral":
        construct_image_spiral(image)
    elif mode == "snake":
        construct_image_snake(image)
