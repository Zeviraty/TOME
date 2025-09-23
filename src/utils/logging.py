from datetime import datetime
import os
from pprint import pp

current_log = ""
testing = False

def start(testing_mode=False):
    if not os.path.exists("logs"):
        os.mkdir("logs")

    global current_log
    current_log = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    global testing
    testing = testing_mode
    
    while os.path.exists('logs/'+current_log):
        if current_log[-1].isnumeric():
            edited = list(current_log)
            edited[-1] = str(int(current_log[-1]) + 1)
            current_log = str(edited)
        else:
            current_log += "1"

def warn(data, name:str="+"):
    if testing:
        return
    data = f"[{datetime.today().strftime('%H:%M:%S')}] \033[33m[WARN] [{name}] {data}"
    open('logs/'+current_log,'a').write(data.replace("\033[33m",'')+"\n")
    print(str(data)+"\033[0m")

def error(data, name:str="+"):
    if testing:
        return
    data = f"[{datetime.today().strftime('%H:%M:%S')}] \033[31m[ERROR] [{name}] {data}"
    open('logs/'+current_log,'a').write(data.replace("\033[31m",'')+"\n")
    print(str(data)+"\033[0m")

def info(data, name:str="+"):
    if testing:
        return
    data = f"[{datetime.today().strftime('%H:%M:%S')}] [INFO] [{name}] {data}"
    open('logs/'+current_log,'a').write(str(data)+"\n")
    print(str(data)+"\033[0m")

def disconnect(data, name:str="+"):
    if testing:
        return
    data = f"[{datetime.today().strftime('%H:%M:%S')}] \033[34m[DISCONNECT] [{name}] {data}"
    open('logs/'+current_log,'a').write(data.replace("\033[34m",'')+"\n")
    print(str(data)+"\033[0m")



def pwarn(data, name:str="+"):
    if testing:
        return
    prefix = f"[{datetime.today().strftime('%H:%M:%S')}] \033[33m[WARN] [{name}]"
    open('logs/'+current_log,'a').write(data.replace("\033[33m",'')+"\n")
    print(prefix,end=" ")
    pp(data)
    print("\033[0m",end=" ")

def perror(data, name:str="+"):
    if testing:
        return
    prefix = f"[{datetime.today().strftime('%H:%M:%S')}] \033[31m[ERROR] [{name}]"
    open('logs/'+current_log,'a').write(data.replace("\033[31m",'')+"\n")
    print(prefix,end=" ")
    pp(data)
    print("\033[0m",end=" ")

def pinfo(data, name:str="+"):
    if testing:
        return
    prefix = f"[{datetime.today().strftime('%H:%M:%S')}] [INFO] [{name}]"
    open('logs/'+current_log,'a').write(str(data)+"\n")
    print(prefix,end=" ")
    pp(data)
    print("\033[0m",end=" ")
