'''
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend())
public_key = private_key.public_key()

print(public_key)

pempri = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

pempub = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open('private_key.txt', 'wb') as f:
    f.write(pempri)
with open('public_key.txt', 'wb') as f:
    f.write(pempub)
'''


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
    def __init__(self, ipAddress=None, torNetwork=None, publicKey=None, privateKey=None):
        self.ipAddress = ipAddress
        self.torNetwork = torNetwork
        self.publicKey = publicKey
        self.privateKey = privateKey
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
