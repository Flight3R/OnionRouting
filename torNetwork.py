from random import randint


def check_address_octals(address):
    try:
        is_correct = not any([int(octal) < 0 or int(octal) > 255 for octal in address.split(".")])
        return is_correct
    except ValueError:
        return False


def random_address():
    address = ""
    for _ in range(4):
        address += str(randint(0, 255)) + "."
    return address[:-1]


def strip_address_zeros(address):
    stripped_address = ""
    for octal in address.split("."):
        stripped_address += str(int(octal)) + "."
    return stripped_address[:-1]


class TorNetwork:
    def __init__(self, node_list, computer_list):
        self.node_list = node_list
        self.computer_list = computer_list

    def validate_address(self, address):
        if not check_address_octals(address):
            address = random_address()
        while not self.allow_address(address):
            address = random_address()
        return strip_address_zeros(address)

    def allow_address(self, address):
        try:
            stripped_address = strip_address_zeros(address)
        except ValueError:
            return False
        is_free = not any([host.ip_address == stripped_address for host in self.computer_list + self.node_list])
        return is_free

    def allow_name(self, name):
        is_free = not any([host.name == name for host in self.node_list + self.computer_list])
        return is_free

    def serve_packet_transfer(self, packet):
        for host in self.node_list + self.computer_list:
            if packet[1] == host.ip_address:
                host.buffer.append(packet)
                break
        else:
            raise ConnectionError("Cannot reach host!")
