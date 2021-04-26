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

for host in torNetwork.server_list + torNetwork.computer_list:
    host.start()
sleep(1)
print(pc1.execute_command("onion init 04.03.02.01"))
sleep(1)
print(pc1.execute_command('onion message 0 "wiadomosc do przeslania hehe dziala"'))
sleep(1)
print(pc1.execute_command("onion finalize 0"))
sleep(1)

for host in torNetwork.server_list + torNetwork.computer_list:
    host.run_event.clear()
    host.join()


# COMMANDS:
# show
#     address
#     servers
#     connections
#     connections <number>
#     logs
#
# onion
#     init <ip_address>
#     message <number> "<message>"
#     finalize <number>

# sleep(2)
# rmtree("keys")
