import Device, Connection
class Server(Device.Device):
    def __init__(self, ipAddress = None, torNetwork = None, publicKey = None, privateKey = None, connectionList = []):
        super().__init__(ipAddress, torNetwork)
        self.publicKey  = publicKey
        self.privateKey = privateKey
        self.connectionList = connectionList
        self.buffer = []



    def bufferCheck(self):
        while(len(self.buffer != 0)):
            packet = self.buffer.pop(0)

            # already existing connection (data to encrypt)
            for connection in self.connectionList:
                if (packet[2] == connection.identNo and packet[0] == connection.destAddr):
                    # wyslij tu: connection.sourceaddrAddr
                    toRemove = connection
                    break
            else:
                self.connectionList.remove(toRemove)

                # new connection (data to decrypt)
                data = arr[3].split("-") # decrypt
                connection = Connection()




# packet = [srcAddr, dstAddr, identNo, "S{src2-dst2-identNo-'S2{src3-dst3-identNo-plaintextdata}'}"]

# newPacket = decrypt(arr[3]).split("-")
