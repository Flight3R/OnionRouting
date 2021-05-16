import os
import random
from time import time
from PIL import Image
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import asymmetric
import connection
import device
import torNetwork


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
        self.tor_network.computer_list.append(self)
        try:
            self.image = Image.open("pc.png")
        except FileNotFoundError:
            pass

    def remove(self):
        self.tor_network.computer_list.remove(self)
        self.run_event.clear()

    def connection_init(self, dest_addr):
        port = random.randint(4000, 65535)
        servers = random.sample(self.tor_network.server_list, 3)
        self.log_write("console", "servers: {}".format("\t".join([str(i) for i in servers])))
        new_connection = connection.Connection(servers[0].ip_address, port, None, dest_addr)
        new_connection.servers = servers
        # generate symmetric keys and initialization vectors
        for _ in range(3):
            new_connection.symmetric_keys.append(os.urandom(16))
            new_connection.init_vectors.append(os.urandom(16))

        self.connection_list.append(new_connection)

        # initialize connection with first server
        data = self.splitter.join(
            [servers[1].ip_address.encode(), new_connection.symmetric_keys[0], new_connection.init_vectors[0]])
        data = rsa_encrypt(servers[0].public_key, data)
        self.form_and_send_packet(servers[0].ip_address, port, data)

        # initialize connection with second server
        data = self.splitter.join(
            [servers[2].ip_address.encode(), new_connection.symmetric_keys[1], new_connection.init_vectors[1]])
        data = rsa_encrypt(servers[1].public_key, data)
        data = device.aes_encrypt(new_connection.symmetric_keys[0], new_connection.init_vectors[0], data)
        self.form_and_send_packet(servers[0].ip_address, port, data)

        # initialize connection with third server
        data = self.splitter.join(
            [dest_addr.encode(), new_connection.symmetric_keys[2], new_connection.init_vectors[2], b"end"])
        data = rsa_encrypt(servers[2].public_key, data)
        data = device.aes_encrypt(new_connection.symmetric_keys[1], new_connection.init_vectors[1], data)
        data = device.aes_encrypt(new_connection.symmetric_keys[0], new_connection.init_vectors[0], data)
        self.form_and_send_packet(servers[0].ip_address, port, data)

    def onion_message(self, current_connection, message):
        blocks = device.split_to_packets(message.encode())
        for i, block in enumerate(blocks):
            self.connection_continue(current_connection,
                                     device.prepare_number(len(blocks) - i - 1) + self.splitter + block)

    def connection_continue(self, current_connection, data):
        for i in range(3)[::-1]:
            data = device.aes_encrypt(current_connection.symmetric_keys[i], current_connection.init_vectors[i], data)
        self.form_and_send_packet(current_connection.source_addr, current_connection.source_port, data)

    def connection_finalize(self, current_connection):
        for i in range(1, 4)[::-1]:
            data = 128 * b"0"
            for j in range(i)[::-1]:
                data = device.aes_encrypt(current_connection.symmetric_keys[j], current_connection.init_vectors[j],
                                          data)
            self.form_and_send_packet(current_connection.source_addr, current_connection.source_port, data)
        self.connection_list.remove(current_connection)

    def handle_known_connection(self, current_connection, raw_data):
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

    def buffer_check(self):
        while len(self.buffer) != 0:
            packet = self.buffer.pop(0)
            self.log_write("sniff",
                           "{}:\tnew packet: src_addr: {}\tdst_addr: {}\tdst_port: {}\tdata_length: {}\traw_data: {}"
                           .format(self, packet[0], packet[1], packet[2], len(packet[3]), packet[3]))
            try:
                current_connection = next(filter(lambda c: c.source_port == packet[2], self.connection_list))
                current_connection.timeout = time()
                self.handle_known_connection(current_connection, packet[3])

            except StopIteration:
                message = packet[3]
                self.log_write("console", "{}:\treceived message from: {}:{}\tlength: {}\tmessage: {}"
                               .format(self, packet[0], packet[2], len(message), message))

# COMMAND EXECUTION BLOCK
    def execute_command(self, line):
        self.log_write("console", "{}$>> {}".format(str(self), line))
        commands = iter(device.parse_command_line(line))
        try:
            current = next(commands)
        except StopIteration:
            return "\n"
        if current == "show":
            return self.show_command(commands)
        if current == "onion":
            return self.onion_command(commands)
        if current == "message":
            return self.onion_msg_command(commands)
        if current == "change":
            return self.change_command(commands)
        if current == "":
            return "\n"
        return "Unknown command! Available: show, onion, message, change\n"

    def onion_command(self, commands):
        syntax = "Syntax: onion {init|msg|fin}\n"
        try:
            current = next(commands)
        except StopIteration:
            return syntax
        if current == "init":
            return self.init_command(commands)
        if current == "msg":
            return self.onion_msg_command(commands)
        if current == "fin":
            return self.onion_fin_command(commands)
        return "Unknown command! " + syntax

    def init_command(self, commands):
        syntax = "Syntax: onion init <pc_ip_address>\n"
        try:
            address = next(commands)
        except StopIteration:
            return syntax
        if not torNetwork.check_address_octets(address) or address in [srv.ip_address for srv in
                                                                       self.tor_network.server_list]:
            return "Not a valid PC address! " + syntax
        self.connection_init(address)
        return "Initialization sent.\n"

    def onion_msg_command(self, commands):
        syntax = 'Syntax: onion msg <number> "<message_text>"\n'
        try:
            number = next(commands)
            message = next(commands)
        except StopIteration:
            return syntax
        try:
            conn = self.connection_list[int(number)]
            self.onion_message(conn, message)
            return "Message sent.\n"
        except IndexError:
            return "No such connection!" + syntax
        except ValueError:
            return "No such connection!" + syntax

    def message_command(self, commands):
        syntax = 'Syntax: message <pc_ip_address> <port> "<message_text>"\n'
        try:
            address = next(commands)
            port = next(commands)
            message = next(commands)
        except StopIteration:
            return syntax
        self.form_and_send_packet(address, port, message)
        return ""

    def onion_fin_command(self, commands):
        syntax = "Syntax: onion fin <number>\n"
        try:
            number = next(commands)
        except StopIteration:
            return syntax
        try:
            conn = self.connection_list[int(number)]
            self.connection_finalize(conn)
            return "Connection finalized.\n"
        except IndexError:
            return "No such connection! " + syntax
        except ValueError:
            return "No such connection! " + syntax
