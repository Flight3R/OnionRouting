from cryptography.hazmat.primitives import padding
import Connection
import Device
import random


class Computer(Device.Device):
    def __init__(self, name=None, ipAddress=None, torNetwork=None, publicKey=None, privateKey=None):
        super().__init__(name, ipAddress, torNetwork, publicKey, privateKey)
        torNetwork.computerList.append(self)

    def onion_message(self, destAddr, identNo, message):
        serverOrder = random.sample(self.torNetwork.serverList, 3)
        message = destAddr + "-" + message

        for server in serverOrder[::-1][:-1]:
            # now encrypt message with server.publicKey
            message = "-".join([server.ipAddress, message])

        # now encrypt message with first server's publicKey
        print(self, "to:", destAddr, "\tvia:", serverOrder[0].ipAddress, "\tsent:", message)
        self.connectionList.append(Connection.Connection(None, None, identNo, destAddr))
        self.send_data(serverOrder[0].ipAddress, identNo, message)

    def packets(self, message=""):
        bytes_message = message.encode('utf-8')
        padder = padding.PKCS7(1024).padder()
        padded_data = padder.update(bytes_message)
        padded_data += padder.finalize()
        data_list = []
        print(padded_data[512])
        for i in range(len(padded_data) // 128):
            k = 128 * i
            data_list.append(padded_data[k:k + 128])
        return data_list

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)

            try:

                connection = next(filter(lambda x: x.destIdentNo == packet[2], self.connectionList))
                # already existing connection (data to decrypt)
                message = packet[3]  # decrypt with self.privateKey
                print("at:", self, "response from:", connection.destAddr, "\tmessage:", message)
                self.connectionList.remove(connection)
            except StopIteration:
                # answer to message
                print("at:", self, "message from:", packet[0], "\tmessage:", packet[3], "\tresponding...")
                self.send_data(packet[0], packet[2], packet[3] + "/la/respuesta/por/tu/puta/madre")

# packet = [srcAddr, dstAddr, identNo, "S{dst2-'S2{dst3-plaintextdata}'}"]
