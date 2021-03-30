import Device
class Computer(Device.Device):
    def __init__(self, ipAddress = None, torNetwork = None, computerList = []):
        self.ipAddress = ipAddress
        self.torNetwork = torNetwork
        self.computerList = computerList