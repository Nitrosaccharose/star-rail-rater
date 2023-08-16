import logging
import re
import time

import numpy as np
from PIL import ImageGrab, Image
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
import pyautogui
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
    padding_top = 0
    padding_bottom = 0
    padding_left = 20
    padding_right = 20

    # 创建一个新的图片，尺寸加上填充值
    new_height = processed_img.shape[0] + padding_top + padding_bottom
    new_width = processed_img.shape[1] + padding_left + padding_right
    new_img = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    target_height = padding_top + processed_img.shape[0]
    target_width = padding_left + processed_img.shape[1]
    new_img[padding_top:target_height, padding_left:target_width] = processed_img

    new_img = 255 - new_img

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
    padding_top = 30
    padding_bottom = 30
    padding_left = 20
    padding_right = 0

    # 创建一个新的图片，尺寸加上填充值
    new_height = processed_img.shape[0] + padding_top + padding_bottom
    new_width = processed_img.shape[1] + padding_left + padding_right
    new_img = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    target_height = padding_top + processed_img.shape[0]
    target_width = padding_left + processed_img.shape[1]
    new_img[padding_top:target_height, padding_left:target_width] = processed_img

    new_img = 255 - new_img

    return new_img


def image_level_processor(image):
    threshold = 230
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
    padding_top = 80
    padding_bottom = 80
    padding_left = 40
    padding_right = 40

    # 创建一个新的图片，尺寸加上填充值
    new_height = processed_img.shape[0] + padding_top + padding_bottom
    new_width = processed_img.shape[1] + padding_left + padding_right
    new_img = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    target_height = padding_top + processed_img.shape[0]
    target_width = padding_left + processed_img.shape[1]
    new_img[padding_top:target_height, padding_left:target_width] = processed_img

    new_img = 255 - new_img

    return new_img


def perform_ocr(image, lang):
    ocr_instance = PaddleOCR(use_angle_cls=True, lang=lang)
    result_list = ocr_instance.ocr(image)[0]
    recognized_texts = []
    for res in result_list:
        recognized_texts.append(res[1][0])
    return recognized_texts


def recognize_entry(image):
    roi = crop_diagonal_rectangle(image, (1442, 400), (1842, 587))
    processed_image = image_entry_processor(roi)
    text_list = perform_ocr(processed_image, "ch")
    return text_list, processed_image


def recognize_name(image):
    roi = crop_diagonal_rectangle(image, (1400, 130), (1842, 160))
    processed_image = image_name_processor(roi)
    text_list = perform_ocr(processed_image, "ch")
    return text_list, processed_image


def recognize_level(image):
    roi = crop_diagonal_rectangle(image, (1442, 311), (1485, 345))
    processed_image = image_level_processor(roi)
    text_list = perform_ocr(processed_image, "en")
    return text_list, processed_image


def is_five_star_relic(image):
    roi = crop_diagonal_rectangle(image, (1400, 130), (1842, 160))
    target_color1 = (194, 152, 253)  # 紫色
    target_color2 = (115, 177, 243)  # 蓝色
    for y in range(roi.shape[0]):
        for x in range(roi.shape[1]):
            pixel_color = roi[y, x]

            # 判断是否接近目标颜色
            close_to_target1 = all(abs(pixel_color[i] - target_color1[i]) <= 30 for i in range(3))
            close_to_target2 = all(abs(pixel_color[i] - target_color2[i]) <= 30 for i in range(3))

            if close_to_target1 or close_to_target2:
                return False
    return True


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


def get_recognize_all_result(screen_image):
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

    if len(recognition_level_result) == 0:
        level_result = -1
    else:
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


def get_fullscreen_capture():
    return np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))


def get_relic_num():
    roi = crop_diagonal_rectangle(get_fullscreen_capture(), (900, 970), (1050, 1010))
    return int(re.findall(r'\d+', PaddleOCR(use_angle_cls=True, lang="ch").ocr(roi)[0][0][1][0])[0])


def init_main_setup():
    logging.disable(logging.DEBUG)


def set_game_window_on_top():
    startTrain = w32.FindWindow('UnityWndClass', u'崩坏：星穹铁道')
    if startTrain != 0:
        w32.ShowWindow(startTrain, win32con.SW_NORMAL)
        w32.SetForegroundWindow(startTrain)
        time.sleep(1)
        print("游戏窗口已置顶。")
    else:
        print("未找到游戏窗口！")
        exit(0)


def set_game_window_not_on_top():
    game_window_title = u'崩坏：星穹铁道'
    game_window = w32.FindWindow('UnityWndClass', game_window_title)

    if game_window != 0:
        w32.SetWindowPos(game_window, win32con.HWND_BOTTOM, 0, 0, 0, 0,
                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        print("游戏窗口已取消置顶。")
    else:
        print("未找到游戏窗口！")


def scroll_to_next_relic_row():
    for _ in range(5):
        pyautogui.moveTo(1290, 550)
        pyautogui.scroll(-1)


def reset_relic_list_to_start():
    for _ in range(5):
        pyautogui.click(1353, 210)
        time.sleep(0.1)


def scale_image(image_data, scale_factor):
    pil_image = Image.fromarray(image_data)

    new_width = int(image_data.shape[1] * scale_factor)
    new_height = int(image_data.shape[0] * scale_factor)

    resized_image = pil_image.resize((new_width, new_height), Image.ANTIALIAS)

    resized_image_data = np.array(resized_image)
    return resized_image_data


def get_relic_list():
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
    image_data_list = []
    result_list = []
    relics_num = get_relic_num()
    for row in center_points:
        for point in row:
            x, y = point
            pyautogui.click(x + offset_val[0], y + offset_val[1])
            image_data_list.append(get_fullscreen_capture())

            click_count += 1
            time.sleep(0.1)
            if click_count >= relics_num:
                break
        if click_count >= relics_num:
            break

    if relics_num > 45:
        while True:
            # 向下滚动一行
            scroll_to_next_relic_row()
            for point in center_points[-1]:
                x, y = point
                pyautogui.click(x + offset_val[0], y + offset_val[1])
                image_data_list.append(get_fullscreen_capture())

                click_count += 1
                time.sleep(0.1)
                if click_count >= relics_num:
                    break

            if click_count >= relics_num:
                break

    set_game_window_not_on_top()

    total_time = 0.0
    print("[")
    for image_data in image_data_list:
        if is_five_star_relic(image_data):
            start_time = time.time()

            recognize_res = get_recognize_all_result(image_data)

            end_time = time.time()
            iteration_time = end_time - start_time
            total_time += iteration_time

            print(recognize_res, end=",\n")

            result_list.append(recognize_res)
    print("]")
    average_time = total_time / len(image_data_list)

    print(f"总共用时: {total_time:.4f} 秒")
    print(f"平均用时: {average_time:.4f} 秒")
    return result_list


def validate_relic(data_relic):
    valid_names = ['过客的冥途游履', '过客的残绣风衣', '过客的游龙臂鞲', '过客的逢春木簪', '快枪手的猎风披肩',
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
    msg_str = ""
    # Check the name (0号元素)
    if data_relic[0] not in valid_names:
        msg_str += "名字不合法"

    # Check the 1号元素是否为纯数字并且取值范围在0~15
    if not re.match(r'^\d+$', data_relic[1]) or int(data_relic[1]) < 0 or int(data_relic[1]) > 15:
        msg_str += "等级不是纯数字或不在范围内"

    # Check the 2号元素中的每个元组
    for item in data_relic[2]:
        if len(item) != 2:
            msg_str += "元组长度不等于2"

        valid_attributes = [
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
        if item[0] not in valid_attributes:
            msg_str += f"属性{item[0]}不合法"

        if not re.match(r'^\d+$', item[1]) and not re.match(r'^\d+(\.\d+)?%$', item[1]):
            msg_str += f"属性{item[0]}的值不合法"
        if msg_str == "":
            return msg_str, True
        return msg_str, False


def validate_relic_list(data_list):
    all_valid = True
    for data in data_list:
        error_str, is_valid = validate_relic(data)
        if not is_valid:
            all_valid = False
            print(data, error_str)
    if all_valid:
        print("全部合法")


if __name__ == '__main__':
    init_main_setup()

    set_game_window_on_top()

    reset_relic_list_to_start()

    relics_list = get_relic_list()

    validate_relic_list(relics_list)
