import Device
class Computer(Device.Device):
    def __init__(self, ipAddress = None, torNetwork = None):
        super().__init__(ipAddress, torNetwork)

    def sendPacket(self, packet):
        for server in self.torNetwork.serverList:
            if (server.ipAddress == packet[1]):
                server.buffer.append(packet)
                return


# packet = [srcAddr, dstAddr, identNo, "S{src2-dst2-identNo-'S2{src3-dst3-identNo-plaintextdata}'}"]

# newPacket = decrypt(arr[3]).split("-")

