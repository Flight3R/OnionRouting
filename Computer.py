import Connection
import Device
import random
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Computer(Device.Device):
    def __init__(self, name=None, ipAddress=None, torNetwork=None):
        super().__init__(name, ipAddress, torNetwork)
        torNetwork.computerList.append(self)

    def onion_message(self, destAddr, identNo, message):
        serverOrder = random.sample(self.torNetwork.serverList, 3)
        message = destAddr + "-" + message

        for server in serverOrder[::-1][:-1]:
            # now encrypt message with server.publicKey
            #print("msgtype:", type(message))
            bytes = message.encode()
            print('b:', bytes)
            #print("type:", type(bytes))
            encryptedBytes = server.publicKey.encrypt(
                bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            print("e/b:", encryptedBytes)
            message = str(encryptedBytes)
            #print("m:", message)
            #message = "-".join([server.ipAddress, message])
            #print("j/m:", message)

        # now encrypt message with first server's publicKey
        bytes = message.encode()
        encryptedBytes = serverOrder[0].publicKey.encrypt(
            bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        message = str(encryptedBytes)
        print(self, "to:", destAddr, "\tvia:", serverOrder[0].ipAddress, "\tsent:", message)
        self.connectionList.append(Connection.Connection(None, None, identNo, destAddr))
        self.send_data(serverOrder[0].ipAddress, identNo, message)

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)

            try:
                connection = next(filter(lambda x: x.destIdentNo == packet[2], self.connectionList))
                # already existing connection (data to decrypt)
                encryptedBytes = packet[3].encode()
                bytes = self.privateKey.decrypt(
                    encryptedBytes,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                message = str(bytes)
                #message = packet[3]  # decrypt with self.privateKey
                print("at:", self, "response from:", connection.destAddr, "\tmessage:", message)
                self.connectionList.remove(connection)
            except StopIteration:
                # answer to message
                print("at:", self, "message from:", packet[0], "\tmessage:", packet[3], "\tresponding...")
                self.send_data(packet[0], packet[2], packet[3] + "/la/respuesta/por/tu/puta/madre")

# packet = [srcAddr, dstAddr, identNo, "S{dst2-'S2{dst3-plaintextdata}'}"]
