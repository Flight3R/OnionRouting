from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

private_key1 = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

private_key2 = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

e = private_key1.public_key().public_numbers().e
n = private_key1.public_key().public_numbers().n
e2 = private_key2.public_key().public_numbers().e
n2 = private_key2.public_key().public_numbers().n

d = private_key1.private_numbers().d
d2 = private_key2.private_numbers().d

input = 'encrypt-me'

toenc1 = int.from_bytes(input.encode(), 'big')
crypted_number = pow(toenc1, e, n)
# –––––––––––––––––––––––––––––––––––––––––––––––––
crypted_data = str(crypted_number)
crypted_data_headed = "header-" + crypted_data

toenc2 = int.from_bytes(crypted_data_headed.encode(), 'big')
crypted_number2 = pow(toenc2, e2, n2)

# –––––––––––––––––––––––––––––––––––––––––––––––––

decrypted2 = pow(crypted_number2, d2, n)
decrypted_data2 = str(decrypted2.to_bytes(256, 'big'))

print("dec2:", decrypted_data2)

# –––––––––––––––––––––––––––––––––––––––––––––––––'''

decrypted = pow(int(decrypted2), d, n)
decrypted_data = str(decrypted.to_bytes(256, 'big'))
print('dec:', decrypted_data)