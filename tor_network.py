class TorNetwork:
    def __init__(self, server_list, computer_list):
        self.server_list = server_list
        self.computer_list = computer_list

    def allow_address(self, address):
        is_free = not any([host.ip_address == address for host in self.computer_list + self.server_list])
        return is_free

    def allow_name(self, name):
        is_free = not any([host.name == name for host in self.server_list + self.computer_list])
        return is_free
