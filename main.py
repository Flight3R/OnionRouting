import Connection, Computer, Link, Server, TorNetwork

torNetwork = TorNetwork([],[])
pc1 = Computer("997.112.420.069", None, [])
torNetwork.computerList.append(pc1)
pc2 = Computer("11.22.33.44", None, [])
torNetwork.computerList.append(pc2)
pc3 = Computer("4.3.2.1", None, [])
torNetwork.computerList.append(pc3)

srv1 = Computer("997.112.420.069", None, [])
torNetwork.serverList.append(srv1)
srv2 = Computer("11.22.33.44", None, [])
torNetwork.serverList.append(srv2)
srv3 = Computer("4.3.2.1", None, [])
torNetwork.serverList.append(srv3)