import threading
from re import findall
from time import sleep, time
from os import getcwd, path, rename, remove
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def aes_encrypt(key, init_vector, data):
    cipher = Cipher(algorithms.AES(key), modes.CBC(init_vector))
    encryptor = cipher.encryptor()
    return encryptor.update(data)


def aes_decrypt(key, init_vector, encrypted):
    cipher = Cipher(algorithms.AES(key), modes.CBC(init_vector))
    return cipher.decryptor().update(encrypted)


def split_to_packets(message):
    padder = padding.PKCS7(960).padder()
    padded_data = padder.update(message)
    padded_data += padder.finalize()
    data_list = []
    for i in range(len(padded_data) // 120):
        k = 120 * i
        data_list.append(padded_data[k:k + 120])
    return data_list


def prepare_number(number):
    string = str(number).encode()
    zeros = b"0" * (3 - len(string))
    string = zeros + string
    return string


def remove_padding(data):
    try:
        unpadder = padding.PKCS7(960).unpadder()
        message = unpadder.update(data)
        message += unpadder.finalize()
        return message
    except ValueError:
        return data


def generate_private_key(name):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,
        backend=default_backend())
    # serialise the key
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_filename = name + "_private_key.txt"
    keys_path = path.join(getcwd(), "keys", private_filename)
    # writing key to the file
    with open(keys_path, "wb") as file:
        file.write(pem)
    return private_key


def generate_public_key(name, private_key):
    public_key = private_key.public_key()

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_filename = name + "_public_key.txt"
    keys_path = path.join(getcwd(), "keys", public_filename)
    # writing key to the file
    with open(keys_path, "wb") as file:
        file.write(pem)
    return public_key


def load_private_key(name):
    path_name = path.join(getcwd(), "keys", (name + "_private_key.txt"))
    with open(path_name, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key


def load_public_key(name):
    path_name = path.join(getcwd(), "keys", (name + "_public_key.txt"))
    with open(path_name, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key


def parse_command_line(line):
    try:
        typo = findall("\".*\"", line)[0]
        arg_list = line.removesuffix(typo).strip().split() + [typo[1:-1]]
    except IndexError:
        return line.strip().split()
    return arg_list


class Device(threading.Thread):
    def __init__(self, name, ip_address, tor_network):
        threading.Thread.__init__(self)
        self.name = name
        self.tor_network = tor_network
        self.ip_address = tor_network.validate_address(ip_address)
        self.connection_list = []
        self.buffer = []
        self.splitter = b"<<-<<"
        try:
            self.private_key = load_private_key(self.name)
            self.public_key = load_public_key(self.name)
        except FileNotFoundError:
            self.private_key = generate_private_key(self.name)
            self.public_key = generate_public_key(self.name, self.private_key)
        self.run_event = threading.Event()

    def __str__(self):
        return self.name + "[" + self.ip_address + "]"

    def log_write(self, file_type, log_message):
        if file_type == "console":
            print(log_message)
        with open(path.join(getcwd(), "logs", file_type + ".txt"), "a+") as file:
            file.write(log_message)
            file.write("\n")
        with open(path.join(getcwd(), "logs", file_type + "_" + self.name + ".txt"), "a+") as file:
            file.write(log_message)
            file.write("\n")

    def buffer_check(self):
        pass

    def connections_timeout_check(self):
        for conn in self.connection_list:
            if time() - conn.timeout > 6000:
                self.connection_list.remove(conn)

    def run(self):
        while self.run_event.is_set():
            self.connections_timeout_check()
            self.buffer_check()
            sleep(0.1)

    def form_and_send_packet(self, dest_addr, port, data):
        packet = [self.ip_address, dest_addr, port, data]
        try:
            self.tor_network.serve_packet_transfer(packet)
        except ConnectionError as exception:
            self.log_write("console", "{}: {}".format(self, exception))

    def remove_dirs(self):
        dirs = [path.join(getcwd(), "logs", "console_" + self.name + ".txt"),
                path.join(getcwd(), "logs", "sniff_" + self.name + ".txt"),
                path.join(getcwd(), "keys", (self.name + "_public_key.txt")),
                path.join(getcwd(), "keys", (self.name + "_private_key.txt"))]
        for _dir in dirs:
            try:
                remove(_dir)
            except FileNotFoundError:
                pass

    # COMMAND EXECUTION BLOCK
    def execute_command(self, line):
        self.log_write("console", "{}$>> {}".format(str(self), line))
        commands = iter(parse_command_line(line))
        try:
            current = next(commands)
        except StopIteration:
            return ""
        if current == "show":
            return self.show_command(commands)
        if current == "change":
            return self.change_command(commands)
        if current == "reset":
            return self.reset_command(commands)
        return "Unknown command! Available: show, change\n"

    def reset_command(self, commands):
        syntax = "Syntax: reset {console|sniff|all}\n"
        try:
            current = next(commands)
        except StopIteration:
            return syntax
        if current == "console":
            try:
                remove(path.join(getcwd(), "logs", "console_" + self.name + ".txt"))
            except FileNotFoundError:
                pass
            return ""
        if current == "sniff":
            try:
                remove(path.join(getcwd(), "logs", "sniff_" + self.name + ".txt"))
            except FileNotFoundError:
                pass
            return ""
        if current == "all":
            try:
                remove(path.join(getcwd(), "logs", "console_" + self.name + ".txt"))
            except FileNotFoundError:
                pass
            try:
                remove(path.join(getcwd(), "logs", "sniff_" + self.name + ".txt"))
            except FileNotFoundError:
                pass
            return ""
        return "Unknown command! " + syntax

    def change_command(self, commands):
        syntax = "Syntax: change {name|address}\n"
        try:
            current = next(commands)
        except StopIteration:
            return syntax
        if current == "name":
            return self.change_name(commands)
        if current == "address":
            return self.change_address(commands)
        return "Unknown command! " + syntax

    def change_name(self, commands):
        try:
            current = next(commands)
        except StopIteration:
            return "Syntax: change name <new_name>\n"
        if not self.tor_network.allow_name(current):
            return "Name already in use! Choose different one!\n"
        rename(path.join(getcwd(), "logs", "console_" + self.name + ".txt"),
               path.join(getcwd(), "logs", "console_" + current + ".txt"))
        try:
            rename(path.join(getcwd(), "logs", "sniff_" + self.name + ".txt"),
                   path.join(getcwd(), "logs", "sniff_" + current + ".txt"))
        except FileNotFoundError:
            pass
        rename(path.join(getcwd(), "keys", self.name + "_public_key.txt"),
               path.join(getcwd(), "keys", current + "_public_key.txt"))
        rename(path.join(getcwd(), "keys", self.name + "_private_key.txt"),
               path.join(getcwd(), "keys", current + "_private_key.txt"))
        self.name = current
        return "Name changed.\n"

    def change_address(self, commands):
        try:
            current = next(commands)
        except StopIteration:
            return "Syntax: change address <new_address>\n"
        if not self.tor_network.allow_address(current):
            return "Not a valid address!\n"
        if len(self.connection_list) != 0:
            return "Cannot change address with open connections!\n"
        self.ip_address = current
        return "Address changed.\n"

    def show_command(self, commands):
        syntax = "Syntax: show {name|address|nodes|connections|logs}\n"
        try:
            current = next(commands)
        except StopIteration:
            return syntax
        if current == "name":
            return self.name + "\n"
        if current == "address":
            return self.ip_address + "\n"
        if current == "nodes":
            return self.get_nodes()
        if current == "connections":
            return self.get_connection(commands)
        if current == "logs":
            return self.get_logs(commands)
        return "Unknown command! " + syntax

    def get_nodes(self):
        result = ""
        for node in self.tor_network.node_list:
            result += node.ip_address + "\n"
        return result

    def get_connection(self, commands):
        try:
            conn_number = next(commands)
            try:
                return self.connection_list[int(conn_number)].get_detail()
            except ValueError:
                return "No such connection!\n"
            except IndexError:
                return "No such connection!\n"
        except StopIteration:
            result = ""
            for i, conn in enumerate(self.connection_list):
                result += "{}\t{}".format(i, conn.get_brief())
            return result

    def get_logs(self, commands):
        syntax = "Syntax: show logs {console|sniff}\n"
        try:
            current = next(commands)
        except StopIteration:
            return syntax
        try:
            if current == "console" or current == "sniff":
                with open(path.join(getcwd(), "logs", current + "_" + self.name + ".txt"), "r") as file:
                    result = file.read()
                return result
            return "Unknown command! " + syntax
        except FileNotFoundError:
            return "There are no logs.\n"
