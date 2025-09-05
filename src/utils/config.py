import toml
import os
from pprint import pp

def get(path:str, key:str="all") -> dict:
    if not path.endswith(".toml"):
        return {}
    y = toml.loads(open(os.path.join("config/",path), 'r').read())

    if key == "all":
        return y
    else:
        try:
            return y[key]
        except KeyError:
            return {}

def get_dir(path:str, key:str="all", ls=False) -> list:
    tmp = []
    for i in os.listdir(os.path.join("config/",path)):
        if ls == False:
            if os.path.isdir(os.path.join("config/",path,i)):
                tmp.append({path+"/"+i: get_dir(os.path.join(path,i),key)})
            else:
                tmp.append({path+"/"+i: get(os.path.join(path,i),key)})
        else:
            tmp.append(get(os.path.join(path,i),key))
    return tmp
