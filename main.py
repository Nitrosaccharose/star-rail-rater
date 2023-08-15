import logging
import re
import time
import numpy as np
import pyautogui
from PIL import ImageGrab
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
import win32con
import win32gui as w32


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

            if (close_to_target and y < processed_img.shape[0] // 2) or np.all(pixel_color >= threshold):
                processed_img[y, x] = white_color
            else:
                processed_img[y, x] = black_color

    return processed_img


def recognize_entry(image):
    # 创建PaddleOCR实例
    ocr_instance = PaddleOCR(use_angle_cls=True, lang="ch")

    # 从原始图像中提取感兴趣区域的部分
    roi = crop_diagonal_rectangle(image, (1442, 400), (1842, 587))

    # 使用图片处理器处理传入的图像
    roi_processor = image_processor(roi)

    # 调用PaddleOCR的识别方法并获取结果列表
    result_list = ocr_instance.ocr(roi_processor)[0]

    # 从识别结果中提取文本并存储在文本列表中
    text_list = []
    for res in result_list:
        text_list.append(res[1][0])

    return text_list, roi_processor


def recognize_name(image):
    # 创建PaddleOCR实例
    ocr_instance = PaddleOCR(use_angle_cls=True, lang="ch")

    # 从原始图像中提取感兴趣区域的部分
    roi = crop_diagonal_rectangle(image, (1400, 130), (1842, 160))

    # 调用PaddleOCR的识别方法并获取结果列表
    result_list = ocr_instance.ocr(roi)[0]

    # 从识别结果中提取文本并存储在文本列表中
    text_list = []
    for res in result_list:
        text_list.append(res[1][0])

    return text_list, roi


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


def recognize():
    screen_image = np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))

    # 调用文本识别函数，获取识别结果和感兴趣区域
    recognition_entry_result, processed_entry_image = recognize_entry(screen_image)

    # 处理识别结果中的每个元组的第一个字符串，并重新组合元组
    processed_result = []

    for i in range(0, len(recognition_entry_result), 2):
        if i + 1 < len(recognition_entry_result):
            processed_result.append(
                (compare_to_existing_strings(recognition_entry_result[i]), recognition_entry_result[i + 1]))
        else:
            processed_result.append((compare_to_existing_strings(recognition_entry_result[i]), None))

    recognition_name_result, processed_name_image = recognize_name(screen_image)

    # 使用matplotlib展示处理后的图片
    plt.figure(figsize=(5, 10))
    plt.subplot(2, 1, 1)
    plt.imshow(processed_entry_image)
    plt.axis('off')  # 取消坐标轴
    plt.subplot(2, 1, 2)
    plt.imshow(processed_name_image)
    plt.axis('off')  # 取消坐标轴
    plt.tight_layout()
    plt.show()

    return [recognition_name_result, processed_result]


if __name__ == '__main__':
    logging.disable(logging.DEBUG)

    startTrain = w32.FindWindow('UnityWndClass', u'崩坏：星穹铁道')
    if startTrain != 0:
        w32.ShowWindow(startTrain, win32con.SW_NORMAL)
        w32.SetForegroundWindow(startTrain)
        time.sleep(1)
    else:
        print("Window not found.")
        exit(0)

    center_points = [
        [(57.5, 67.5), (182.5, 67.5), (307.5, 67.5), (432.5, 67.5), (557.5, 67.5), (682.5, 67.5), (807.5, 67.5),
         (932.5, 67.5), (1057.5, 67.5)],
        [(57.5, 218.5), (182.5, 218.5), (307.5, 218.5), (432.5, 218.5), (557.5, 218.5), (682.5, 218.5),
         (807.5, 218.5), (932.5, 218.5), (1057.5, 218.5)],
        [(57.5, 369.5), (182.5, 369.5), (307.5, 369.5), (432.5, 369.5), (557.5, 369.5), (682.5, 369.5),
         (807.5, 369.5), (932.5, 369.5), (1057.5, 369.5)],
        [(57.5, 520.5), (182.5, 520.5), (307.5, 520.5), (432.5, 520.5), (557.5, 520.5), (682.5, 520.5),
         (807.5, 520.5), (932.5, 520.5), (1057.5, 520.5)],
        [(57.5, 671.5), (182.5, 671.5), (307.5, 671.5), (432.5, 671.5), (557.5, 671.5), (682.5, 671.5),
         (807.5, 671.5), (932.5, 671.5), (1057.5, 671.5)]]

    offset_val = (124, 193)

    click_count = 0

    roi_num = crop_diagonal_rectangle(np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080))), (900, 970), (1050, 1010))
    click_num = int(re.findall(r'\d+', PaddleOCR(use_angle_cls=True, lang="ch").ocr(roi_num)[0][0][1][0])[0])

    for _ in range(5):
        pyautogui.click(1353, 210)
        time.sleep(0.1)
    recognize_list = []
    for row in center_points:
        for point in row:
            x, y = point
            pyautogui.click(x + offset_val[0], y + offset_val[1])

            recognize_res = recognize()
            recognize_list.append(recognize_res)
            print(recognize_res)

            click_count += 1
            time.sleep(0.1)
            if click_count >= click_num:
                break

    if click_num > 45:
        while True:
            # 向下滚动一行
            for _ in range(5):
                pyautogui.moveTo(1290, 550)
                pyautogui.scroll(-1)

            for point in center_points[-1]:
                x, y = point
                pyautogui.click(x + offset_val[0], y + offset_val[1])

                recognize_res = recognize()
                recognize_list.append(recognize_res)
                print(recognize_res)

                click_count += 1
                time.sleep(0.1)  # 可以根据实际情况调整点击之间的时间间隔
                if click_count >= click_num:
                    break

            if click_count >= click_num:
                break
