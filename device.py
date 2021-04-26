import threading
from re import findall
from random import randint
from os import getcwd, path
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


def test_address(address="", test_network=None):
    try:
        if any([int(octal) < 0 or int(octal) > 255 for octal in address.split(".")]):
            address = random_address()
    except ValueError:
        address = random_address()
    while any([host.ip_address == address for host in test_network.computer_list+test_network.server_list]):
        address = random_address()
    return address


def random_address():
    address = ""
    for _ in range(4):
        address += str(randint(0, 255)) + "."
    return address[:-1]


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
        arg_list = line.removesuffix(" "+typo).split(" ") + [typo[1:-1]]
    except IndexError:
        return line.removesuffix(" ").split(" ")
    return arg_list


class Device(threading.Thread):
    def __init__(self, name="None", ip_address="None", tor_network=None):
        threading.Thread.__init__(self)
        self.name = name
        self.ip_address = test_address(ip_address, tor_network)
        self.tor_network = tor_network
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
        self.run_event.set()

    def send_data(self, dest_addr, port, data):
        packet = [self.ip_address, dest_addr, port, data]
        for host in self.tor_network.server_list + self.tor_network.computer_list:
            if dest_addr == host.ip_address:
                host.buffer.append(packet)
                break

    def log_write(self, file_type, log_message):
        if file_type == "console":
            print(log_message)
        with open(path.join(getcwd(), "logs", file_type + "_logs.txt"), "a+") as file:
            file.write(log_message)
            file.write("\n")
        with open(path.join(getcwd(), "logs", file_type + "_" + self.name + "_logs.txt"), "a+") as file:
            file.write(log_message)
            file.write("\n")

    def execute_command(self, line):
        commands = iter(parse_command_line(line))
        current = next(commands)
        if current == "show":
            return self.show_command(commands)
        return "Unknown command! Available: show\n"

    def show_command(self, commands):
        try:
            current = next(commands)
        except StopIteration:
            return ">>> address, servers, connections, logs\n"
        if current == "address":
            return self.ip_address
        if current == "servers":
            return self.get_servers()
        if current == "connections":
            return self.get_connection(commands)
        if current == "logs":
            return self.get_logs(commands)
        return "Unknown command! Available: address, servers, connections, logs\n"

    def get_servers(self):
        result = ""
        for server in self.tor_network.server_list:
            result += server.ip_address + "\n"
        return result

    def get_connection(self, commands):
        try:
            conn_number = next(commands)
            try:
                return self.connection_list[int(conn_number)].get_detail()
            except ValueError or IndexError:
                return "No such connection!\n"
        except StopIteration:
            result = ""
            for i, conn in enumerate(self.connection_list):
                result += "{}\t{}\n".format(i, conn.get_brief())
            return result

    def get_logs(self, commands):
        try:
            current = next(commands)
        except StopIteration:
            return "\n"
        try:
            with open(path.join(getcwd(), "logs", "sniff_" + self.name + "_logs.txt"), "r") as file:
                result = file.read()
            return result
        except FileNotFoundError:
            return "No such file!\n"

    def __str__(self):
        return self.name + "[" + self.ip_address + "]"
