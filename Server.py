import Connection
import Device
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import random

def rsa_decrypt(key, encrypted):
    data = key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return data

class Server(Device.Device):
    def __init__(self, name=None, ipAddress=None, torNetwork=None):
        super().__init__(name, ipAddress, torNetwork)

    def create_connection(self, packet):
        data = rsa_decrypt(self.privateKey,packet[3]).split(b"<<_<<")  # decrypt packet[3] with self.privateKey before split
        nextPort = random.randint(4000, 4294967295)
        newConnection = Connection.Connection(packet[0], packet[2], nextPort, data[0].decode())
        newConnection.symmetricKeys.append(data[1])
        newConnection.initVectors.append(data[2])
        self.connectionList.append(newConnection)
        print(self, "\b:\tnew/con from:", newConnection.sourceAddr, "\tto:", newConnection.destAddr, "\tlength:", len(b"<<_<<".join(data)), "\tdata:", b"<<_<<".join(data))

    def forward_connection(self, packet, connection):
        data = Device.aes_decrypt(connection.symmetricKeys[0], connection.initVectors[0], packet[3])
        if data == 128 * b"0":
            print(self, "\b:\trem/con from:", connection.sourceAddr, "\tto:", connection.destAddr)
            self.connectionList.remove(connection)
        else:
            self.send_data(connection.destAddr, connection.destPort, data)
            print(self, "\b:\tfwd/con from:", packet[0], "\tto:", connection.destAddr, "\tlength:", len(data), "\tdata:", data)

    def backward_connection(self, packet, connection):
        data = Device.aes_encrypt(connection.symmetricKeys[0], connection.initVectors[0], packet[3])
        self.send_data(connection.sourceAddr, connection.sourcePort, data)
        print(self, "\b:\tbck/con from:", packet[0], "\tto:",  connection.sourceAddr, "\tlength:", len(data), "\tdata:", data)

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)
            try:
                conn = next(filter(lambda c: c.sourcePort == packet[2], self.connectionList))
                self.forward_connection(packet, conn)
            except StopIteration:
                try:
                    conn = next(filter(lambda c: c.destPort == packet[2], self.connectionList))
                    self.backward_connection(packet, conn)
                except StopIteration:
                    self.create_connection(packet)
