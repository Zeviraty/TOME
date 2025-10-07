from . import Test

class CreationTest(Test):
    def __init__(self):
        super().__init__("Character creation test")

    def run(self) -> bool:
        return True
