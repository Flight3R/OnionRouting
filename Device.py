import TorNetwork


def test_address(testAddress="", testNetwork=None):
    addresses = testAddress.split(".")
    for i in addresses:
        if int(i) < 0 or int(i) > 255:
            print("Invalid address")
            return "0.0.0.0"
    for i in testNetwork.computerList:
        if i.ipAddress == testAddress:
            print("Reused address")
            return "0.0.0.0"
    for i in testNetwork.serverList:
        if i.ipAddress == testAddress:
            print("Reused address")
            return "0.0.0.0"
    return testAddress


class Device:
    def __init__(self, ipAddress=None, torNetwork=None):
        self.ipAddress = test_address(ipAddress, torNetwork)
        self.torNetwork = torNetwork
