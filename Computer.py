from cryptography.hazmat.primitives import padding
import Connection
import Device
import random
import os
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


    def onion_message(self, destAddr, identNo, message):
        serverOrder = random.sample(self.torNetwork.serverList, 3)
        message = destAddr + "-" + message

    def connection_init(self, destAddr):
        port = random.randint(4000, 4294967295)
        servers = random.sample(self.torNetwork.serverList, 3)
        print("servers:", end="\t")
        [print(i, end="\t") for i in servers]
        print()
        newConnection = Connection.Connection(None, None, port, servers[0].ipAddress)


        for i in range(3):
            newConnection.symmetricKeys.append(os.urandom(16))
            newConnection.initVectors.append(os.urandom(16))

        self.connectionList.append(newConnection)

        data = b"<<_<<".join([servers[1].ipAddress.encode(), newConnection.symmetricKeys[0], newConnection.initVectors[0]])
        data = rsa_encrypt(servers[0].publicKey, data)
        self.send_data(servers[0].ipAddress, port, data)

        data = b"<<_<<".join([servers[2].ipAddress.encode(), newConnection.symmetricKeys[1], newConnection.initVectors[1]])
        data = rsa_encrypt(servers[1].publicKey, data)
        data = Device.aes_encrypt(newConnection.symmetricKeys[0], newConnection.initVectors[0], data)
        self.send_data(servers[0].ipAddress, port, data)

        data = b"<<_<<".join([destAddr.encode(), newConnection.symmetricKeys[2], newConnection.initVectors[2]])
        data = rsa_encrypt(servers[2].publicKey, data)
        data = Device.aes_encrypt(newConnection.symmetricKeys[1], newConnection.initVectors[1], data)
        data = Device.aes_encrypt(newConnection.symmetricKeys[0], newConnection.initVectors[0], data)
        self.send_data(servers[0].ipAddress, port, data)

    def connection_continue(self, connection, data):
        data = data.encode()
        for i in range(3)[::-1]:
            data = Device.aes_encrypt(connection.symmetricKeys[i], connection.initVectors[i], data)

        self.send_data(connection.destAddr, connection.destPort, data)

    def connection_finalize(self, connection):
        for i in range(1,4)[::-1]:
            data = 512 * b"0"
            for j in range(i)[::-1]:
                data = Device.aes_encrypt(connection.symmetricKeys[j], connection.initVectors[j], data)
            self.send_data(connection.destAddr, connection.destPort, data)

        self.connectionList.remove(connection)

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
                conn = next(filter(lambda c: c.destPort == packet[2], self.connectionList))
                data = packet[3]
                for i in range(3):
                    data = Device.aes_decrypt(conn.symmetricKeys[i], conn.initVectors[i], data)
                print("at:", self, "response from:", conn.destAddr, "\tlength:", len(data.decode()), "\tmessage:", data.decode())
            except StopIteration:
                print("at:", self, "message from:", packet[0], "\tlength:", len(packet[3].decode()), "\tmessage:", packet[3].decode(), "\tresponding...")
                self.send_data(packet[0], packet[2], packet[3] + b"-la-respuesta-por-tu-puta-madre")
