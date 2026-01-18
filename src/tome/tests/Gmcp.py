from tome.tests import Test, TestingClient
from tome.client.mainmenu import login

class GmcpTest(Test):
    def __init__(self):
        super().__init__("basicTest")

    def run(self) -> bool:
        client = TestingClient(bytesinbuffer=True)
        client.inputbuffer = [b'\xff\xfd\xc9', b'\xff\xfa\xc9Core.Hello{"client":"Mudlet","version":"4.19.1"}\xff\xf0', b'\xff\xfa\xc9Core.Supports.Set["Char1","Char.Skills1","Char.Items1","Room1","IRE.Rift1","IRE.Composer1","External.Discord1","Client.Media1","Char.Login1"]\xff\xf0', b'\xff\xfa\xc9External.Discord.Hello\xff\xf0']
        login(client,"admin",gmcp=True,askpassword=False)
        if client.buffer == [b'\xff\xfb\xc9']:
            return True
        else:
            return False

TESTS = [GmcpTest]
NAME = "Gmcp"
