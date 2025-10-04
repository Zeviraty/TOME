class CharLenError(Exception):
    def __init__(self,len) -> None:
        super().__init__(f"Char cant be longer than 1 is {len}.")

class OutsideOfMapBoundsException(Exception) :
    def __init__(self,x,y) -> None:
        super().__init__(f"Attempted to place object or Tile outside of the specified map: {x},{y}")

class ColorCodeError(Exception):
    def __init__(self,color_code) -> None:
        if color_code < 0:
            super().__init__(f"Color code is negative: {color_code}")
        elif color_code > 255:
            super().__init__(f"Color code is above 255: {color_code}")

class Color:
    def __init__(self,color_code:int) -> None:
        if color_code < -1 or color_code > 255:
            raise ColorCodeError(color_code)
        self.color_code = color_code

    def bg(self) -> str:
        if self.color_code == -1:
            return ""
        return f"\x1b[48;5;{self.color_code}m"

    def fg(self) -> str:
        if self.color_code == -1:
            return ""
        return f"\x1b[38;5;{self.color_code}m"

    def apply(self, text: str = "", bg=False, reset=True) -> str:
        color = self.bg() if bg else self.fg()
        if reset:
            return f"{color}{text}\x1b[0m"
        else:
            return f"{color}{text}"

RED = Color(9)
DARK_RED = Color(1)

GREEN = Color(10)
DARK_GREEN = Color(2)

YELLOW = Color(11)
DARK_YELLOW = Color(3)

BLUE = Color(12)
DARK_BLUE = Color(4)

LIGHT_PURPLE = Color(13)
MAGENTA = LIGHT_PURPLE
PINK = MAGENTA
PURPLE = Color(5)

CYAN = Color(14)
DARK_CYAN = Color(6)

GRAY = Color(7)
DARK_GRAY = Color(8)

WHITE = Color(15)
BLACK = Color(0)

RESET = "\x1b[0m"
