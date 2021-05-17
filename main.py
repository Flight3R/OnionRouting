from os import mkdir
from shutil import rmtree
from time import sleep
import computer
import node
import torNetwork


try:
    mkdir("keys")
except FileExistsError:
    pass

try:
    rmtree("logs")
except FileNotFoundError:
    pass

mkdir("logs")

tor_network = torNetwork.TorNetwork([], [])

pc1 = computer.Computer("PC1", "1.112.11.69", tor_network)
pc2 = computer.Computer("PC2", "11.22.33.44", tor_network)
pc3 = computer.Computer("PC3", "04.03.02.01", tor_network)

node1 = node.Node("NODE1", "11.11.11.11", tor_network)
node2 = node.Node("NODE2", "22.22.22.22", tor_network)
node3 = node.Node("NODE3", "33.33.33.33", tor_network)
node4 = node.Node("NODE4", "44.44.44.44", tor_network)
node5 = node.Node("NODE5", "55.55.55.55", tor_network)
node6 = node.Node("NODE6", "66.66.66.66", tor_network)

for host in tor_network.node_list + tor_network.computer_list:
    host.start()
######################################################################################################################
pc1.log_write("console", pc1.execute_command(""))
pc1.log_write("console", pc1.execute_command('onion message 0 "wiadomosc do przeslania hehe dziala"'))
sleep(1)
pc1.log_write("console", pc1.execute_command("onion finalize 0"))
sleep(1)

######################################################################################################################
for host in tor_network.node_list + tor_network.computer_list:
    host.run_event.clear()
    host.join()

# COMMANDS:
# show
#     address
#     servers
#     connections
#     connections <number>
#     logs
#         sniff
#         console
#
# onion
#     init <ip_address>
#     message <number> "<message>"
#     finalize <number>
# change
#     name <new_name>
#     address <new_address>
