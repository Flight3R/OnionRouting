import Computer
import Server
import TorNetwork

torNetwork = TorNetwork.TorNetwork([], [])

pc1 = Computer.Computer("997.112.420.069", torNetwork)
pc2 = Computer.Computer("11.22.33.44", torNetwork)
pc3 = Computer.Computer("4.3.2.1", torNetwork)


srv1 = Server.Server("11.11.11.11", torNetwork, [])
srv2 = Server.Server("22.22.22.22", torNetwork, [])
srv3 = Server.Server("33.33.33.33", torNetwork, [])
srv4 = Server.Server("44.44.44.44", torNetwork, [])
srv5 = Server.Server("55.55.55.55", torNetwork, [])
srv6 = Server.Server("55.55.55.55", torNetwork, [])


print(torNetwork.serverList[5].ipAddress)
print(torNetwork.serverList[4].ipAddress)
