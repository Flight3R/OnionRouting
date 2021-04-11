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
