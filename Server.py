import Connection
import Device


class Server(Device.Device):
    def __init__(self, name=None, ipAddress=None, torNetwork=None, publicKey=None, privateKey=None):
        super().__init__(name, ipAddress, torNetwork, publicKey, privateKey)

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)

            try:
                connection = next(filter(lambda x: x.destIdentNo == packet[2], self.connectionList))
                # already existing connection (data to decrypt and encrypt)
                data = packet[3]  # decrypt with self.privateKey and encrypt with connection.sourceAddr.publicKey
                print("at:", self, "e/c from:", packet[0], "\tto:", connection.sourceAddr, "\tdata:", data)
                self.send_data(connection.sourceAddr, connection.sourceIdentNo, data)
                self.connectionList.remove(connection)
            except StopIteration:
                # new connection (data to decrypt)
                data = packet[3].split("-")  # decrypt packet[3] with self.privateKey before split
                print("at:", self, "n/c from:", packet[0], "\tto:", data[1], "\tdata:", "-".join(data[1:]))
                newIdent = packet[2]  # can be random
                self.connectionList.append(Connection.Connection(packet[0], packet[2], newIdent, data[0]))
                self.send_data(data[0], newIdent, "-".join(data[1:]))

# packet = [srcAddr, dstAddr, identNo, "S{dst2-'S2{dst3-plaintextdata}'}"]
