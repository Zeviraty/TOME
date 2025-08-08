from datetime import datetime
import os

if not os.path.exists("logs"):
    os.mkdir("logs")

def warn(text:str, name:str="+"):
    text = f"[{datetime.today().strftime('%H:%M:%S')}] \033[33m[WARN] [{name}] {text}"
    open('logs/'+datetime.today().strftime('%Y-%m-%d'),'a').write(text.replace("\033[33m",'')+"\n")
    print(text+"\033[0m")

def error(text:str, name:str="+"):
    text = f"[{datetime.today().strftime('%H:%M:%S')}] \033[31m[ERROR] [{name}] {text}"
    open('logs/'+datetime.today().strftime('%Y-%m-%d'),'a').write(text.replace("\033[31m",'')+"\n")
    print(text+"\033[0m")

def info(text:str, name:str="+"):
    text = f"[{datetime.today().strftime('%H:%M:%S')}] [INFO] [{name}] {text}"
    open('logs/'+datetime.today().strftime('%Y-%m-%d'),'a').write(text+"\n")
    print(text+"\033[0m")

def disconnect(text:str, name:str="+"):
    text = f"[{datetime.today().strftime('%H:%M:%S')}] \033[34m[DISCONNECT] [{name}] {text}"
    open('logs/'+datetime.today().strftime('%Y-%m-%d'),'a').write(text.replace("\033[34m",'')+"\n")
    print(text+"\033[0m")
