import logging
import time
import numpy as np
import pyautogui
import winsound
from PIL import ImageGrab
from PIL import Image
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
import keyboard
import win32con
import win32gui as w32
import pydirectinput as pdi


def crop_diagonal_rectangle(image_array, top_left, bottom_right):
    cropped_array = image_array[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    return cropped_array


def image_processor(image):
    threshold = 210  # 阈值，大于等于该值的色块将变成白色，否则变成黑色
    target_color = (241, 162, 60)  # 目标颜色1
    white_color = (255, 255, 255)
    black_color = (0, 0, 0)
    processed_img = np.copy(image)

    for y in range(processed_img.shape[0]):
        for x in range(processed_img.shape[1]):
            pixel_color = processed_img[y, x]

            # 判断是否接近目标颜色
            close_to_target = all(abs(pixel_color[i] - target_color[i]) <= 40 for i in range(3))

            if close_to_target or np.all(pixel_color >= threshold):
                processed_img[y, x] = white_color
            else:
                processed_img[y, x] = black_color

    return processed_img


def recognize_text(image):
    # 创建PaddleOCR实例
    ocr_instance = PaddleOCR(use_angle_cls=True, lang="ch")

    # 从原始图像中提取感兴趣区域的部分
    roi = crop_diagonal_rectangle(image, (1530, 275), (1890, 470))

    # 使用图片处理器处理传入的图像
    roi_processor = image_processor(roi)

    # 调用PaddleOCR的识别方法并获取结果列表
    result_list = ocr_instance.ocr(roi_processor)[0]

    # 从识别结果中提取文本并存储在文本列表中
    text_list = []
    for res in result_list:
        text_list.append(res[1][0])

    return text_list, roi_processor


def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1], distances[index1 + 1], new_distances[-1])))
        distances = new_distances

    return distances[-1]


def compare_to_existing_strings(input_string):
    existing_strings = [
        "生命值",
        "防御力",
        "攻击力",
        "暴击率",
        "暴击伤害",
        "效果命中",
        "效果抵抗",
        "击破特攻",
        "速度",
        "量子属性伤害提高",
        "虚数属性伤害提高",
        "火属性伤害提高",
        "冰属性伤害提高",
        "风属性伤害提高",
        "雷属性伤害提高",
        "物理属性伤害提高",
        "能量恢复效率"
    ]

    input_string = input_string.strip()

    if not input_string:
        return ""

    best_match = None
    min_distance = float('inf')

    for existing_string in existing_strings:
        distance = levenshtein_distance(input_string, existing_string)
        if distance < min_distance:
            min_distance = distance
            best_match = existing_string

    return best_match


if __name__ == '__main__':

    startTrain = w32.FindWindow('UnityWndClass', u'崩坏：星穹铁道')
    if startTrain != 0:
        w32.ShowWindow(startTrain, win32con.SW_NORMAL)
        w32.SetForegroundWindow(startTrain)
        time.sleep(1)
    else:
        print("Window not found.")
        exit(0)

    pyautogui.click(1353, 210)
    time.sleep(0.5)

    for _ in range(3):
        roi = crop_diagonal_rectangle(np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080))), (124, 193), (1243, 928))

        for _ in range(5):
            pyautogui.moveTo(1290, 550)
            pyautogui.scroll(-1)

        num_rows = roi.shape[0] // 135
        num_cols = roi.shape[1] // 115

        center_points = []

        for row in range(num_rows):
            for col in range(num_cols):
                x = col * (117 + 8)
                y = row * (135 + 16)
                plt.plot([x, x + 115, x + 115, x, x], [y, y, y + 135, y + 135, y], color='red')

                center_x = x + 115 / 2
                center_y = y + 135 / 2
                center_points.append((center_x, center_y))
                plt.scatter(center_x, center_y, color='lime', s=10)

        plt.imshow(roi)
        plt.axis('off')  # 关闭坐标轴
        plt.show()
        print(center_points)

    # logging.disable(logging.DEBUG)
    #
    # while True:
    #     # 捕获屏幕图像
    #     screen_image = np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))
    #
    #     # 调用文本识别函数，获取识别结果和感兴趣区域
    #     recognition_result, processed_image = recognize_text(screen_image)
    #
    #     # 处理识别结果中的每个元组的第一个字符串，并重新组合元组
    #     processed_result = [(compare_to_existing_strings(recognition_result[i]), recognition_result[i + 1]) for i in
    #                         range(0, len(recognition_result), 2)]
    #
    #     print(processed_result)
    #
    #     plt.imshow(processed_image)
    #     plt.axis('off')  # 关闭坐标轴
    #     plt.show()

