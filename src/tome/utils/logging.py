from datetime import datetime
import os
from pprint import pp

current_log = ""
testing = False

def start(testing_mode: bool = False):
    '''
    Start logging

    Parameters
    ----------
    testing_mode : bool
        If it sould initialize into testing mode
    '''
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

def warn(*text, name:str="+"):
    '''
    Print a log with level 'WARN'

    Parameters
    ----------
    *text : str
        Contents of message
    name : str, optional
        Name to use in logging (default is '+')
    '''
    text = " ".join(text)
    if testing:
        return
    display = ""
    for i in text.split("\n"):
        display += f"[{datetime.today().strftime('%H:%M:%S')}] \033[33m[WARN] [{name}] {i}\033[0m\n"
    display.strip()
    open('logs/'+current_log,'a').write(display.replace("\033[33m",''))
    print(str(display)+"\033[0m",end="")

def error(*text, name:str="+"):
    '''
    Print a log with level 'ERROR'

    Parameters
    ----------
    *text : str
        Contents of message
    name : str, optional
        Name to use in logging (default is '+')
    '''
    text = " ".join(text)
    if testing:
        return
    display = ""
    for i in text.split("\n"):
        display += f"[{datetime.today().strftime('%H:%M:%S')}] \033[31m[ERROR] [{name}] {i}\033[0m\n"
    display.strip()
    open('logs/'+current_log,'a').write(display.replace("\033[31m",''))
    print(str(display)+"\033[0m",end="")

def info(*text, name:str="+"):
    '''
    Print a log with level 'INFO'

    Parameters
    ----------
    *text : str
        Contents of message
    name : str, optional
        Name to use in logging (default is '+')
    '''
    text = " ".join(text)
    if testing:
        return
    display = ""
    for i in text.split("\n"):
        display += f"[{datetime.today().strftime('%H:%M:%S')}] [INFO] [{name}] {i}\033[0m\n"
    display.strip()
    open('logs/'+current_log,'a').write(str(display))
    print(str(display)+"\033[0m",end="")

def disconnect(*text, name:str="+"):
    '''
    Print a log with level 'DISCONNECT'

    Parameters
    ----------
    *text : str
        Contents of message
    name : str, optional
        Name to use in logging (default is '+')
    '''
    text = " ".join(text)
    if testing:
        return
    display = ""
    for i in text.split("\n"):
        display = f"[{datetime.today().strftime('%H:%M:%S')}] \033[34m[DISCONNECT] [{name}] {i}\033[0m\n"
    display.strip()
    open('logs/'+current_log,'a').write(display.replace("\033[34m",''))
    print(str(display)+"\033[0m",end="")



def pwarn(*text, name:str="+"):
    '''
    PrettyPrint a log with level 'WARN'

    Parameters
    ----------
    *text : str
        Contents of message
    name : str, optional
        Name to use in logging (default is '+')
    '''
    text = " ".join(text)
    if testing:
        return
    prefix = f"[{datetime.today().strftime('%H:%M:%S')}] \033[33m[WARN] [{name}]"
    open('logs/'+current_log,'a').write(text.replace("\033[33m",'')+"\n")
    print(prefix,end=" ")
    pp(text)
    print("\033[0m",end=" ")

def perror(*text, name:str="+"):
    '''
    PrettyPrint a log with level 'ERROR'

    Parameters
    ----------
    *text : str
        Contents of message
    name : str, optional
        Name to use in logging (default is '+')
    '''
    text = " ".join(text)
    if testing:
        return
    prefix = f"[{datetime.today().strftime('%H:%M:%S')}] \033[31m[ERROR] [{name}]"
    open('logs/'+current_log,'a').write(text.replace("\033[31m",'')+"\n")
    print(prefix,end=" ")
    pp(text)
    print("\033[0m",end=" ")

def pinfo(*text, name:str="+"):
    '''
    PrettyPrint a log with level 'INFO'

    Parameters
    ----------
    *text : str
        Contents of message
    name : str, optional
        Name to use in logging (default is '+')
    '''
    text = " ".join(text)
    if testing:
        return
    prefix = f"[{datetime.today().strftime('%H:%M:%S')}] [INFO] [{name}]"
    open('logs/'+current_log,'a').write(str(text)+"\n")
    print(prefix,end=" ")
    pp(text)
    print("\033[0m",end=" ")
