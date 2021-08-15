#press on default desktop setup
import os
os.environ['DISPLAY']=":1"

import pyautogui
screenWidth, screenHeight = pyautogui.size()
pyautogui.moveTo(screenWidth/2, screenHeight/2)
pyautogui.click()
pyautogui.press('enter')