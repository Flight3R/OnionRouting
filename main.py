from os import mkdir
from shutil import rmtree
from time import sleep
import Computer
import Server
import TorNetwork

mkdir('keys')
sleep(5)
torNetwork = TorNetwork.TorNetwork([], [])

pc1 = Computer.Computer("PC1", "997.112.420.069", torNetwork)
pc2 = Computer.Computer("PC2", "11.22.33.44", torNetwork)
pc3 = Computer.Computer("PC3", "4.3.2.1", torNetwork)

srv1 = Server.Server("SRV1", "11.11.11.11", torNetwork, [])
srv2 = Server.Server("SRV2", "22.22.22.22", torNetwork, [])
srv3 = Server.Server("SRV3", "33.33.33.33", torNetwork, [])
srv4 = Server.Server("SRV4", "44.44.44.44", torNetwork, [])
srv5 = Server.Server("SRV5", "55.55.55.55", torNetwork, [])
srv6 = Server.Server("SRV6", "66.66.66.66", torNetwork, [])

torNetwork.serverList.append(srv1)
torNetwork.serverList.append(srv2)
torNetwork.serverList.append(srv3)
torNetwork.serverList.append(srv4)
torNetwork.serverList.append(srv5)
torNetwork.serverList.append(srv6)
# '''
pc1.onion_message("4.3.2.1", 123456, "mam/nadzieje/ze/dziala")

for i in range(10):
    for host in torNetwork.serverList + torNetwork.computerList:
        host.buffer_check()
# '''
sleep(5)
rmtree('keys')
