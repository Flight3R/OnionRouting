import os
import random
from time import sleep
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import asymmetric
import connection
import device


def rsa_encrypt(key, data):
    encrypted = key.encrypt(
        data,
        asymmetric.padding.OAEP(
            mgf=asymmetric.padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted


class Computer(device.Device):
    def __init__(self, name=None, ip_address=None, tor_network=None):
        super().__init__(name, ip_address, tor_network)
        tor_network.computer_list.append(self)

    def connection_init(self, dest_addr):
        port = random.randint(4000, 4294967295)
        servers = random.sample(self.tor_network.server_list, 3)
        print("servers:", end="\t")
        [print(i, end="\t") for i in servers]
        print()
        new_connection = connection.Connection(None, None, port, servers[0].ip_address)

        for i in range(3):
            new_connection.symmetric_keys.append(os.urandom(16))
            new_connection.init_vectors.append(os.urandom(16))

        self.connection_list.append(new_connection)

        data = b"<<_<<".join(
            [servers[1].ip_address.encode(), new_connection.symmetric_keys[0], new_connection.init_vectors[0]])
        data = rsa_encrypt(servers[0].publicKey, data)
        self.send_data(servers[0].ip_address, port, 0, data)

        data = b"<<_<<".join(
            [servers[2].ip_address.encode(), new_connection.symmetric_keys[1], new_connection.init_vectors[1]])
        data = rsa_encrypt(servers[1].publicKey, data)
        data = device.aes_encrypt(new_connection.symmetric_keys[0], new_connection.init_vectors[0], data)
        self.send_data(servers[0].ip_address, port, 0, data)

        data = b"<<_<<".join([dest_addr.encode(), new_connection.symmetric_keys[2], new_connection.init_vectors[2]])
        data = rsa_encrypt(servers[2].publicKey, data)
        data = device.aes_encrypt(new_connection.symmetric_keys[1], new_connection.init_vectors[1], data)
        data = device.aes_encrypt(new_connection.symmetric_keys[0], new_connection.init_vectors[0], data)
        self.send_data(servers[0].ip_address, port, 0, data)

    def onion_message(self, connection, message):
        blocks = device.packets(message.encode())
        for i, block in enumerate(blocks):
            self.connection_continue(connection, len(blocks)-i-1, block)

    def connection_continue(self, connection, counter, data):
        for i in range(3)[::-1]:
            data = device.aes_encrypt(connection.symmetric_keys[i], connection.init_vectors[i], data)

        self.send_data(connection.dest_addr, connection.dest_port, counter, data)

    def connection_finalize(self, connection):
        for i in range(1, 4)[::-1]:
            data = 128 * b"0"
            for j in range(i)[::-1]:
                data = device.aes_encrypt(connection.symmetric_keys[j], connection.init_vectors[j], data)
            self.send_data(connection.dest_addr, connection.dest_port, 0, data)

        self.connection_list.remove(connection)

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)
            try:
                conn = next(filter(lambda c: c.dest_port == packet[2], self.connection_list))
                data = packet[4]
                for i in range(3):
                    data = device.aes_decrypt(conn.symmetric_keys[i], conn.init_vectors[i], data)
                if packet[3] != 0:
                    conn.data_buffer.append(data)
                else:
                    message = device.unpad(b"".join([data for data in conn.data_buffer] + [data])).decode()
                    print("{}:\tresponse from: {}\tlength: {}\tmessage: {}".format(self, conn.dest_addr, len(message), message))
                    conn.data_buffer = []

            except StopIteration:
                message = packet[4]
                print("{}:\tmessage from: {}\tlength: {}\tmessage: {}\tresponding...".format(self, packet[0], len(message), message))
                respond = b"odpowiedz na zapytanie jakas zeby byla fajnie by bylo jakby zadzialalo w koncu, totez musi miec wiecej niz 128 bitow dlatego tak duzo pisze"
                self.send_data(packet[0], packet[2], 0, message+respond)

    def run(self):
        while self.run_event.is_set():
            self.buffer_check()
            sleep(0.1)
