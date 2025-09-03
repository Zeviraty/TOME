from datetime import datetime
import os
from pprint import pp

current_log = ""

def start():
    if not os.path.exists("logs"):
        os.mkdir("logs")

    global current_log
    current_log = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    
    while not os.path.exists('logs/'+current_log):
        if current_log[-1].isnumeric():
            current_log[-1] = str(int(current_log[-1]) + 1)
        else:
            current_log += "1"

def warn(text:str, name:str="+"):
    text = f"[{datetime.today().strftime('%H:%M:%S')}] \033[33m[WARN] [{name}] {text}"
    open('logs/'+current_log,'a').write(text.replace("\033[33m",'')+"\n")
    print(text+"\033[0m")

def error(text:str, name:str="+"):
    text = f"[{datetime.today().strftime('%H:%M:%S')}] \033[31m[ERROR] [{name}] {text}"
    open('logs/'+current_log,'a').write(text.replace("\033[31m",'')+"\n")
    print(text+"\033[0m")

def info(text:str, name:str="+"):
    text = f"[{datetime.today().strftime('%H:%M:%S')}] [INFO] [{name}] {text}"
    open('logs/'+current_log,'a').write(text+"\n")
    print(text+"\033[0m")

def disconnect(text:str, name:str="+"):
    text = f"[{datetime.today().strftime('%H:%M:%S')}] \033[34m[DISCONNECT] [{name}] {text}"
    open('logs/'+current_log,'a').write(text.replace("\033[34m",'')+"\n")
    print(text+"\033[0m")



def pwarn(text:str, name:str="+"):
    prefix = f"[{datetime.today().strftime('%H:%M:%S')}] \033[33m[WARN] [{name}]"
    open('logs/'+current_log,'a').write(text.replace("\033[33m",'')+"\n")
    print(prefix,end="")
    pp(text,"\033[0m")

def perror(text:str, name:str="+"):
    prefix = f"[{datetime.today().strftime('%H:%M:%S')}] \033[31m[ERROR] [{name}]"
    open('logs/'+current_log,'a').write(text.replace("\033[31m",'')+"\n")
    print(prefix,end="")
    pp(text,"\033[0m")

def pinfo(text:str, name:str="+"):
    prefix = f"[{datetime.today().strftime('%H:%M:%S')}] [INFO] [{name}]"
    open('logs/'+current_log,'a').write(text+"\n")
    print(prefix,end="")
    pp(text,"\033[0m")
