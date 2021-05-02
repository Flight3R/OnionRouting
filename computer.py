import os
import random
from time import time
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
    def __init__(self, name, ip_address, tor_network):
        super().__init__(name, ip_address, tor_network)
        tor_network.computer_list.append(self)

    def connection_init(self, dest_addr):
        port = random.randint(4000, 65535)
        servers = random.sample(self.tor_network.server_list, 3)
        print("servers:", end="\t")
        [print(i, end="\t") for i in servers]
        print()
        new_connection = connection.Connection(servers[0].ip_address, port, None, dest_addr)

        """ generate symmetric keys and initialization vectors """
        for _ in range(3):
            new_connection.symmetric_keys.append(os.urandom(16))
            new_connection.init_vectors.append(os.urandom(16))

        self.connection_list.append(new_connection)

        """ initialize connection with first server """
        data = self.splitter.join(
            [servers[1].ip_address.encode(), new_connection.symmetric_keys[0], new_connection.init_vectors[0]])
        data = rsa_encrypt(servers[0].public_key, data)
        self.tor_network.send_data(self.ip_address, servers[0].ip_address, port, data)

        """ initialize connection with second server """
        data = self.splitter.join(
            [servers[2].ip_address.encode(), new_connection.symmetric_keys[1], new_connection.init_vectors[1]])
        data = rsa_encrypt(servers[1].public_key, data)
        data = device.aes_encrypt(new_connection.symmetric_keys[0], new_connection.init_vectors[0], data)
        self.tor_network.send_data(self.ip_address, servers[0].ip_address, port, data)

        """ initialize connection with third server """
        data = self.splitter.join(
            [dest_addr.encode(), new_connection.symmetric_keys[2], new_connection.init_vectors[2], b"end"])
        data = rsa_encrypt(servers[2].public_key, data)
        data = device.aes_encrypt(new_connection.symmetric_keys[1], new_connection.init_vectors[1], data)
        data = device.aes_encrypt(new_connection.symmetric_keys[0], new_connection.init_vectors[0], data)
        self.tor_network.send_data(self.ip_address, servers[0].ip_address, port, data)

    def onion_message(self, current_connection, message):
        blocks = device.split_to_packets(message.encode())
        for i, block in enumerate(blocks):
            self.connection_continue(current_connection,
                                     device.prepare_number(len(blocks) - i - 1) + self.splitter + block)

    def connection_continue(self, current_connection, data):
        for i in range(3)[::-1]:
            data = device.aes_encrypt(current_connection.symmetric_keys[i], current_connection.init_vectors[i], data)
        self.tor_network.send_data(self.ip_address, current_connection.source_addr, current_connection.source_port, data)

    def connection_finalize(self, current_connection):
        for i in range(1, 4)[::-1]:
            data = 128 * b"0"
            for j in range(i)[::-1]:
                data = device.aes_encrypt(current_connection.symmetric_keys[j], current_connection.init_vectors[j],
                                          data)
            self.tor_network.send_data(self.ip_address, current_connection.source_addr, current_connection.source_port, data)
        self.connection_list.remove(current_connection)

    def handle_self_connection(self, current_connection, raw_data):
        for i in range(3):
            try:
                raw_data = device.aes_decrypt(current_connection.symmetric_keys[i], current_connection.init_vectors[i],
                                              raw_data)
            except ValueError:
                return
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
        self.tor_network.send_data(self.ip_address, packet[0], packet[2], response)

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)
            self.log_write("sniff",
                           "{}:\tnew packet: src_addr: {}\tdst_addr: {}\tdst_port: {}\tdata_length: {}\traw_data: {}"
                           .format(self, packet[0], packet[1], packet[2], len(packet[3]), packet[3]))
            try:
                current_connection = next(filter(lambda c: c.source_port == packet[2], self.connection_list))
                current_connection.timeout = time()
                self.handle_self_connection(current_connection, packet[3])

            except StopIteration:
                self.handle_new_connection(packet)

    def execute_command(self, line):
        self.log_write("console", "{}$>> {}".format(str(self), line))
        commands = iter(device.parse_command_line(line))
        current = next(commands)
        if current == "show":
            return self.show_command(commands)
        if current == "onion":
            return self.onion_command(commands)
        if current == "message":
            return self.message_command(commands)
        if current == "change":
            return self.change_command(commands)
        if current == "":
            return "\n"
        return "Unknown command! Available: show, onion, message, change\n"

    def onion_command(self, commands):
        syntax = "Syntax: onion {init|message|finalize}\n"
        try:
            current = next(commands)
        except StopIteration:
            return syntax
        if current == "init":
            return self.init_command(commands)
        if current == "message":
            return self.message_command(commands)
        if current == "finalize":
            return self.finalize_command(commands)
        return "Unknown command! " + syntax

    def init_command(self, commands):
        syntax = "Syntax: onion init <pc_ip_address>\n"
        try:
            address = next(commands)
        except StopIteration:
            return syntax
        if not device.check_address_octets(address) or address in [srv.ip_address for srv in
                                                                   self.tor_network.server_list]:
            return "Not a valid PC address! " + syntax
        self.connection_init(address)
        return "Initialization sent.\n"

    def message_command(self, commands):
        try:
            number = next(commands)
            message = next(commands)
        except StopIteration:
            return 'Syntax: onion message <number> "<message_text>"\n'
        try:
            conn = self.connection_list[int(number)]
            self.onion_message(conn, message)
            return "Message sent.\n"
        except IndexError or ValueError:
            return "No such connection!\n"

    def finalize_command(self, commands):
        syntax = "Syntax: onion finalize <number>\n"
        try:
            number = next(commands)
        except StopIteration:
            return syntax
        try:
            conn = self.connection_list[int(number)]
            self.connection_finalize(conn)
            return "Connection finalized.\n"
        except IndexError or ValueError:
            return "No such connection! " + syntax
