from time import time


class Connection:
    def __init__(self, source_addr, source_port, dest_port, dest_addr):
        self.source_addr = source_addr
        self.source_port = source_port
        self.dest_port = dest_port
        self.dest_addr = dest_addr
        self.symmetric_keys = []
        self.init_vectors = []
        self.data_buffer = []
        self.is_end_node = False
        self.timeout = time()
        self.servers = []

    def get_brief(self):
        return "src_addr: {}\tdst_addr: {}\n".format(str(self.source_addr), self.dest_addr)

    def get_detail(self):
        result = "source_address: {}\tdestination_address: {}\n" \
                   "source_port: {}\tdestination_port: {}\n" \
                   "symmetric_keys:\n".format(self.source_addr, self.dest_addr, self.source_port, self.dest_port)
        for key in self.symmetric_keys:
            result += str(key) + "\n"
        result += "initialization_vectors:\n"
        for vector in self.init_vectors:
            result += str(vector) + "\n"
        result += "is_end_node? {}\n".format(self.is_end_node)
        return result
