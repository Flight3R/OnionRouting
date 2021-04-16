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

    def handle_forward_connection(self, current_connection, raw_data):
        data = device.aes_decrypt(current_connection.symmetric_keys[0], current_connection.init_vectors[0], raw_data)
        if data == 128 * b"0":
            self.remove_connection(current_connection)
        elif current_connection.is_end_node:
            parts = data.split(self.splitter)
            number = parts[0]
            message = parts[1]
            if number != b"000":
                current_connection.data_buffer.append(message)
            else:
                unpadded_message = device.remove_padding(b"".join([data for data in current_connection.data_buffer] + [message]))
                current_connection.data_buffer = []
                self.forward_connection(current_connection, unpadded_message)
        else:
            self.forward_connection(current_connection, data)

    def handle_backward_connection(self, current_connection, raw_data):
        if current_connection.is_end_node:
            blocks = device.split_to_packets(raw_data)
            for i, block in enumerate(blocks):
                self.backward_connection(current_connection, device.prepare_number(len(blocks)-i-1) + self.splitter + block)
        else:
            self.backward_connection(current_connection, raw_data)

    def create_connection(self, packet):
        raw_data = packet[3]
        data = rsa_decrypt(self.private_key, raw_data).split(self.splitter)  # decrypt packet[3] with self.privateKey before split
        next_port = random.randint(4000, 65535)
        next_addr = data[0].decode()
        new_connection = connection.Connection(packet[0], packet[2], next_port, next_addr)
        new_connection.symmetric_keys.append(data[1])
        new_connection.init_vectors.append(data[2])
        try:
            new_connection.is_end_node = True if data[3] == b"end" else False
        except IndexError:
            pass
        self.connection_list.append(new_connection)
        device.log_write("{}:\trcv/new/con from: {}\tto: {}\tlength: {}\tdata: {}".format(self, new_connection.source_addr, new_connection.dest_addr, len(self.splitter.join(data)), self.splitter.join(data)))

    def forward_connection(self, current_connection, data):
        self.send_data(current_connection.dest_addr, current_connection.dest_port, data)
        device.log_write("{}:\tsnd/fwd/con from: {}\tto: {}\tlength: {}\tdata: {}".format(self, current_connection.source_addr, current_connection.dest_addr, len(data), data))

    def backward_connection(self, current_connection, data):
        data = device.aes_encrypt(current_connection.symmetric_keys[0], current_connection.init_vectors[0], data)
        self.send_data(current_connection.source_addr, current_connection.source_port, data)
        device.log_write("{}:\tsnd/bck/con from: {}\tto: {}\tlength: {}\tdata: {}". format(self, current_connection.dest_addr, current_connection.source_addr, len(data), data))

    def remove_connection(self, current_connection):
        device.log_write("{}:\trcv/rmv/con from: {}\tto: {}".format(self, current_connection.source_addr, current_connection.dest_addr))
        self.connection_list.remove(current_connection)

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)
            device.log_write("{}:\tnew packet: src_addr: {}\tdst_addr: {}\tdest_port: {}\tdata_length: {}\traw_data: {}"
                             .format(self, packet[0], packet[1], packet[2], len(packet[3]), packet[3]))
            try:
                current_connection = next(filter(lambda c: c.source_port == packet[2], self.connection_list))
                self.handle_forward_connection(current_connection, packet[3])
            except StopIteration:
                try:
                    current_connection = next(filter(lambda c: c.dest_port == packet[2], self.connection_list))
                    self.handle_backward_connection(current_connection, packet[3])
                except StopIteration:
                    self.create_connection(packet)

    def run(self):
        while self.run_event.is_set():
            self.buffer_check()
            sleep(0.1)
