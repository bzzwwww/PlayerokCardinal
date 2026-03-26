import os
from configparser import ConfigParser
import time
import telebot
from colorama import Fore, Style
from Utils.cardinal_tools import validate_proxy, hash_password

default_config = {
    "Playerok": {
        "token": "",
        "user_agent": "",
        "autoResponse": "0",
        "autoDelivery": "0",
        "autoRestore": "0",
        "restorePriorityMode": "premium"
    },
    "Telegram": {
        "enabled": "0",
        "token": "",
        "secretKeyHash": "ХешСекретногоПароля",
        "blockLogin": "0"
    },
    "Proxy": {
        "enable": "0",
        "ip": "",
        "port": "",
        "login": "",
        "password": "",
        "check": "0"
    },
    "Other": {
        "watermark": "🎮",
        "requestsDelay": "1.0",
        "safeMode": "0"
    }
}


def safe_input(prompt: str) -> str:
    try:
        tty_input = "CONIN$" if os.name == "nt" else "/dev/tty"
        tty_output = "CONOUT$" if os.name == "nt" else "/dev/tty"

        try:
            with open(tty_output, "w") as out_stream:
                out_stream.write(prompt)
                out_stream.flush()
            with open(tty_input, "r") as in_stream:
                line = in_stream.readline()
            if not line:
                raise EOFError
            return line.strip()
        except OSError:
            return input(prompt).strip()
    except EOFError:
        print(
            f"\n{Fore.RED}{Style.BRIGHT}Ввод прерван. Запусти первичную настройку в интерактивном терминале и попробуй еще раз.{Style.RESET_ALL}"
        )
        raise SystemExit(1)

def create_configs():
    if not os.path.exists("configs/auto_response.cfg"):
        with open("configs/auto_response.cfg", "w", encoding="utf-8"):
            ...
    if not os.path.exists("configs/auto_delivery.cfg"):
        with open("configs/auto_delivery.cfg", "w", encoding="utf-8"):
            ...

def create_config_obj(settings) -> ConfigParser:
    config = ConfigParser(delimiters=(":",), interpolation=None)
    config.optionxform = str
    config.read_dict(settings)
    return config

def contains_russian(text: str) -> bool:
    for char in text:
        if 'А' <= char <= 'я' or char in 'Ёё':
            return True
    return False

def first_setup():
    import colorama
    colorama.init()
    
    config = create_config_obj(default_config)
    sleep_time = 1

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Привет! {Fore.RED}(`-`)/{Style.RESET_ALL}")
    time.sleep(sleep_time)

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Не могу найти основной конфиг... {Fore.RED}(-_-;). . .{Style.RESET_ALL}")
    time.sleep(sleep_time)

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Давай ка проведем первичную настройку! {Fore.RED}°++°{Style.RESET_ALL}")
    time.sleep(sleep_time)

    while True:
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
              f"Введи токен (token) твоего Playerok аккаунта (можно найти в Cookie) {Fore.RED}(._.){Style.RESET_ALL}")
        token = safe_input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}")
        if len(token) > 10:
            config.set("Playerok", "token", token)
            break
        else:
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Неверный формат токена. Попробуй еще раз! {Fore.RED}\\(!!˚0˚)/{Style.RESET_ALL}")

    while True:
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
              f"Если хочешь, можешь указать свой User-agent (введи в Google \"my user agent\"). Или просто нажми Enter. "
              f"{Fore.RED}¯\\(°_o)/¯{Style.RESET_ALL}")
        user_agent = safe_input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}")
        if contains_russian(user_agent):
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Ты не знаешь, что такое Google? {Fore.RED}\\(!!˚0˚)/{Style.RESET_ALL}")
            continue
        if user_agent:
            config.set("Playerok", "user_agent", user_agent)
        break

    while True:
        print(
            f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}Введи API-токен Telegram-бота (получить можно у @BotFather). "
            f"Подойдет любой корректный токен. {Fore.RED}(._.){Style.RESET_ALL}")
        token = safe_input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}")
        try:
            if not token or ":" not in token or not token.split(":", 1)[0].isdigit():
                raise Exception("Неправильный формат токена")
            telebot.TeleBot(token).get_me()
        except Exception as ex:
            s = ""
            if str(ex):
                s = f" ({str(ex)})"
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Попробуй еще раз!{s} {Fore.RED}\\(!!˚0˚)/{Style.RESET_ALL}")
            continue
        break

    while True:
        print(
            f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}Придумай пароль (его потребует Telegram-бот). Пароль должен содержать более 8 символов, заглавные, строчные буквы и хотя бы одну цифру "
            f" {Fore.RED}ᴖ̮ ̮ᴖ{Style.RESET_ALL}")
        password = safe_input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}")
        if len(password) < 8 or password.lower() == password or password.upper() == password or not any([i.isdigit() for i in password]):
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Это плохой пароль. Попробуй еще раз! {Fore.RED}\\(!!˚0˚)/{Style.RESET_ALL}")
            continue
        break

    config.set("Telegram", "enabled", "1")
    config.set("Telegram", "token", token)
    config.set("Telegram", "secretKeyHash", hash_password(password))

    while True:
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
              f"Если хочешь использовать IPv4 прокси – укажи их в формате login:password@ip:port или ip:port. Если не нужны - просто нажми Enter. "
              f"{Fore.RED}(* ^ ω ^){Style.RESET_ALL}")
        proxy = safe_input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}")
        if proxy:
            try:
                login, password, ip, port = validate_proxy(proxy)
                config.set("Proxy", "enable", "1")
                config.set("Proxy", "check", "1")
                config.set("Proxy", "login", login)
                config.set("Proxy", "password", password)
                config.set("Proxy", "ip", ip)
                config.set("Proxy", "port", port)
                break
            except:
                print(f"\n{Fore.CYAN}{Style.BRIGHT}Неверный формат прокси. Попробуй еще раз! {Fore.RED}(o-_-o){Style.RESET_ALL}")
                continue
        else:
            break

    if not os.path.exists("configs"):
        os.makedirs("configs")
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Готово! Сейчас я сохраню конфиг и завершу программу! {Fore.RED}ʘ>ʘ{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}Запусти меня снова и напиши своему Telegram-боту. "
          f"Все остальное ты сможешь настроить через него. {Fore.RED}ʕ•ᴥ•ʔ{Style.RESET_ALL}")
    
    with open("configs/_main.cfg", "w", encoding="utf-8") as f:
        config.write(f)
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ Конфиг сохранен в configs/_main.cfg{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}Программа завершится через 5 секунд...{Style.RESET_ALL}")
    time.sleep(5)

