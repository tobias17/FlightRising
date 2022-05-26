from doctest import master
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import numpy as np
import cv2 as cv
from time import sleep
import os, uuid
from settings import *

CIPHER_NAME = 'cipher.txt'

def guid_to_img(guid_str):
    return f'{guid_str}.png'

def main():

    if not os.path.exists(SESSION_NAME):
        os.mkdir(SESSION_NAME)

    cipher_path = os.path.join(SESSION_NAME, CIPHER_NAME)
    if not os.path.exists(cipher_path):
        pairs = []
        for male in males:
            for female in females:
                pairs.append( (uuid.uuid4().hex, male, female) )
        pairs = sorted(pairs, key=lambda x: x[0])
        with open(cipher_path, 'w') as f:
            lines = []
            for pair in pairs:
                lines.append(','.join(pair))
            f.write('\n'.join(lines))
    
    with open(cipher_path) as f:
        lines = f.read().split('\n')
        pairs = [line.split(',') for line in lines]
    
    todo_list = []
    for pair in pairs:
        if not os.path.exists(os.path.join(SESSION_NAME, guid_to_img(pair[0]))):
            todo_list.append(pair)
    
    if len(todo_list) == 0:
        print('no work found to do, exiting')
        return
    print(f'found {len(todo_list)} items to do, starting browser')

    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if HEADLESS: chrome_options.add_argument('headless')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    driver.get('https://flightrising.com/main.php?p=scrying&view=progeny')
    sleep(2.0)

    left_input_box = driver.find_element(by=By.ID, value='id10t1')
    right_input_box = driver.find_element(by=By.ID, value='id10t2')
    preview_button = driver.find_element(by=By.ID, value='super-container').find_element(by=By.CLASS_NAME, value='thingbutton')

    for guid, male, female in todo_list:
        left_input_box.clear()
        left_input_box.send_keys(male)
        right_input_box.clear()
        right_input_box.send_keys(female)
        img_list = []

        for _ in range(GRID_SIZE ** 2):
            preview_button.click()
            sleep(0.5)

            preview_section = driver.find_element(by=By.ID, value='preview')
            imgs = preview_section.find_elements(by=By.TAG_NAME, value='img')

            for img in imgs:
                img.screenshot('temp.png')
                img_list.append(cv.imread('temp.png'))
        
        row_count = GRID_SIZE * 2
        img_height = img_list[0].shape[0]
        img_width  = img_list[0].shape[1]
        master_img = np.zeros((img_height * row_count, img_width  * row_count, 3))

        for i, img in enumerate(img_list):
            super_x, super_y = i % row_count, i // row_count
            master_img[super_y*img_height:(super_y+1)*img_height, super_x*img_width:(super_x+1)*img_width] = img

        cv.imwrite(os.path.join(SESSION_NAME, guid_to_img(guid)), master_img)

if '__main__' in __name__:
    main()