from os import mkdir
from shutil import rmtree
from time import sleep
import Computer
import Server
import TorNetwork

try:
    mkdir('keys')
except FileExistsError:
    pass

torNetwork = TorNetwork.TorNetwork([], [])

pc1 = Computer.Computer("PC1", "1.112.110.069", torNetwork)
pc2 = Computer.Computer("PC2", "11.22.33.44", torNetwork)
pc3 = Computer.Computer("PC3", "4.3.2.1", torNetwork)

srv1 = Server.Server("SRV1", "11.11.11.11", torNetwork)
srv2 = Server.Server("SRV2", "22.22.22.22", torNetwork)
srv3 = Server.Server("SRV3", "33.33.33.33", torNetwork)
srv4 = Server.Server("SRV4", "44.44.44.44", torNetwork)
srv5 = Server.Server("SRV5", "55.55.55.55", torNetwork)
srv6 = Server.Server("SRV6", "66.66.66.66", torNetwork)

torNetwork.serverList.append(srv1)
torNetwork.serverList.append(srv2)
torNetwork.serverList.append(srv3)
torNetwork.serverList.append(srv4)
torNetwork.serverList.append(srv5)
torNetwork.serverList.append(srv6)

pc1.connection_init("4.3.2.1")
print('––––––––––––––––––CONN INIT––––––––––––––––––––')

for i in range(10):
    for host in torNetwork.serverList + torNetwork.computerList:
        host.buffer_check()

print('––––––––––––––––––SENDING–––––––––––––––––––––')

msg = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut sit amet pellentesque dui. Sed tincidunt fringilla nibh eget sodales. Sed ipsum lorem, pulvinar nec dictum vitae, lobortis et orci accumsan."
for data in Computer.packets(msg):
    pc1.connection_continue(pc1.connectionList[0], data)

print('––––––––––––––––––MSG SENT––––––––––––––––––––')

for i in range(10):
    for host in torNetwork.serverList + torNetwork.computerList:
        host.buffer_check()

pc1.connection_finalize(pc1.connectionList[0])
print('––––––––––––––––––CONN FIN––––––––––––––––––––')

for i in range(10):
    for host in torNetwork.serverList + torNetwork.computerList:
        host.buffer_check()

#sleep(2)
#rmtree('keys')
