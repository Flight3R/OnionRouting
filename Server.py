import Device, Connection
class Server(Device.Device):
    def __init__(self, ipAddress = None, torNetwork = None, publicKey = None, privateKey = None):
        super().__init__(ipAddress, torNetwork, publicKey, privateKey)

    def bufferCheck(self):
        #print("srv b/c",len(self.buffer))
        while(len(self.buffer) != 0):
            packet = self.buffer.pop(0)

            try:
                connection = next(con for con in self.connectionList if con.destIdentNo == packet[2])
                # already existing connection (data to decrypt and encrypt)
                data = packet[3]  # decrypt with self.privateKey and encrypt with connection.sourceAddr.publicKey
                print("e/c from: ", packet[0], "\tto: ", connection.sourceAddr, ":\t", data)
                self.sendData(connection.sourceAddr, connection.sourceIdentNo, data)
                self.connectionList.remove(connection)
                self.connectionList.remove(connection)
            except StopIteration:
                print("aaaaa")
                # new connection (data to decrypt)
                data = packet[3].split("-")  # decrypt packet[3] with self.privateKey before split
                print("n/c from: ", packet[0], "\tto: ", data[0], ":\t", data[1])
                newIdent = packet[2]  # can be random
                self.connectionList.append(Connection.Connection(packet[0], packet[2], newIdent, data[0]))
                self.sendData(data[0], newIdent, data[1])

# packet = [srcAddr, dstAddr, identNo, "S{dst2-'S2{dst3-plaintextdata}'}"]
