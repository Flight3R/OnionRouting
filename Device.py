from os import getcwd, path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_private(device_name=""):
    # generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())
    # serialise the key
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_txt = device_name + '_private_key.txt'
    keys_path = path.join(getcwd(), 'keys', private_txt)
    # writing key to the file
    with open(keys_path, 'wb') as f:
        f.write(pem)
    return private_key


def generate_public(device_name="", private_key=None):
    # generate public key
    public_key = private_key.public_key()

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_txt = device_name + '_public_key.txt'
    keys_path = path.join(getcwd(), 'keys', public_txt)
    with open(keys_path, 'wb') as f:
        f.write(pem)
    return public_key


def test_address(testAddress="", testNetwork=None):
    addresses = testAddress.split(".")
    for i in addresses:
        if int(i) < 0 or int(i) > 255:
            print("Invalid address")
            return "0.0.0.0"
    for i in testNetwork.computerList + testNetwork.serverList:
        if i.ipAddress == testAddress:
            print("Reused address")
            return "0.0.0.0"
    return testAddress


class Device:
    def __init__(self, name=None, ipAddress=None, torNetwork=None, publicKey=None, privateKey=None):
        self.name = name
        self.ipAddress = test_address(ipAddress, torNetwork)
        self.torNetwork = torNetwork
        self.privateKey = generate_private(name)
        self.publicKey = generate_public(name, self.privateKey)
        self.connectionList = []
        self.buffer = []

    def send_data(self, destAddr, identNo, data):
        packet = [self.ipAddress, destAddr, identNo, data]
        for host in self.torNetwork.serverList + self.torNetwork.computerList:
            if destAddr == host.ipAddress:
                host.buffer.append(packet)
                break

    def __str__(self):
        return self.ipAddress
