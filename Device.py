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
    def __init__(self, ipAddress = None, torNetwork = None, publicKey = None, privateKey = None):
        self.ipAddress = ipAddress
        self.torNetwork = torNetwork
        self.publicKey = publicKey
        self.privateKey = privateKey
        self.connectionList = []
        self.buffer = []

    def sendData(self, destAddr, identNo, data):
        packet = [self.ipAddress, destAddr, identNo, data]
        for host in self.torNetwork.serverList + self.torNetwork.computerList:
            if destAddr == host.ipAddress:
                host.buffer.append(packet)
                break


    def __str__(self):
        return self.ipAddress