class TorNetwork:
    def __init__(self, server_list, computer_list):
        self.server_list = server_list
        self.computer_list = computer_list

    def allow_address(self, address):
        return not any([host.ip_address == address for host in self.computer_list + self.server_list])
