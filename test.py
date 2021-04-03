
from cryptography.hazmat.primitives.ciphers import algorithms

#algorithms.AES.

'''from cryptography.hazmat.backends import default_backend
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
input_int_str = str(int.from_bytes(input.encode(), 'big'))
print(input_int_str)

toenc1 = int.from_bytes(input_int_str.encode(), 'big')
print("n:", n)
C1 = pow(toenc1, e, n)
C1_str = str(C1)
C1_str_head = C1_str
print(C1_str_head)
# –––––––––––––––––––––––––––––––––––––––––––––––––
toenc2 = int.from_bytes(C1_str_head.encode(), 'big')
C2 = pow(toenc2, e2, n2)
print('C2:', C2)
# –––––––––––––––––––––––––––––––––––––––––––––––––
D2 = pow(C2, d2, n2)
if toenc2 > n2:
    print('hurra')
D2_str = D2.to_bytes(256, 'big')#.lstrip('\x00')
print("dec2:", D2_str)
# –––––––––––––––––––––––––––––––––––––––––––––––––
todec = int(D2_str)
D1 = pow(todec, d, n)
decrypted_data = str(D1.to_bytes(256, 'big'))
print('dec:', decrypted_data)'''