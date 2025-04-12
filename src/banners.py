import pyfiglet
from random import choice

types = [
    "broadway",
    "colossal",
    "whimsy",
    "amc_aaa01",
    "bolger",
    "nvscript",
    "train",
    "ansi_shadow",
    "univers",
    "defleppard",
    "dos_rebel",
    "banner3-D",
]

def generate(text: str, font: None | str = None):
    if font == None:
        font = choice(types)
    text = pyfiglet.figlet_format(text, font=font,width=100000).strip()
    length = []
    for i in text.splitlines():
        length.append(len(i))
    length = max(length)
    return "="*length+"\n"+text+"\n"+"="*length
