import Connection, Computer, Link, Server, TorNetwork

torNetwork = TorNetwork.TorNetwork([],[])

pc1 = Computer.Computer("997.112.420.069", torNetwork)
pc2 = Computer.Computer("11.22.33.44", torNetwork)
pc3 = Computer.Computer("4.3.2.1", torNetwork)
torNetwork.computerList.append(pc1)
torNetwork.computerList.append(pc2)
torNetwork.computerList.append(pc3)

srv1 = Server.Server("11.11.11.11", torNetwork, [])
srv2 = Server.Server("22.22.22.22", torNetwork, [])
srv3 = Server.Server("33.33.33.33", torNetwork, [])
srv4 = Server.Server("44.44.44.44", torNetwork, [])
srv5 = Server.Server("55.55.55.55", torNetwork, [])
srv6 = Server.Server("66.66.66.66", torNetwork, [])
torNetwork.serverList.append(srv1)
torNetwork.serverList.append(srv2)
torNetwork.serverList.append(srv3)
torNetwork.serverList.append(srv4)
torNetwork.serverList.append(srv5)
torNetwork.serverList.append(srv6)

pc1.onionMessage("4.3.2.1", 123456, "mam/nadzieje/ze/dziala")

for i in range(10):
    for host in torNetwork.serverList + torNetwork.computerList:
        host.bufferCheck()
