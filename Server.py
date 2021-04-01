import Device, Connection
class Server(Device.Device):
    def __init__(self, ipAddress = None, torNetwork = None, publicKey = None, privateKey = None, connectionList = []):
        super().__init__(ipAddress, torNetwork)
        self.publicKey  = publicKey
        self.privateKey = privateKey
        self.connectionList = connectionList

    

