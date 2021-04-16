from os import mkdir
from shutil import rmtree
from time import sleep
import computer
import server
import tor_network


try:
    mkdir("keys")
except FileExistsError:
    pass

try:
    rmtree("logs")
except FileNotFoundError:
    pass

mkdir("logs")


torNetwork = tor_network.TorNetwork([], [])

pc1 = computer.Computer("PC1", "1.112.11.69", torNetwork)
pc2 = computer.Computer("PC2", "11.22.33.44", torNetwork)
pc3 = computer.Computer("PC3", "04.03.02.01", torNetwork)

srv1 = server.Server("SRV1", "11.11.11.11", torNetwork)
srv2 = server.Server("SRV2", "22.22.22.22", torNetwork)
srv3 = server.Server("SRV3", "33.33.33.33", torNetwork)
srv4 = server.Server("SRV4", "44.44.44.44", torNetwork)
srv5 = server.Server("SRV5", "55.55.55.55", torNetwork)
srv6 = server.Server("SRV6", "66.66.66.66", torNetwork)

torNetwork.server_list.append(srv1)
torNetwork.server_list.append(srv2)
torNetwork.server_list.append(srv3)
torNetwork.server_list.append(srv4)
torNetwork.server_list.append(srv5)
torNetwork.server_list.append(srv6)

for host in torNetwork.server_list + torNetwork.computer_list:
    host.start()

print("––––––––––––––––––CONN INIT––––––––––––––––––––")
pc1.connection_init("04.03.02.01")

sleep(1)

print("––––––––––––––––––MSG SENT––––––––––––––––––––")
MESSAGE = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec commodo metus vitae elit volutpat consectetur. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Praesent malesuada dolor id libero dapibus, eget volutpat erat vestibulum. Morbi vel nulla libero."
pc1.onion_message(pc1.connection_list[0], MESSAGE)

sleep(1)

print("––––––––––––––––––CONN FIN––––––––––––––––––––")
pc1.connection_finalize(pc1.connection_list[0])

sleep(1)

for host in torNetwork.server_list + torNetwork.computer_list:
    host.run_event.clear()
    host.join()

print("––––––––––––––––––TERM––––––––––––––––––––––––")

# sleep(2)
# rmtree("keys")
