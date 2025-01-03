import os
import re
import json
import time
import string
import random
import ddddocr
import inspect
import asyncio
import requests
import secrets
from telegram import Bot
from loguru import logger
from datetime import datetime
from urllib.parse import quote
from requests.exceptions import JSONDecodeError
os.makedirs("static", exist_ok=True)
os.makedirs("ocr", exist_ok=True)
cache = {}
global input_token, input_chatid, username, email
config_file = 'static/config.json'
account_file = 'static/account.json'
log_file = 'static/log.json'
def get_input_prompt():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.') + str(datetime.now().microsecond // 1000).zfill(3)
    frame = inspect.stack()[1]
    module_name = inspect.getmodule(frame[0]).__name__
    module_info = f'{module_name}:<module>'
    caller_line = frame.lineno
    return f'\033[32m{current_time}\033[0m | \033[1;94mINPUT\033[0m    | \033[36m{module_info}:{caller_line}\033[0m - '
async def send_message(message):
    global input_token, input_chatid
    bot = Bot(token=input_token)
    try:
        await bot.send_message(chat_id=input_chatid, text=message)
    except Exception as e:
        logger.error(f"发送失败: {e}")
    return
def get_user_name():
    url = "https://www.ivtool.com/random-name-generater/uinames/api/index.php?region=united%20states&gender=male&amount=5&="
    resp = requests.get(url, verify=False)
    if resp.status_code != 200:
        print(resp.status_code, resp.text)
        raise Exception("获取名字出错")
    data = resp.json()
    return data
def generate_random_username():
    ints = random.randint(0, 4)
    random_digits = ''.join(random.choice(string.digits) for _ in range(ints))
    random_login = first_name + random_digits
    return random_login
def start_userconfig():
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                if config: return config['token'], config['chatid']
        except (json.JSONDecodeError, IOError):
            pass
        input_token = input(f"{get_input_prompt()}\033[1;94m请输入Telegram Bot Token [默认使用 @Serv00Reg_Bot]:\033[0m")
        if input_token == "": input_token = '7594103635:AAEoQKB_ApJgDbfoVJm-gwW6e0VVS_a5Dl4'
        input_chatid = get_valid_input(f"\033[1;94m请输入Telegram Chat ID:\033[0m", lambda x: x.isdigit() and int(x) > 0, "无效的ChatID,请输入一个正整数.")
    with open(config_file, 'w') as f:
        json.dump({'token': input_token.strip(), 'chatid': input_chatid.strip()}, f)
    return input_token, input_chatid
def get_valid_input(prompt, validation_func, error_msg):
    while True:
        user_input = input(f"{get_input_prompt()}{prompt}")
        if validation_func(user_input):
            return user_input
        logger.error(f"\033[1;93m{error_msg}\033[0m")
def play_music():
    mixer.init()
    mixer.music.load('music.mp3')
    mixer.music.play()
    time.sleep(10)
    mixer.music.stop()  
    return
def save_account():
    global username, email
    with open(account_file, 'w') as f:
        json.dump({'username': username, 'mail': email}, f)
    return username, email
def start_task(input_email: str):
    id_retry = 1
    global username, email, first_name, resp
    while True:
        try:
            User_Agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            Cookie = "csrftoken={}"
            url1 = "https://www.serv00.com/offer/create_new_account"
            headers = {f"User-Agent": User_Agent}
            captcha_url = "https://www.serv00.com/captcha/image/{}/"
            header2 = {"Cookie": Cookie, "User-Agent": User_Agent}
            url3 = "https://www.serv00.com/offer/create_new_account.json"
            header3 = {
                "content-length":   "207",
                "x-requested-with": "XMLHttpRequest",
                "User-Agent": User_Agent,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin":   "https://www.serv00.com",
                "sec-fetch-site":   "same-origin",
                "sec-fetch-mode":   "cors",
                "sec-fetch-dest":   "empty",
                "Referer": "https://www.serv00.com/offer/create_new_account",
                "Cookie": Cookie,
                
            }
            email = input_email
            usernames = get_user_name()
            _ = usernames.pop()
            first_name = _["name"]
            last_name = _["surname"]
            username = generate_random_username().lower()
            print(""), logger.info(f"{email} {first_name} {last_name} {username}")
            with requests.Session() as session:
                logger.info(f"打开注册网页 ")
                resp = session.get(url=url1, headers=headers, verify=False)
                if resp.status_code == 403:
                    logger.error("IP被限，停止注册！")
                    return
                content = resp.text
                headers = resp.headers
                csrftoken = re.findall(r"csrftoken=(\w+);", headers.get("set-cookie"))[0]
                header2["Cookie"] = header2["Cookie"].format(csrftoken)
                header3["Cookie"] = header3["Cookie"].format(csrftoken)
                captcha_0 = re.findall(r'id=\"id_captcha_0\" name=\"captcha_0\" value=\"(\w+)\">', content)[0]
                captcha_retry = 0
                while True:
                    time.sleep(random.uniform(0.2, 0.5))
                    logger.info("获取验证码")
                    resp = session.get(url=captcha_url.format(captcha_0), headers=dict(header2, **{"Cookie": header2["Cookie"].format(csrftoken)}), verify=False)
                    content = resp.content
                    cors = username
                    with open(f"static/{username}.jpg", "wb") as f:
                        f.write(content)
                    captcha_1 = ddddocr.DdddOcr(show_ad=False).classification(content).upper()
                    if bool(re.match(r'^[a-zA-Z0-9]{4}$', captcha_1)):
                        logger.info(f"识别成功:  \033[1;92m{captcha_1}\033[0m")
                    else:
                        logger.warning("识别失败")
                        captcha_retry += 1
                        if captcha_retry > 2: # 此处修改重试次数，默认200次.
                            captcha_retry = 1
                            time.sleep(random.uniform(2, 3))
                        continue
                    data = f"csrfmiddlewaretoken={csrftoken}&first_name={first_name}&last_name={last_name}&username={username}&email={quote(email)}&captcha_0={captcha_0}&captcha_1={captcha_1}&question=free&tos=on"
                    time.sleep(random.uniform(0.3, 0.5))
                    logger.info("提交请求")
                    resp = session.post(url=url3, headers=dict(header3, **{"Cookie": header3["Cookie"].format(csrftoken)}), data=data, verify=False)
                    content = resp.json()
                    logger.info(f'请求状态码: \033[1;93m{resp.status_code}\033[0m')
                    try:
                        if resp.status_code == 403:
                            logger.error("IP被滥用，停止注册！")
                            return
                        elif resp.status_code == 500:
                            if content.get("captcha") and content["captcha"][0] == "Invalid CAPTCHA":
                                captcha_0 = content["__captcha_key"]
                                continue
                            elif content.get("username") and content["username"][0] == "Maintenance time. Try again later.":
                                logger.error(f"第{id_retry}次提交成功")
                                id_retry += 1
                                captcha_0 = content["__captcha_key"]
                                continue
                            elif content.get("username") and content["username"][0] == "An account with the given username already exists - please choose a different login.":
                                logger.error(f"用户名：{username}已经被注册过")
                                break
                            elif content.get("email") and content["email"][0] == "Enter a valid email address.":
                                logger.error("无效的邮箱,请重新输入.")
                                return
                            elif content.get("email") and content["email"][0] == "An account has already been registered to this e-mail address.":
                                logger.error(f"{input_email}邮箱已被注册,请重新输入.")
                                asyncio.run(send_message(f"{input_email}已被注册,请重新输入."))
                                return
                            else:
                                print("未知500错误信息!")#调试输出
                                with open(log_file, "w") as f:
                                    json.dump(content, f)
                        else:
                            if resp.status_code == 200:
                                logger.success(f"账户 {username} 已成功创建!")
                                username, email = save_account()
                                asyncio.run(send_message(f"Success!\nEmail: {input_email}\nUserName: {username}"))
                                with open(log_file, "w") as f:
                                    json.dump(content, f)
                                return
                            else:
                                print("未知200信息!")#调试输出
                                username, email = save_account()
                                asyncio.run(send_message(f"Success!\nEmail: {input_email}\nUserName: {username}"))
                                with open(log_file, "w") as f:
                                    json.dump(content, f)
                                    continue
                    except JSONDecodeError:
                        logger.error("\033[7m获取信息错误,正在重试...\033[0m")
                        time.sleep(random.randint(1, 2))
        except Exception as e:
            logger.error("\033[7m发生异常:{e},正在重新开始任务...\033[0m")
            continue
        if input_email in cache:
            del cache[input_email]
    return
if __name__ == "__main__":
    First_Run = True
    while True:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                input_token, input_chatid = config['token'], config['chatid']
                break
        except (FileNotFoundError, json.JSONDecodeError):
            if First_Run: logger.error("\033[1;92m初始化运行未检测到配置文件.\033[0m"); First_Run = False
            input_token, input_chatid = start_userconfig()
            f.close()
os.system("cls" if os.name == "nt" else "clear")
response = requests.get('https://ping0.cc/geo', verify=False)
print(f"\n=============================\n{response.text[:200]}\n=============================")
logger.info("输入邮箱开始自动任务,退出快捷键Ctrl+C.\n")
while True:
    input_email = get_valid_input(f"\n请输入邮箱:", lambda x: '@' in x, "无效的邮箱,请重新输入.")
    if '@' not in input_email:
        logger.error("\033[1;93m无效的邮箱,请重新输入.\033[0m")
        continue
    start_task(input_email)
