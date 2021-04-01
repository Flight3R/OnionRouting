import Connection
import Device
import random


class Computer(Device.Device):
    def __init__(self, ipAddress = None, torNetwork = None, publicKey = None, privateKey = None):
        super().__init__(ipAddress, torNetwork, publicKey, privateKey)
        torNetwork.computerList.append(self)

    def onion_message(self, destAddr, identNo, message):
        serverAmount = random.randint(3, len(self.torNetwork.serverList))
        serverOrder = random.sample(self.torNetwork.serverList, serverAmount)
        message = destAddr + "-" + message

        for server in serverOrder[::-1][:-1]:
            # now encrypt message with server.publicKey
            message = "-".join([server.ipAddress, message])

        # now encrypt message with first server's publicKey
        print(self, "to:", destAddr, "\tvia:", serverOrder[0].ipAddress, "\tsent:", message)
        self.connectionList.append(Connection.Connection(None, None, identNo, destAddr))
        self.send_data(serverOrder[0].ipAddress, identNo, message)

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)

            try:

                connection = next(filter(lambda x: x.destIdentNo == packet[2], self.connectionList))
                # already existing connection (data to decrypt)
                message = packet[3] # decrypt with self.privateKey
                print("at:", self, "response from:", connection.destAddr, "\tmessage:", message)
                self.connectionList.remove(connection)
            except StopIteration:
                # answer to message
                print("at:", self, "message from:", packet[0], "\tmessage:", packet[3], "\tresponding...")
                self.send_data(packet[0], packet[2], packet[3]+"/la/respuesta/por/tu/puta/madre")


# packet = [srcAddr, dstAddr, identNo, "S{dst2-'S2{dst3-plaintextdata}'}"]
