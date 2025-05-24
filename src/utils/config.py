import yaml

def get(path:str, key:str="all") -> dict:
    y = yaml.safe_load(open(f"config/{path}", 'r'))

    if key == "all":
        return y
    else:
        try:
            return y[key]
        except KeyError:
            return {}
