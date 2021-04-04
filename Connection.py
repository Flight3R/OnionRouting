class Connection:
    def __init__(self, sourceAddr, sourcePort, destPort, destAddr):
        self.sourceAddr = sourceAddr
        self.sourcePort = sourcePort
        self.destPort = destPort
        self.destAddr = destAddr
        self.symmetricKeys = []
        self.initVectors = []
        self.dataBuffer = []
        self.isEndNode = False
