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
        data = rsa_decrypt(self.privateKey,packet[4]).split(b"<<_<<")  # decrypt packet[3] with self.privateKey before split
        nextPort = random.randint(4000, 4294967295)
        nextAddr = data[0].decode()
        newConnection = Connection.Connection(packet[0], packet[2], nextPort, nextAddr)
        newConnection.symmetricKeys.append(data[1])
        newConnection.initVectors.append(data[2])
        if any(nextAddr == host.ipAddress for host in self.torNetwork.computerList):
            newConnection.isEndNone = True
        self.connectionList.append(newConnection)
        print("{}:\tnew/con from: {}\tto: {}\tlength: {}\tdata: {}".format(self, newConnection.sourceAddr, newConnection.destAddr, len(b"<<_<<".join(data)), b"<<_<<".join(data)))

    def forward_connection(self, dataList, connection):
        message = b""
        for block in dataList:
            part = Device.aes_decrypt(connection.symmetricKeys[0], connection.initVectors[0], block)
            message += Device.unpadder(part)

        if message == 128 * b"0":
            print("{}:\trem/con from: {}\tto: {}".format(self, connection.sourceAddr, connection.destAddr))
            self.connectionList.remove(connection)
        else:
            self.send_data(connection.destAddr, connection.destPort, 0, message)
            print("{}:\tfwd/con from: {}\tto: {}\tlength: {}\tdata: {}".format(self, connection.sourceAddr, connection.destAddr, len(message), message))

    def backward_connection(self, data, connection):
        blocks = Device.packets(data)
        for i, block in enumerate(blocks):
            data = Device.aes_encrypt(connection.symmetricKeys[0], connection.initVectors[0], block)
            self.send_data(connection.sourceAddr, connection.sourcePort, len(blocks)-i-1, data)
            print("{}:\tbck/con from: {}\tto: {}\tlength: {}\tdata: {}". format(self, connection.destAddr, connection.sourceAddr, len(data), data))

    def buffer_check(self):
            while len(self.buffer) != 0:
                packet = self.buffer.pop(0)
                try:
                    conn = next(filter(lambda c: c.sourcePort == packet[2], self.connectionList))
                    if not conn.isEndNode:
                        self.forward_connection([packet[4]], conn)
                    elif packet[3] != 0:
                        conn.dataBuffer.append(packet[4])
                    else:
                        self.forward_connection(conn.dataBuffer + [packet[4]], conn)
                except StopIteration:
                    try:
                        conn = next(filter(lambda c: c.destPort == packet[2], self.connectionList))
                        self.backward_connection(packet[4], conn)
                    except StopIteration:
                        self.create_connection(packet)
