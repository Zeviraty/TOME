from tests import Test

class CreationTest(Test):
    def __init__(self):
        super().__init__("basicTest")

    def run(self) -> bool:
        return True

TESTS = []
NAME = "CharacterCreation"
