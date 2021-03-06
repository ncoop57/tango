# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/07_utils.ipynb (unless otherwise specified).

__all__ = ['write_json_line_by_line', 'read_csv_to_dic_list', 'read_json', 'read_json_line_by_line', 'find_file',
           'write_csv_from_json_list', 'group_dict', 'load_settings', 'get_grayscale', 'remove_noise', 'thresholding',
           'thresholding_med', 'dilate', 'erode', 'opening', 'canny', 'deskew', 'match_template', 'extract_text',
           'preprocess_img', 'extract_frames', 'process_frame']

# Cell
import csv
import cv2
import fnmatch
import json
import ntpath
import os
import pytesseract

import numpy as np
import pandas as pd

from itertools import groupby

# Cell
def write_json_line_by_line(data, file_path):
    with open(file_path, 'w') as dest_file:
        for record in data:
            print(json.dumps(record), file=dest_file)


def read_csv_to_dic_list(file_path):
    data = []
    with open(file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for item in csv_reader:
            data.append(item)
    return data


def read_json(file_path):
    with open(file_path) as file:
        return json.load(file)


def read_json_line_by_line(file_path):
    data = []
    with open(file_path) as sett_file:
        for item in map(json.loads, sett_file):
            data.append(item)
    return data


def find_file(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                if 'fix' not in name:
                    result.append(os.path.join(root, name))
    return result


def write_csv_from_json_list(data, output_path):
    pd.read_json(json.dumps(data)).to_csv(output_path, index=False, sep=";")


def group_dict(data, lambda_expr):
    result = {}
    data.sort(key=lambda_expr)
    for k, v in groupby(data, key=lambda_expr):
        result[k] = list(v)
    return result


def load_settings(path):
    settings_files = find_file("*.json", path)

    all_settings = {}
    for file_path in settings_files:
        setting_name = ntpath.basename(file_path).split(".")[0]
        all_settings[setting_name] = []
        with open(file_path) as sett_file:
            for retrieval_run in map(json.loads, sett_file):
                all_settings[setting_name].append(retrieval_run)

    return all_settings

# Cell

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 5)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def thresholding_med(image):
    return cv2.threshold(cv2.medianBlur(image, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# dilation
def dilate(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


# erosion
def erode(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


# opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((1, 1), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


# canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)


# skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


# template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

# Cell
def extract_text(img):
    custom_config = r'--oem 3 --psm 3'
    return pytesseract.image_to_string(img, config=custom_config)


def preprocess_img(image):
    prep_img = get_grayscale(image)
    prep_img = opening(prep_img)
    prep_img = thresholding_med(prep_img)
    return prep_img


def extract_frames(video_path, out_path, fps):
    ffmpeg_command = f'ffmpeg -i {video_path} -vf "fps={fps}" {out_path}/%04d.jpeg'
    os.system(ffmpeg_command)


def process_frame(frame):
    image_frame = cv2.imread(frame)
    prep_image = preprocess_img(image_frame)
    text = extract_text(prep_image)

    frame_name = ntpath.basename(frame).split(".")[0]
    record = {"f": frame_name, "txt": text}
    return record