import zte as term
import time

def main():
    term.echo(False)
    term.raw(True)
    term.mouse(True)
    term.hide()
    term.cs()
    term.border()
    while True:
        ev = term.getmouse(True)
        if type(ev) == dict:
            key = None
        else:
            key = ev
            ev = None
        if key == 'q':
            break
        elif ev:
            if ev["pressed"] == 1:
                x,y = ev["x"],ev["y"]
                if x == 1 or x == term.wh()[0] or y == 1 or y == term.wh()[1]:
                    pass
                elif ev["button"] == 1:
                    term.ip(x,y,"A")
                elif ev["button"] == 2:
                    term.ip(x,y," ")

        time.sleep(0.01)

if __name__ == "__main__":
    main()
