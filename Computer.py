import Device, Connection, random
class Computer(Device.Device):
    def __init__(self, ipAddress = None, torNetwork = None, publicKey = None, privateKey = None):
        super().__init__(ipAddress, torNetwork, publicKey, privateKey)

    def createData(self, destAddr, identNo, message):
        serverAmount = random.randint(3, len(self.torNetwork.serverList))
        serverOrder = random.sample(self.torNetwork.serverList, serverAmount)
        message = destAddr + "-" + message
        print(message)
        for server in serverOrder[::-1][:-1]:
            # now encrypt message with server.publicKey
            message = "-".join([server.ipAddress, message])

        # now encrypt message with first server's publicKey

        self.connectionList.append(Connection.Connection(None, identNo, None, destAddr))
        self.sendData(serverOrder[0].ipAddress, identNo, message)

    def bufferCheck(self):
        #print("comp b/c",len(self.buffer))
        while (len(self.buffer) != 0):
            packet = self.buffer.pop(0)
            print("comp b/c - in")
            try:
                connection = next(con for con in self.connectionList if con.destIdentNo == packet[2])
                # already existing connection (data to decrypt)
                message = packet[3] # decrypt with self.privateKey
                print("from: ", connection.destAddr, ": ", message)
                self.connectionList.remove(connection)
            except StopIteration:
                # answer to message
                print("from: ", packet[0], "\t: ", packet[3], "\tresponding...")
                self.createData(packet[0], random.randint(3000, 65535), message+"-la-respuesta-por-tu-puta-madre")


# packet = [srcAddr, dstAddr, identNo, "S{dst2-'S2{dst3-plaintextdata}'}"]

