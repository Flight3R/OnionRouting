import Connection
import Device
import random
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def rsa_encrypt(key, data):
    encrypted = key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted



class Computer(Device.Device):
    def __init__(self, name=None, ipAddress=None, torNetwork=None):
        super().__init__(name, ipAddress, torNetwork)
        torNetwork.computerList.append(self)

    def connection_init(self, destAddr):
        port = random.randint(4000, 65535)
        servers = random.sample(self.torNetwork.serverList, 3)
        [print(i) for i in servers]
        newConnection = Connection.Connection(None, None, port, servers[0].ipAddress)

        for i in range(3):
            newConnection.symmetricKeys.append(os.urandom(32))
            newConnection.initVectors.append(os.urandom(16))

        self.connectionList.append(newConnection)

        data = b"/".join([servers[1].ipAddress.encode(), newConnection.symmetricKeys[0], newConnection.initVectors[0]])
        data = rsa_encrypt(servers[0].publicKey, data)
        self.send_data(servers[0].ipAddress, port, data)

        data = b"/".join([servers[2].ipAddress.encode(), newConnection.symmetricKeys[1], newConnection.initVectors[1]])
        data = rsa_encrypt(servers[1].publicKey, data)
        data = Device.aes_encrypt(newConnection.symmetricKeys[0], newConnection.initVectors[0], data)
        self.send_data(servers[0].ipAddress, port, data)

        data = b"/".join([destAddr.encode(), newConnection.symmetricKeys[2], newConnection.initVectors[2]])
        data = rsa_encrypt(servers[2].publicKey, data)
        data = Device.aes_encrypt(newConnection.symmetricKeys[1], newConnection.initVectors[1], data)
        data = Device.aes_encrypt(newConnection.symmetricKeys[0], newConnection.initVectors[0], data)
        self.send_data(servers[0].ipAddress, port, data)

    def connection_continue(self, connection, data):
        for i in range(3)[::-1]:
            data = Device.aes_encrypt(connection.symmetricKeys[i], connection.initVectors[i], data)

        self.send_data(connection.destAddr, connection.destPort, data)

    def connection_finalize(self, connection):
        for i in range(1,4)[::-1]:
            data = 512 * b"0"
            for j in range(i)[::-1]:
                data = Device.aes_encrypt(connection.symmetricKeys[j], connection.initVector[j], data)
            self.send_data(connection.destAddr, connection.destPort, data)

        self.connectionList.remove(connection)

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

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)

            try:
                connection = next(filter(lambda x: x.destPort == packet[2], self.connectionList))
                # already existing connection (data to decrypt)

                message = packet[3]  # decrypt with self.privateKey
                print("at:", self, "response from:", connection.destAddr, "\tmessage:", message)
                self.connectionList.remove(connection)
            except StopIteration:
                # answer to message
                print("at:", self, "message from:", packet[0], "\tmessage:", packet[3], "\tresponding...")
                self.send_data(packet[0], packet[2], packet[3] + "/la/respuesta/por/tu/puta/madre")

# packet = [srcAddr, dstAddr, identNo, "S{dst2-'S2{dst3-plaintextdata}'}"]
