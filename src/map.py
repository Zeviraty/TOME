class CharLenError(Exception):
    def __init__(self,len):
        super().__init__(f"Char cant be longer than 1 is {len}.")

class ColorCodeError(Exception):
    def __init__(self,color_code):
        if color_code < 0:
            super().__init__(f"Color code is negative: {color_code}")
        elif color_code > 255:
            super().__init__(f"Color code is above 255: {color_code}")

class Color:
    def __init__(self,color_code:int):
        if color_code < 0 or color_code > 255:
            raise ColorCodeError(color_code)
        self.color_code = color_code

    def bg(self):
        return f"\u001b[48;5;{self.color_code}m"

    def fg(self):
        return f"\u001b[38;5;{self.color_code}m"

    def apply(self,text:str=" ",bg=False):
        if bg == True:
            return self.bg() + text + '\x1b[48;5;0m\x1b[38;5;15m'
        else:
            return self.fg() + text + '\x1b[48;5;0m\x1b[38;5;15m'

class Char:
    def __init__(self,text:str = "", fg: Color=Color(232), bg: Color=Color(255)):
        if len(text) != 1:
            raise CharLenError(len(text))
        self.text = text
        self.fg = bg
        self.bg = fg

    def __repr__(self):
        return self.bg.apply(self.fg.apply(self.text,True)) + "\033[0m"

class Tile:
    def __init__(self,passable = False, char:Char=Char("#")):
        self.passable = passable
        self.char = char

    def __repr__(self):
        return str(self.char)

class Map:
    def __init__(self,x:int,y:int,base:Tile):
        self.array = [[base]*x]*y
        print(self.array)
