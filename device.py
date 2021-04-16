import threading
from os import getcwd, path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def log_write(log_message):
    print(log_message)
    with open("logs.txt", "a+") as file:
        file.write(log_message)
        file.write("\n")


def aes_encrypt(key, init_vector, data):
    cipher = Cipher(algorithms.AES(key), modes.CBC(init_vector))
    encryptor = cipher.encryptor()
    return encryptor.update(data)


def aes_decrypt(key, init_vector, encrypted):
    cipher = Cipher(algorithms.AES(key), modes.CBC(init_vector))
    return cipher.decryptor().update(encrypted)


def test_address(address="", test_network=None):
    addresses = address.split(".")
    for i in addresses:
        if int(i) < 0 or int(i) > 255:
            print("Invalid address")
            return "0.0.0.0"
    for i in test_network.computer_list + test_network.server_list:
        if i.ip_address == address:
            print("Reused address")
            return "0.0.0.0"
    return address


def packets(message):
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


def generate_private(name):
    # generate private key
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
    private_txt = name + "_private_key.txt"
    keys_path = path.join(getcwd(), "keys", private_txt)
    # writing key to the file
    with open(keys_path, "wb") as file:
        file.write(pem)
    return private_key


def generate_public(name, private_key):
    # generate public key
    public_key = private_key.public_key()

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_txt = name + "_public_key.txt"
    keys_path = path.join(getcwd(), "keys", public_txt)
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


class Device(threading.Thread):
    def __init__(self, name=None, ip_address=None, tor_network=None):
        threading.Thread.__init__(self)
        self.name = name
        self.ip_address = test_address(ip_address, tor_network)
        self.tor_network = tor_network
        self.connection_list = []
        self.buffer = []
        try:
            self.private_key = load_private_key(self.name)
            self.public_key = load_public_key(self.name)
        except FileNotFoundError:
            self.private_key = generate_private(self.name)
            self.public_key = generate_public(self.name, self.private_key)
        self.run_event = threading.Event()
        self.run_event.set()

    def send_data(self, dest_addr, port, data):
        packet = [self.ip_address, dest_addr, port, data]
        for host in self.tor_network.server_list + self.tor_network.computer_list:
            if dest_addr == host.ip_address:
                host.buffer.append(packet)
                break

    def __str__(self):
        return self.name + "[" + self.ip_address + "]"
