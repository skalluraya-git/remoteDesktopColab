try:
  import os
  os.environ['DISPLAY']=":1"
  import pyautogui
  import time
  os.popen("anydesk")
  time.sleep(5)

  adpass = "necromancer123"

  # screenWidth, screenHeight = pyautogui.size()
  # pyautogui.moveTo(screenWidth/2, screenHeight/2)
  # pyautogui.click()
  # pyautogui.press('enter')

  pyautogui.click(711, 319)
  time.sleep(1)
  pyautogui.click(554,217)
  time.sleep(1)
  pyautogui.click(535,342)
  time.sleep(2)
  pyautogui.click(535,428)
  pyautogui.typewrite(adpass)
  pyautogui.click(535,491)
  pyautogui.typewrite(adpass)
  pyautogui.click(785,552)

  pyautogui.click(991,810) #close
  print("ANYDESK pass:",adpass)
except Exception as e:
  print(e)