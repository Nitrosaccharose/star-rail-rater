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


def image_entry_processor(image):
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

    # 添加上下左右填充
    padding_top = 10
    padding_bottom = 10
    padding_left = 40
    padding_right = 40

    # 创建一个新的图片，尺寸加上填充值
    new_height = processed_img.shape[0] + padding_top + padding_bottom
    new_width = processed_img.shape[1] + padding_left + padding_right
    new_img = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    # 将处理后的图片数据放置在新图片的中间
    new_img[padding_top:padding_top + processed_img.shape[0],
    padding_left:padding_left + processed_img.shape[1]] = processed_img

    return new_img


def image_name_processor(image):
    target_color1 = (255, 200, 112)  # 目标颜色1
    target_color2 = (194, 152, 253)  # 目标颜色2
    target_color3 = (115, 177, 243)  # 目标颜色3
    white_color = (255, 255, 255)
    black_color = (0, 0, 0)
    processed_img = np.copy(image)

    for y in range(processed_img.shape[0]):
        for x in range(processed_img.shape[1]):
            pixel_color = processed_img[y, x]

            # 判断是否接近目标颜色
            close_to_target1 = all(abs(pixel_color[i] - target_color1[i]) <= 40 for i in range(3))
            close_to_target2 = all(abs(pixel_color[i] - target_color2[i]) <= 40 for i in range(3))
            close_to_target3 = all(abs(pixel_color[i] - target_color3[i]) <= 40 for i in range(3))

            if close_to_target1 or close_to_target2 or close_to_target3:
                processed_img[y, x] = white_color
            else:
                processed_img[y, x] = black_color

    # 添加上下左右填充
    padding_top = 80
    padding_bottom = 80
    padding_left = 20
    padding_right = 0

    # 创建一个新的图片，尺寸加上填充值
    new_height = processed_img.shape[0] + padding_top + padding_bottom
    new_width = processed_img.shape[1] + padding_left + padding_right
    new_img = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    # 将处理后的图片数据放置在新图片的中间
    new_img[padding_top:padding_top + processed_img.shape[0],
    padding_left:padding_left + processed_img.shape[1]] = processed_img

    return new_img


def image_level_processor(image):
    threshold = 210  # 阈值，大于等于该值的色块将变成白色，否则变成黑色
    white_color = (255, 255, 255)
    black_color = (0, 0, 0)
    processed_img = np.copy(image)

    for y in range(processed_img.shape[0]):
        for x in range(processed_img.shape[1]):
            pixel_color = processed_img[y, x]

            if np.all(pixel_color >= threshold):
                processed_img[y, x] = white_color
            else:
                processed_img[y, x] = black_color

    # 添加上下左右填充
    padding_top = 50
    padding_bottom = 50
    padding_left = 80
    padding_right = 80

    # 创建一个新的图片，尺寸加上填充值
    new_height = processed_img.shape[0] + padding_top + padding_bottom
    new_width = processed_img.shape[1] + padding_left + padding_right
    new_img = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    # 将处理后的图片数据放置在新图片的中间
    new_img[padding_top:padding_top + processed_img.shape[0],
    padding_left:padding_left + processed_img.shape[1]] = processed_img

    return new_img


def recognize_entry(image):
    # 创建PaddleOCR实例
    ocr_instance = PaddleOCR(use_angle_cls=True, lang="ch")

    # 从原始图像中提取感兴趣区域的部分
    roi = crop_diagonal_rectangle(image, (1442, 400), (1842, 587))

    # 使用图片处理器处理传入的图像
    roi_processor = image_entry_processor(roi)

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

    # 使用图片处理器处理传入的图像
    roi_processor = image_name_processor(roi)

    # 调用PaddleOCR的识别方法并获取结果列表
    result_list = ocr_instance.ocr(roi_processor)[0]

    # 从识别结果中提取文本并存储在文本列表中
    text_list = []
    for res in result_list:
        text_list.append(res[1][0])

    return text_list, roi_processor


def recognize_level(image):
    # 创建PaddleOCR实例
    ocr_instance = PaddleOCR(use_angle_cls=True, lang="ch")

    # 从原始图像中提取感兴趣区域的部分
    roi = crop_diagonal_rectangle(image, (1442, 311), (1485, 345))

    # 使用图片处理器处理传入的图像
    roi_processor = image_level_processor(roi)

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


def compare_to_existing_strings(existing_strings, input_string):
    input_string = input_string.strip()

    if input_string == "":
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

    entry_str_list = [
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
        "物理属性伤害提高",
        "能量恢复效率",
        "治疗量加成"
    ]

    name_str_list = ['过客的冥途游履', '过客的残绣风衣', '过客的游龙臂鞲', '过客的逢春木簪', '快枪手的猎风披肩',
                     '快枪手的粗革手套', '快枪手的野穗毡帽', '快枪手的铆钉马靴', '圣骑的宽恕盔面', '圣骑的沉默誓环',
                     '圣骑的秩序铁靴', '圣骑的肃穆胸甲', '雪猎的荒神兜帽', '雪猎的巨蜥手套', '雪猎的冰龙披风',
                     '雪猎的鹿皮软靴', '拳王的冠军护头', '拳王的弧步战靴', '拳王的贴身护胸', '拳王的重炮拳套',
                     '铁卫的旧制军服', '铁卫的银鳞手甲', '铁卫的铸铁面盔', '铁卫的白银护胫', '火匠的黑曜目镜',
                     '火匠的御火戒指', '火匠的阻燃围裙', '火匠的合金义肢', '天才的元域深潜', '天才的引力漫步',
                     '天才的超距遥感', '天才的频变捕手', '乐队的偏光墨镜', '乐队的巡演手绳', '乐队的钉刺皮衣',
                     '乐队的铆钉短靴', '翔鹰的长喙头盔', '翔鹰的鹰击指环', '翔鹰的翼装束带', '翔鹰的绒羽绑带',
                     '怪盗的千人假面', '怪盗的流星快靴', '怪盗的纤钢爪钩', '怪盗的绘纹手套', '莳者的复明义眼',
                     '莳者的机巧木手', '莳者的承露羽衣', '莳者的天人丝履', '信使的全息目镜', '信使的密信挎包',
                     '信使的百变义手', '信使的酷跑板鞋', '黑塔的空间站点', '黑塔的漫历轨迹', '罗浮仙舟的天外楼船',
                     '罗浮仙舟的建木枝蔓', '公司的巨构总部', '公司的贸易航道', '贝洛伯格的存护堡垒',
                     '贝洛伯格的铁卫防线', '螺丝星的机械烈阳', '螺丝星的环星孔带', '萨尔索图的移动城市',
                     '萨尔索图的晨昏界线', '塔利亚的钉壳小镇', '塔利亚的裸皮电线', '翁瓦克的诞生之岛',
                     '翁瓦克的环岛海岸', '泰科铵的镭射球场', '泰科铵的弧光赛道', '伊须磨洲的残船鲸落',
                     '伊须磨洲的坼裂缆索']

    for i in range(0, len(recognition_entry_result), 2):
        if i + 1 < len(recognition_entry_result):
            processed_result.append(
                (compare_to_existing_strings(entry_str_list, recognition_entry_result[i]),
                 recognition_entry_result[i + 1]))
        else:
            processed_result.append((compare_to_existing_strings(entry_str_list, recognition_entry_result[i]), None))

    recognition_name_result, processed_name_image = recognize_name(screen_image)

    if len(recognition_name_result) == 0:
        name_result = compare_to_existing_strings(name_str_list, "")
    else:
        name_result = compare_to_existing_strings(name_str_list, recognition_name_result[0])

    recognition_level_result, processed_level_image = recognize_level(screen_image)

    level_result = recognition_level_result[0]

    plt.figure(figsize=(5, 10))
    plt.subplot(3, 1, 1)
    plt.imshow(processed_entry_image)
    plt.axis('off')  # 取消坐标轴
    plt.subplot(3, 1, 2)
    plt.imshow(processed_name_image)
    plt.axis('off')  # 取消坐标轴
    plt.subplot(3, 1, 3)
    plt.imshow(processed_level_image)
    plt.axis('off')  # 取消坐标轴
    plt.tight_layout()
    plt.show()

    return [name_result, level_result, processed_result]


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

    recognize_list = []

    for _ in range(5):
        pyautogui.click(1353, 210)
        time.sleep(0.1)
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
