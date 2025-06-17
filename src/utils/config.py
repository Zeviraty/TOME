import toml
import os

def get(path:str, key:str="all") -> dict:
    y = toml.loads(open(os.path.join("config/",path), 'r').read())

    if key == "all":
        return y
    else:
        try:
            return y[key]
        except KeyError:
            return {}

def get_dir(path:str, key:str="all") -> list:
    tmp = []
    for i in os.listdir(os.path.join("config/",path)):
        tmp.append(get(os.path.join(path,i),key))
    return tmp
