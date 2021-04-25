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
        port = random.randint(4000, 65535)
        servers = random.sample(self.tor_network.server_list, 3)
        print("servers:", end="\t")
        [print(i, end="\t") for i in servers]
        print()
        new_connection = connection.Connection(servers[0].ip_address, port, None, dest_addr)

        # generate symmetric keys and initialization vectors
        for _ in range(3):
            new_connection.symmetric_keys.append(os.urandom(16))
            new_connection.init_vectors.append(os.urandom(16))

        self.connection_list.append(new_connection)

        # initialize connection with first server
        data = self.splitter.join(
            [servers[1].ip_address.encode(), new_connection.symmetric_keys[0], new_connection.init_vectors[0]])
        data = rsa_encrypt(servers[0].public_key, data)
        self.send_data(servers[0].ip_address, port, data)

        # initialize connection with second server
        data = self.splitter.join(
            [servers[2].ip_address.encode(), new_connection.symmetric_keys[1], new_connection.init_vectors[1]])
        data = rsa_encrypt(servers[1].public_key, data)
        data = device.aes_encrypt(new_connection.symmetric_keys[0], new_connection.init_vectors[0], data)
        self.send_data(servers[0].ip_address, port, data)

        # initialize connection with third server
        data = self.splitter.join(
            [dest_addr.encode(), new_connection.symmetric_keys[2], new_connection.init_vectors[2], b"end"])
        data = rsa_encrypt(servers[2].public_key, data)
        data = device.aes_encrypt(new_connection.symmetric_keys[1], new_connection.init_vectors[1], data)
        data = device.aes_encrypt(new_connection.symmetric_keys[0], new_connection.init_vectors[0], data)
        self.send_data(servers[0].ip_address, port, data)

    def onion_message(self, current_connection, message):
        blocks = device.split_to_packets(message.encode())
        for i, block in enumerate(blocks):
            self.connection_continue(current_connection,
                                     device.prepare_number(len(blocks) - i - 1) + self.splitter + block)

    def connection_continue(self, current_connection, data):
        for i in range(3)[::-1]:
            data = device.aes_encrypt(current_connection.symmetric_keys[i], current_connection.init_vectors[i], data)
        self.send_data(current_connection.source_addr, current_connection.source_port, data)

    def connection_finalize(self, current_connection):
        for i in range(1, 4)[::-1]:
            data = 128 * b"0"
            for j in range(i)[::-1]:
                data = device.aes_encrypt(current_connection.symmetric_keys[j], current_connection.init_vectors[j],
                                          data)
            self.send_data(current_connection.source_addr, current_connection.source_port, data)
        self.connection_list.remove(current_connection)

    def handle_self_connection(self, current_connection, raw_data):
        for i in range(3):
            raw_data = device.aes_decrypt(current_connection.symmetric_keys[i], current_connection.init_vectors[i],
                                          raw_data)
        data = raw_data.split(self.splitter)
        number = data[0]
        message = data[1]
        if number != b"000":
            current_connection.data_buffer.append(message)
        else:
            unpadded_message = device.remove_padding(
                b"".join([data for data in current_connection.data_buffer] + [message])).decode()
            self.log_write("console", "{}:\treceived response from: {}\tlength: {}\tmessage: {}"
                           .format(self, current_connection.dest_addr, len(unpadded_message), unpadded_message))
            current_connection.data_buffer = []

    def handle_new_connection(self, packet):
        message = packet[3]
        self.log_write("console", "{}:\treceived message from: {}\tlength: {}\tmessage: {}\tresponding..."
                       .format(self, packet[0], len(message), message))
        # write from keyboard
        response = b" */*/* odpowiedz na zapytanie jakas zeby byla fajnie by bylo jakby zadzialalo w koncu, totez musi miec wiecej niz 128 bitow dlatego tak duzo pisze"
        self.send_data(packet[0], packet[2], response)

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)
            self.log_write("sniff",
                           "{}:\tnew packet: src_addr: {}\tdst_addr: {}\tdest_port: {}\tdata_length: {}\traw_data: {}"
                           .format(self, packet[0], packet[1], packet[2], len(packet[3]), packet[3]))
            try:
                current_connection = next(filter(lambda c: c.source_port == packet[2], self.connection_list))
                self.handle_self_connection(current_connection, packet[3])

            except StopIteration:
                self.handle_new_connection(packet)

    def execute_command(self, line):
        commands = iter(line.split(" "))
        current = next(commands)
        if current == "show":
            return self.show_command(commands)
        if current == "onion":
            return self.onion_command(commands)
        if current == "message":
            return self.message_command(commands)
        return "Unknown command! Available: show, onion, message\n"

    def onion_command(self, commands):
        try:
            current = next(commands)
            if current == "init":
                return self.init_command(commands)
            if current == "message":
                return self.message_command(commands)
            if current == "finalize":
                return self.finalize_command(commands)
            return "Unknown command! Available: init, message, finalize\n"
        except StopIteration:
            pass

    def init_command(self, commands):
        try:
            address = next(commands)
            self.connection_init(address)
            return "Initialization sent.\n"
        except StopIteration:
            return "Destination address needed!\n"

    def message_command(self, commands):
        try:
            number = next(commands)
            message = next(commands)
        except StopIteration:
            return "Connection number and message needed!\n"
        try:
            conn = self.connection_list[int(number)]
            self.onion_message(conn, message)
            return "Message sent.\n"
        except ValueError or IndexError:
            return "No such connection!\n"

    def finalize_command(self, commands):
        try:
            number = next(commands)
        except StopIteration:
            return "Connection number needed!\n"
        try:
            conn = self.connection_list[int(number)]
            self.connection_finalize(conn)
            return "Connection finalized.\n"
        except ValueError or IndexError:
            return "No such connection!\n"

    def run(self):
        while self.run_event.is_set():
            self.buffer_check()
            sleep(0.1)
