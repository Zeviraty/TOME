from tests import Test, TestingClient
from client.mainmenu import mainmenu,login

class MainMenuTest(Test):
    def __init__(self):
        super().__init__("basicTest")

    def run(self) -> bool:
        client = TestingClient()
        login(client,"TESTING",askpassword=False)
        client.inputbuffer =["2"]
        mainmenu(client)
        if client.buffer == [' \x1b[38;5;11m\x1b[48;5;4mMain Menu:\n\x1b[0m\x1b[0m \x1b[48;5;4m\x1b[38;5;11m0\x1b[0m) \x1b[38;5;14mNew character\x1b[0m\n \x1b[48;5;4m\x1b[38;5;11m1\x1b[0m) \x1b[38;5;14mList characters\x1b[0m\n \x1b[48;5;4m\x1b[38;5;11m2\x1b[0m) \x1b[38;5;14mExit\x1b[0m\n\n']:
            return True
        return False

TESTS = [MainMenuTest]
NAME = "MainMenuTest"
