import threading
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
    padder = padding.PKCS7(1024).padder()
    padded_data = padder.update(message)
    padded_data += padder.finalize()
    data_list = []
    for i in range(len(padded_data) // 128):
        k = 128 * i
        data_list.append(padded_data[k:k + 128])
    return data_list


def unpad(data):
    try:
        unpadder = padding.PKCS7(1024).unpadder()
        message = unpadder.update(data)
        message += unpadder.finalize()
        return message
    except ValueError:
        return data


class Device(threading.Thread):
    def __init__(self, name=None, ip_address=None, tor_network=None):
        threading.Thread.__init__(self)
        self.name = name
        self.ip_address = test_address(ip_address, tor_network)
        self.tor_network = tor_network
        self.connection_list = []
        self.buffer = []
        try:
            self.load_private_key()
            self.load_public_key()
        except FileNotFoundError:
            self.generate_private()
            self.generate_public()
        self.run_event = threading.Event()
        self.run_event.set()

    def generate_private(self):
        # generate private key
        self.privateKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024,
            backend=default_backend())
        # serialise the key
        pem = self.privateKey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        private_txt = self.name + '_private_key.txt'
        keys_path = path.join(getcwd(), 'keys', private_txt)
        # writing key to the file
        with open(keys_path, 'wb') as file:
            file.write(pem)

    def generate_public(self):
        # generate public key
        self.publicKey = self.privateKey.public_key()

        pem = self.publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        public_txt = self.name + '_public_key.txt'
        keys_path = path.join(getcwd(), 'keys', public_txt)
        with open(keys_path, 'wb') as file:
            file.write(pem)

    def send_data(self, dest_addr, port, counter, data):
        packet = [self.ip_address, dest_addr, port, counter, data]
        for host in self.tor_network.server_list + self.tor_network.computer_list:
            if dest_addr == host.ip_address:
                host.buffer.append(packet)
                break

    def load_private_key(self):
        path_name = path.join(getcwd(), 'keys', (self.name + '_private_key.txt'))
        with open(path_name, "rb") as key_file:
            self.privateKey = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

    def load_public_key(self):
        path_name = path.join(getcwd(), 'keys', (self.name + '_public_key.txt'))
        with open(path_name, "rb") as key_file:
            self.publicKey = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

    def __str__(self):
        return self.name + "[" + self.ip_address + "]"
