import cv2
import numpy as np
import spidev
import copy
import random


""" joystick setting"""
sw_channel = 0
px_channel = 1
py_channel = 2
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000

""" display setting """
start_img = np.ones((550, 500, 3), dtype=np.uint8) * 255
start_img = cv2.rectangle(start_img, (100, 50), (400, 150), (0, 0, 0), 3)  # game name
start_img = cv2.rectangle(start_img, (50, 250), (450, 350), (0, 0, 0), 3)  # start
start_img = cv2.rectangle(start_img, (50, 400), (450, 500), (0, 0, 0), 3)  # ranking
start_img = cv2.putText(start_img, "2048 game", (110, 120), 1, 3, (0, 0, 0), 3)
start_img = cv2.putText(start_img, "Start", (175, 320), 1, 3, (0, 0, 0), 4)
start_img = cv2.putText(start_img, "Rank", (180, 470), 1, 3, (0, 0, 0), 4)

rank_img = np.ones((550, 500, 3), dtype=np.uint8) * 255
rank_img = cv2.rectangle(rank_img, (100, 460), (200, 520), (0, 0, 0), 3)  # back
rank_img = cv2.rectangle(rank_img, (280, 460), (380, 520), (0, 0, 0), 3)  # reset
rank_img = cv2.putText(rank_img, "back", (110, 505), 1, 2, (0, 0, 0), 4)
rank_img = cv2.putText(rank_img, "reset", (285, 505), 1, 2, (0, 0, 0), 4)

play_img = cv2.imread("/home/pi/Webapps/project/data/stage.png")  # stage
result_img = copy.deepcopy(start_img)  # print display image

""" program value """
global menu
menu = 0  # menu select index
# start_img:  1: start , 2: rank
display = 0  # 0: start, 1: play , 2: ranking
global rank_dic  # rank data Dictionary
username = ""  # play username
score = 0  # play score

""" input joystick adc """


def readac(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, (8 + adcnum) << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data


"""  input joystick switch """


def joy_sw():
    sw = readac(sw_channel)
    if sw < 100:
        return True
    else:
        return False


"""  input joystick (up, down, left, right) """


def joy_way():
    px = readac(px_channel)
    py = readac(py_channel)
    if py < 10 and px < 700 and px > 300:  # up
        return 0
    elif py > 900 and px < 700 and px > 300:  # down
        return 1
    elif py < 700 and py > 300 and px > 900:  # left
        return 2
    elif px < 10 and py < 700 and py > 300:  # right
        return 3
    else:
        return 4


""" raed rank data file """


def read_rank():
    rank_f = open("/home/pi/Webapps/project/data/ranking.txt", "r")
    rank_dic = {}
    i = 0
    while True:
        line = rank_f.readline()
        if not line:
            rank_f.close()
            return rank_dic
        chars = line.split(" ")
        ia = int(chars[1])
        rank_dic[chars[0]] = ia


""" reset rank data file """


def reset_rank(img):
    rank_f = open("/home/pi/Webapps/project/data/ranking.txt", "w")
    rank_f.write("")
    rank_dic = {}
    img = np.ones((550, 500, 3), dtype=np.uint8) * 255
    img = cv2.rectangle(rank_img, (100, 460), (200, 520), (0, 0, 0), 3)  # back
    img = cv2.rectangle(rank_img, (280, 460), (380, 520), (0, 0, 0), 3)  # reset
    img = cv2.putText(rank_img, "back", (110, 505), 1, 2, (0, 0, 0), 4)
    img = cv2.putText(rank_img, "reset", (285, 505), 1, 2, (0, 0, 0), 4)
    return rank_dic, img


""" rank menu show """


def rank_show(rank_img, rank_dic, display):
    global menu
    result_img = copy.deepcopy(rank_img)
    rank_dic = read_rank()
    if rank_dic != 0:
        menu = 0
        rank_dic_reverse = {v: k for k, v in rank_dic.items()}
        rank_list = []
        for i in rank_dic.values():
            rank_list.append(i)

        rank_list.sort(reverse=True)
        cnt = 0
        position_y = 30
        for i in rank_list:
            cnt += 1
            position_y += 30
            if cnt == 1:
                result_img = cv2.putText(
                    result_img,
                    "No." + str(cnt) + " " + rank_dic_reverse.get(i) + " : " + str(i),
                    (10, 50),
                    1,
                    2,
                    (0, 0, 255),
                    3,
                )
            elif cnt == 2:
                esult_img = cv2.putText(
                    result_img,
                    "No." + str(cnt) + " " + rank_dic_reverse.get(i) + " : " + str(i),
                    (10, 80),
                    1,
                    1.5,
                    (0, 255, 0),
                    2,
                )
            elif cnt == 3:
                esult_img = cv2.putText(
                    result_img,
                    "No." + str(cnt) + " " + rank_dic_reverse.get(i) + " : " + str(i),
                    (10, 110),
                    1,
                    1.5,
                    (255, 0, 0),
                    2,
                )
            else:
                esult_img = cv2.putText(
                    result_img,
                    "No." + str(cnt) + " " + rank_dic_reverse.get(i) + " : " + str(i),
                    (10, position_y),
                    1,
                    1,
                    (0, 0, 0),
                    2,
                )
    while 1:
        display = 2
        cv2.imshow("2048 game", result_img)
        cv2.waitKey(1)
        if cv2.waitKey(1) == 27:
            break
        result_img = select_menu(result_img, display)

        if joy_sw():
            if menu == 1:  # back
                display = 0
                break
            elif menu == 2:  # reset
                rank_dic, result_img = reset_rank(result_img)
                display = 2
    return 0, 0


""" select menu show """


def select_menu(result_img, display):
    global menu
    way = joy_way()
    if way == 0 and display == 0:
        result_img = cv2.rectangle(
            result_img, (50, 250), (450, 350), (255, 0, 0), 3
        )  # start
        result_img = cv2.rectangle(
            result_img, (50, 400), (450, 500), (0, 0, 0), 3
        )  # ranking
        menu = 1
    elif way == 1 and display == 0:
        result_img = cv2.rectangle(
            result_img, (50, 250), (450, 350), (0, 0, 0), 3
        )  # start
        result_img = cv2.rectangle(
            result_img, (50, 400), (450, 500), (255, 0, 0), 3
        )  # ranking
        menu = 2
    elif way == 2 and display == 2:
        result_img = cv2.rectangle(
            result_img, (100, 460), (200, 520), (255, 0, 0), 3
        )  # back
        result_img = cv2.rectangle(
            result_img, (280, 460), (380, 520), (0, 0, 0), 3
        )  # reset
        menu = 1
    elif way == 3 and display == 2:
        result_img = cv2.rectangle(
            result_img, (100, 460), (200, 520), (0, 0, 0), 3
        )  # back
        result_img = cv2.rectangle(
            result_img, (280, 460), (380, 520), (255, 0, 0), 3
        )  # reset
        menu = 2

    return result_img


"""  input username """


def input_user():
    img = cv2.imread("/home/pi/Webapps/project/data/username2.png")
    username = ""
    while 1:
        cv2.imshow("2048 game", img)
        key = cv2.waitKey(0)
        if key == 13:
            break
        elif key == 8:
            username = username[:-1]
            img = cv2.imread("/home/pi/Webapps/project/data/username2.png")
            img = cv2.putText(img, username, (120, 160), 1, 3, (0, 0, 0), 4)
            continue
        username += chr(key)
        if len(username) > 8:
            username = username[:-1]
        img = cv2.putText(img, username, (120, 160), 1, 3, (0, 0, 0), 4)
    return username


""" block show display """


def block_show(temp_img, block_array):
    sum = 0
    result = copy.deepcopy(temp_img)
    x = 10
    y = 120
    cnt = 0
    for list in block_array:
        for i in list:
            sum += i
            cnt += 1
            if i != 0:
                if i == 2:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (0, 0, 0), 2)
                elif i == 4:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (0, 0, 255), 2)
                elif i == 8:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (0, 50, 255), 2)
                elif i == 16:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (0, 255, 255), 2)
                elif i == 32:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (0, 255, 0), 2)
                elif i == 64:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (255, 0, 0), 2)
                elif i == 128:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (255, 0, 100), 2)
                elif i == 256:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (200, 0, 255), 2)
                elif i == 512:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (0, 76, 153), 2)
                elif i == 1024:
                    result = cv2.putText(
                        result, str(i), (x, y), 1, 2, (100, 255, 255), 2
                    )
                elif i == 2048:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (0, 50, 50), 2)
                else:
                    result = cv2.putText(result, str(i), (x, y), 1, 2, (153, 0, 0), 2)
            x += 100

        x = 10
        y += 100

    result = cv2.putText(result, str(sum), (230, 30), 1, 1.5, (0, 0, 0), 2)

    return result


""" block move """


def block_move(way, block_array):
    for i in range(0, 5):
        x = 0
        y = 0
        if way == 0:
            for list in block_array:
                for i in list:
                    if i != 0 and y != 0:
                        if block_array[y - 1][x] == 0:
                            block_array[y - 1][x] = i
                            block_array[y][x] = 0
                        elif (
                            block_array[y - 1][x] == block_array[y][x]
                            and block_array[y][x] > 0
                        ):
                            block_array[y - 1][x] += i
                            block_array[y - 1][x] = -block_array[y - 1][x]
                            block_array[y][x] = 0
                    x += 1
                x = 0
                y += 1
        elif way == 1:
            for list in reversed(block_array):
                for i in reversed(list):
                    if i != 0 and y != 0:
                        if block_array[4 - y + 1][4 - x] == 0:
                            block_array[4 - y + 1][4 - x] = i
                            block_array[4 - y][4 - x] = 0
                        elif (
                            block_array[4 - y + 1][4 - x] == block_array[4 - y][4 - x]
                            and block_array[4 - y][4 - x] > 0
                        ):
                            block_array[4 - y + 1][4 - x] += i
                            block_array[4 - y + 1][4 - x] = -block_array[4 - y + 1][
                                4 - x
                            ]
                            block_array[4 - y][4 - x] = 0
                    x += 1
                x = 0
                y += 1
        elif way == 2:
            for list in block_array:
                for i in list:
                    if i != 0 and x != 0:
                        if block_array[y][x - 1] == 0:
                            block_array[y][x - 1] = i
                            block_array[y][x] = 0
                        elif (
                            block_array[y][x - 1] == block_array[y][x]
                            and block_array[y][x] > 0
                        ):
                            block_array[y][x - 1] += i
                            block_array[y][x - 1] = -block_array[y][x - 1]
                            block_array[y][x] = 0
                    x += 1
                x = 0
                y += 1
        elif way == 3:
            for list in reversed(block_array):
                for i in reversed(list):
                    if i != 0 and x != 0:
                        if block_array[4 - y][4 - x + 1] == 0:
                            block_array[4 - y][4 - x + 1] = i
                            block_array[4 - y][4 - x] = 0
                        elif (
                            block_array[4 - y][4 - x + 1] == block_array[4 - y][4 - x]
                            and block_array[4 - y][4 - x] > 0
                        ):
                            block_array[4 - y][4 - x + 1] += i
                            block_array[4 - y][4 - x + 1] = -block_array[4 - y][
                                4 - x + 1
                            ]
                            block_array[4 - y][4 - x] = 0
                    x += 1
                x = 0
                y += 1

    x = 0
    y = 0
    for list in block_array:
        for i in list:
            block_array[y][x] = abs(block_array[y][x])
            x += 1
        x = 0
        y += 1
    return block_array


""" random block appear """


def rand_block(block_array):
    sum = 0
    for list in block_array:
        for i in list:
            sum += i
    num = 4
    num = sum / 200
    while 1:
        x = random.randrange(0, 5)
        y = random.randrange(0, 5)
        if block_array[y][x] != 0:
            continue
        else:
            if num <= 0:
                block_array[y][x] = 2
                break
            elif num <= 1:
                block_array[y][x] = random.choice([2, 4])
                break
            elif num <= 3:
                block_array[y][x] = random.choice([2, 4, 8])
                break
            elif num > 3:
                block_array[y][x] = random.choice([2, 4, 8, 16])
                break
    return block_array


""" save rank file """


def save_game(block_array, username):
    global rank_dic
    sum = 0
    for list in block_array:
        for i in list:
            sum += i
    rank_f = open("/home/pi/Webapps/project/data/ranking.txt", "a")
    rank_f.write(username + " " + str(sum) + "\n")

    rank_dic[username] = sum


""" check gameover """


def gamecheck(block_array):
    flag = False
    for list in block_array:
        for i in list:
            if i == 0:
                return False

    flag = True
    for i in range(0, 5):
        for j in range(0, 5):
            if (
                j < 4
                and i < 4
                and (
                    block_array[i][j] == block_array[i + 1][j]
                    or block_array[i][j] == block_array[i][j + 1]
                )
            ):
                flag = False
            elif i == 4:
                if j < 4 and block_array[i][j] == block_array[i][j + 1]:
                    flag = False
            elif j == 4:
                if i < 4 and block_array[i][j] == block_array[i + 1][j]:
                    flag = False
    return flag


""" gameover """


def gameover(block_array, username):
    save_game(block_array, username)
    sum = 0
    for list in block_array:
        for i in list:
            sum += i
    img = cv2.imread("/home/pi/Webapps/project/data/gameover.png")
    img = cv2.putText(
        img,
        str(sum),
        (200, 340),
        1,
        3,
        (0, 255, 255),
        3,
    )

    while 1:
        cv2.imshow("2048 game", img)
        cv2.waitKey(1)
        if joy_way() == 0:
            break


""" playgame """


def playgame(play_img, username, rank_dic):
    result_img = copy.deepcopy(play_img)
    list = []
    if len(rank_dic) != 0:
        for i in rank_dic.values():
            list.append(i)

        bestscore = max(list)
        result_img = cv2.putText(
            result_img, "best: " + str(bestscore), (360, 30), 1, 1.5, (0, 0, 0), 2
        )
    result_img = cv2.putText(result_img, username, (10, 30), 1, 1.5, (0, 0, 0), 2)
    temp_img = copy.deepcopy(result_img)
    block_array = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [2, 0, 0, 0, 0],
        [2, 0, 0, 0, 0],
    ]
    flag = False
    way = 4
    while 1:
        result_img = block_show(temp_img, block_array)  # block and score show
        cv2.imshow("2048 game", result_img)
        if cv2.waitKey(1) == 27:
            save_game(block_array, username)
            break

        if flag:
            way = joy_way()  # 0123 : up down left right
            if way != 4:
                temp = copy.deepcopy(block_array)
                block_array = block_move(way, block_array)
                if temp != block_array:
                    block_array = rand_block(block_array)
                if gamecheck(block_array):
                    gameover(block_array, username)
                    break
                flag = False
            else:
                flag = True

        if joy_way() == 4:
            flag = True


rank_dic = read_rank()  # rank data reading

while 1:
    display = 0
    cv2.imshow("2048 game", result_img)
    if cv2.waitKey(1) == 27:
        break

    result_img = select_menu(result_img, display)

    if joy_sw():
        if menu == 1:
            display = 1
            rank_dic = read_rank()
            username = input_user()
            playgame(play_img, username, rank_dic)
            result_img = copy.deepcopy(start_img)
        elif menu == 2:
            display = 2
            menu, display = rank_show(rank_img, rank_dic, display)
            result_img = copy.deepcopy(start_img)
