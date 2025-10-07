# Importing and running tests
from .CharacterCreation import CreationTest
from .MainMenu import MainMenuTest
from .Gmcp import GmcpTest
from utils.logging import start
import os
os.chdir("..")

tests = [CreationTest, MainMenuTest, GmcpTest]
failed = 0
for test in tests:
    test_class = test()
    print(f"Executing {test_class.name}... ",end="")
    status = test_class.run()
    if status == True:
        print("\x1b[32mOk\x1b[0m")
    else:
        print("\x1b[31mFailed\x1b[0m")
        failed = 1

exit(failed)
