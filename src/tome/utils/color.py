class CharLenError(Exception):
    '''
    Raised when a char is longer than 1 character
    '''
    def __init__(self,len) -> None:
        super().__init__(f"Char cant be longer than 1 is {len}.")

class OutsideOfMapBoundsException(Exception) :
    '''
    Raised if it is tried to place an object or tile outside of the map
    '''
    def __init__(self,x,y) -> None:
        super().__init__(f"Attempted to place object or Tile outside of the specified map: {x},{y}")

class ColorCodeError(Exception):
    '''
    If colorcode is not valid
    '''
    def __init__(self,color_code) -> None:
        if color_code < 0:
            super().__init__(f"Color code is negative: {color_code}")
        elif color_code > 255:
            super().__init__(f"Color code is above 255: {color_code}")

class Color:
    '''
    Color class
    '''
    def __init__(self,color_code:int) -> None:
        '''
        Initialize a color

        Parameters
        ----------
        color_code : int
            Color code

        Raises
        ------
        ColorCodeError:
            Raised if color code is invalid 
        '''
        if color_code < -1 or color_code > 255:
            raise ColorCodeError(color_code)
        self.color_code = color_code

    def bg(self) -> str:
        '''
        Apply self as background color to text

        Returns
        -------
        str
            Colored text
        '''
        if self.color_code == -1:
            return ""
        return f"\x1b[48;5;{self.color_code}m"

    def fg(self) -> str:
        '''
        Apply self as foreground color to text

        Returns
        -------
        str
            Colored text
        '''
        if self.color_code == -1:
            return ""
        return f"\x1b[38;5;{self.color_code}m"

    def apply(self, text: str = "", bg: bool = False, reset: bool = True) -> str:
        '''
        Apply self to text

        Parameters
        ----------
        text : str, optional
            Text to color (default is '')
        bg : bool, optional
            If background should be colored (default is False)
        reset : bool, optional
            Whether the reset code should be added at the end

        Returns
        -------
        str
            Colored text
        '''
        color = self.bg() if bg else self.fg()
        if reset:
            return f"{color}{text}\x1b[0m"
        else:
            return f"{color}{text}"

def apply(fg:Color | None = None,bg: Color | None = None,text: str ="") -> str:
    '''
    Applies a color to text

    Parameters
    ----------
    fg : Color | None
        Foreground color
    bg : Color | None
        Background color
    text : str, optional
        Text to color (default is '')

    Returns
    -------
    str
        The colored text
    '''
    if fg is None and bg is None:
        return text
    elif fg is None and not bg is None:
        return bg.apply(text,True)
    elif not fg is None and not bg is None:
        return bg.apply(fg.apply(text),True)
    else:
        return text

class Char:
    '''
    Class representing a singular character
    '''
    def __init__(self,text:str = "", fg: Color=Color(232), bg: Color=Color(-1)):
        '''
        Initializes a Char class

        Parameters
        ----------
        text : str, optional
            The text of the character, must not be longer than 1 character (default is '')
        fg : Color, optional
            Foreground color of character (default is Color(232))
        bg : Color, optional
            Background color of character (default is Color(-1))

        Raises
        ------
        CharLenError:
            Raised if the length of text is more than 1
        '''
        if len(text) != 1:
            raise CharLenError(len(text))
        self.text = text
        self.fg = fg
        self.bg = bg

    def __repr__(self):
        '''
        Represents the character with color applied
        '''
        return apply(self.fg,self.bg,self.text) + "\033[0m"

    def dump(self):
        '''
        Gets a json version of the character
        '''
        return {"text": self.text,
                "fg": self.fg.__dict__,
                "bg": self.bg.__dict__
                }

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
