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
        print(self, "rsa-dec", packet[3])
        data = rsa_decrypt(self.privateKey,packet[3]).split(b"/")  # decrypt packet[3] with self.privateKey before split
        nextPort = packet[2] #random.randint(4000, 65535)
        newConnection = Connection.Connection(packet[0], packet[2], nextPort, data[0].decode())
        newConnection.symmetricKeys.append(data[1])
        newConnection.initVectors.append(data[2])
        self.connectionList.append(newConnection)
        print("at:", self, "new/con from:", packet[0], "\tcreds:", b"/".join(data))

    def forward_connection(self, packet, connection):
        print('forward')
        data = Device.aes_decrypt(connection.symmetricKeys[0], connection.initVectors[0], packet[3])
        if (data == 64 * b"0"):
            self.connectionList.remove(connection)
        else:
            print('forward-send')
            self.send_data(connection.destAddr, connection.destPort, data)

        print("at:", self, "fwd/con from:", packet[0], "\tto:", connection.destAddr, "\tcreds:", data)

    def backward_connection(self, packet, connection):
        data = Device.aes_encrypt(connection.symmetricKeys[0], connection.initVectors[0], packet[3])
        self.send_data(connection.destAddr, connection.destPort, data)

        print("at:", self, "bck/con from:", packet[0], "\tto:",  connection.destAddr, "\tcreds:", data)

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)
            print('aaa')
            for conn in self.connectionList:
                if (conn.destPort == packet[2]):
                    print(self, 'forward!!')
                    self.forward_connection(packet, conn)
                    break
                elif (conn.sourcePort == packet[2]):
                    print(self, 'backward!!')
                    self.backward_connection(packet, conn)
                    break
            else:
                print(self, 'new!!')
                self.create_connection(packet)

# packet = [srcAddr, dstAddr, identNo, "S{dst2-'S2{dst3-plaintextdata}'}"]
