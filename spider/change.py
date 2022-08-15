import pyautogui
import time
import requests
import os
import random
import subprocess

SLEEP = 60*3
from datetime import datetime
#United States


def get_ip_file_path(country=None):
    if country == None:
        country = 'US'
    for root, dirs, files in os.walk(country, topdown=False):
        return country+'/'+random.choice(files)

def change_ip(country=None):
    pyautogui.moveTo(1918, 1060)
    pyautogui.click()
    time.sleep(1)
    pyautogui.moveTo(1730, 1060)
    pyautogui.rightClick()
    time.sleep(1)

    if country == None:
        for root, dirs, files in os.walk('./'):
            if root == './':
                country = random.choice([i for i in dirs if i.find('__') == -1])
                break
    ip_file_path = get_ip_file_path(country)
    print(ip_file_path)
    pyautogui.click('favorite.jpg')
    time.sleep(1)
    try:
        pyautogui.click(ip_file_path)
    except Exception as e:
        print(e)
        print("选择ip失败了，重新开始")
        with open('ip_error.txt','a+',encoding='utf-8') as f:
            f.write(str(datetime.now())+'----'+ip_file_path+'----error'+'\n')
        change_ip(country)


    get_ip_url = 'http://httpbin.org/ip'
    wait_time = 1
    pyautogui.moveTo(1918, 1060)
    pyautogui.click()
    time.sleep(1)
    while True:
            try:
                ip = requests.get(get_ip_url,timeout=10).json()['origin']
                check_ip_url = 'http://ip-api.com/json/'+ip
                ip_content = requests.get(check_ip_url,timeout=10)
                res = ip_content.json()
                if res['country'] != 'China':
                    print(datetime.now(),ip,res['country'],'换ip成功')

                    return True
            except Exception as e:
                #print(e)
                pass
            time.sleep(1)
            wait_time = wait_time + 1
            if wait_time >= 30:
                print("换ip超时了")
                return False
if __name__ == '__main__':
    while True:
        subprocess.Popen('taskkill /F /im chrome.exe',shell=True)
        change_ip()
        subprocess.Popen("C:\Program Files\Google\Chrome\Application\chrome.exe", shell=True)
        time.sleep(60 * 10)




