import Device


class Computer(Device.Device):
    def __init__(self, ipAddress=None, torNetwork=None):
        super().__init__(ipAddress, torNetwork)
        torNetwork.computerList.append(self)
