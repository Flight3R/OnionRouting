import random
from time import sleep
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import connection
import device


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


class Server(device.Device):
    def __init__(self, name=None, ip_address=None, tor_network=None):
        super().__init__(name, ip_address, tor_network)

    def create_connection(self, packet):
        data = rsa_decrypt(self.private_key, packet[4]).split(b'<<_<<')  # decrypt packet[3] with self.privateKey before split
        next_port = random.randint(4000, 4294967295)
        next_addr = data[0].decode()
        new_connection = connection.Connection(packet[0], packet[2], next_port, next_addr)
        new_connection.symmetric_keys.append(data[1])
        new_connection.init_vectors.append(data[2])
        if any(next_addr == host.ip_address for host in self.tor_network.computer_list):
            new_connection.is_end_node = True
        self.connection_list.append(new_connection)
        device.log_write('{}:\tnew/con from: {}\tto: {}\tlength: {}\tdata: {}'.format(self, new_connection.source_addr, new_connection.dest_addr, len(b'<<_<<'.join(data)), b'<<_<<'.join(data)))

    def forward_connection(self, connection, counter, data_list):
        message = b''
        for block in data_list:
            part = device.aes_decrypt(connection.symmetric_keys[0], connection.init_vectors[0], block)
            if part == 128 * b'0':
                device.log_write('{}:\trem/con from: {}\tto: {}'.format(self, connection.source_addr, connection.dest_addr))
                self.connection_list.remove(connection)
                break
            message += device.remove_padding(part)
        else:
            self.send_data(connection.dest_addr, connection.dest_port, counter, message)
            device.log_write('{}:\tfwd/con from: {}\tto: {}\tlength: {}\tdata: {}'.format(self, connection.source_addr, connection.dest_addr, len(message), message))

    def backward_connection(self, connection, counter, data):
        data = device.aes_encrypt(connection.symmetric_keys[0], connection.init_vectors[0], data)
        self.send_data(connection.source_addr, connection.source_port, counter, data)
        device.log_write('{}:\tbck/con from: {}\tto: {}\tlength: {}\tdata: {}'. format(self, connection.dest_addr, connection.source_addr, len(data), data))

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)
            try:
                conn = next(filter(lambda c: c.source_port == packet[2], self.connection_list))
                if not conn.is_end_node:
                    self.forward_connection(conn, packet[3], [packet[4]])
                elif packet[3] != 0:
                    conn.data_buffer.append(packet[4])
                else:
                    self.forward_connection(conn, 0, conn.data_buffer + [packet[4]])
                    conn.data_buffer = []
            except StopIteration:
                try:
                    conn = next(filter(lambda c: c.dest_port == packet[2], self.connection_list))
                    if not conn.is_end_node:
                        self.backward_connection(conn, packet[3], packet[4])
                    else:
                        blocks = device.packets(packet[4])
                        for i, block in enumerate(blocks):
                            self.backward_connection(conn, len(blocks)-i-1, block)
                except StopIteration:
                    self.create_connection(packet)

    def run(self):
        while self.run_event.is_set():
            self.buffer_check()
            sleep(0.1)
