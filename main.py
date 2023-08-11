import easyocr
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import ImageGrab


def recognize_text(screen_image):
    reader = easyocr.Reader(['ch_sim', 'en'])

    gray = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)

    _, thresholded = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY_INV)

    thresholded[330:465, 1625:1810] = 255

    top_left_corner = (1530, 275)
    bottom_right_corner = (1890, 465)

    roi = thresholded[top_left_corner[1]:bottom_right_corner[1], top_left_corner[0]:bottom_right_corner[0]]

    result = reader.readtext(roi)
    text = ' '.join([res[1] for res in result])

    return text, roi


if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = "True"
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    while True:
        # Capture the screen image
        screen_image = np.array(ImageGrab.grab(bbox=(0, 0, 1920, 1080)))

        recognition_result, roi = recognize_text(screen_image)

        print("识别结果:\n", recognition_result)

        # Display the ROI using matplotlib
        plt.imshow(roi, cmap='gray')
        plt.axis('off')
        plt.show()

