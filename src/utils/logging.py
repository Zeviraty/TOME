def warn(text:str, name:str="+"):
    print(f"\033[33m[WARN][{name}] {text}\033[0m")

def error(text:str, name:str="+"):
    print(f"\033[31m[ERROR][{name}] {text}\033[0m")

def info(text:str, name:str="+"):
    print(f"[INFO][{name}] {text}\033[0m")

def disconnect(text:str, name:str="+"):
    print(f"\033[34m[DISCONNECT][{name}] {text}\033[0m")
