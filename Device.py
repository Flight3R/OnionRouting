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
            print(destAddr, host.ipAddress)
            if destAddr == host.ipAddress:
                host.buffer.append(packet)
                print('b')
            return


