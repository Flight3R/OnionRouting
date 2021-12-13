# Onion Routing

Graphical application simulating encrypted communication in the manner of the real TOR network basing on modern and secure encryption algorithms .



## Usage

### Center field

In a default configuration the main panel consists of 2 sets of machines: computers and nodes. Computers are ment to be end-clients while nodes are used to establish a random chain of multiple layer encryption.

### Left panel

The user can choose a device by clicking or picking one from a list in the upper left corner of the main application window; operating machine will be marked by blue color and it's name with IP address will be automatically displayed in the drop menu.

The simulator allows the user to add new devices with a distinct name and an IP address.

The last option in left panel allows the user to stop real time routing and observe step-by-step how connections are managed and operated.

### Upper panel

After the working device have been choosen the user can access to it's terminal and issue control commands. 

All possible options are listed as `Syntax: …` after passing non recognized order. Every command has it's own parameters:

```
COMMANDS:
show
    address
    nodes
    connections
    connections <number>
    logs
        sniff
        console
onion
    init <ip_address>
    msg <number> "<message>"
    fin <number>
change
    name <new_name>
    address <new_address>
reset
    console
    sniff
```

 

## Principles of operation

On every computer (A) it is possible to create an encrypted multihop link to other computer (B) using series of nodes.

After picking a destination 3 nodes are drawn from the all-nodes list. It is important to notice that the simulator assumes common access to the public keys database for every device existing in the network. From that database all necessary keys are fetched to initialize the communication path: every node in a sequence recieves RSA-encrypted:

1. address of the next hop
2. generated symmetric key (AES (CBC))
3. generated initialization vector (AES (CBC))

Those values are stored for future usage. 

In practice we observe creation of 3 tunnels overlaping each other:

1. A → node 1
2. A → node 1 → node 2
3. A → node 1 → node 2 → node 3

Only the initializing computer has access to all 3 symmetric keys and is the only one who knows the tunnel path. In this manner symmetrically encrypted 3 layer tunnel is established.

Presented method makes it **impossible** for:

- First node to know who is the third node and the recipient
- Second node - who is the sender and the recipient 
- Third node - the sender and the first node

When a stable connection is created, computer A can send some user data. To prevent attacks based on packet length corelation computer A firstly splits long message into few parts and sends them in different packets. At the end of the tunnel, the third node joins messages back together and sends them to computer B. Moreover if the packet is shorter than a specified bit size, a standarized padding is added before encryption.

Simmilar procedure is performed when computer B replies in this communication.

NOTE: This program simulates encryption in the third layer OSI model only, thus data sent from the third node to the end computer are in plain text. In the real life there are higher layer protocols used for assuring message privacy (TLS).

To break the tunnel initializing computer (A) sends 3 packets (destined to 3 nodes) with a data sequence recognized by the nodes. Thanks to the properties of AES algorithm it is almost 100% guaranteed that this message will not accidentally repeat. When the node recieves this sequence it deletes the corresponding connection and keys from it's forwarding table.

The implementation of those operations guarantees constant packet size at every stage of communication, thus it is not possible for third person to distinguish which packet is an initialization, data carrage neither finalisation.

## Example of usage

![1](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/1.png)

Figure 1. Computer A specifies the recipient and initializes connection 

![2](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/2.png)

Figure 2. Packets recieved by the first node, NOTE: only the first packet is readable by this node - it contains: next hop address (figure 3), symmetric key and  init. vector.

![3](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/3.png)

Figure 3. Packets recieved by the second node.

![4](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/4.png)

Figure 4. Packets recieved by the third node.

![5](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/5.png)

Figure 5. No message has been send to destination PC so far; its log is yet empty.

![6](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/6.png)

Figure 6. Computer A sends message throuth the initialized tunnel (3 times simmetrically encrypted).

![7](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/7.png)

Figure 7. First node cannot see message content, it only removes it's layer of encryption.

![8](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/8.png)

Figure 8.The second node does the same.

![9](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/9.png)

Figure 9. Third node obtains plain text message by removing last layer of encryption and sends it to destination PC.

![10](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/10.png)

Figure 10. Computer B recieves the message, but from IP address it looks like the third node is the sender.

![11](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/11.png)

Figure 11. Computer B can respond to this message as the tunnel is mantained until max age count is reached. 

![12](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/12.png)

Figure 12. Every node on response's way back adds it's own layer of encryption. 

![13](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/13.png)

Figure 13. As above.

![14](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/14.png)

Figure 14. As above.

![15](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/15.png)

Figure 15. Computer A removes all 3 added layers of encryption and reads the response message.

![16](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/16.png)

Figure 16. When the tunnel is no longer ment to be used, it can be closed; 3 packet destined to the nodes are sent.

![17](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/17.png)

Figure 17. Although finalization packets travel in the same order though the nodes:

1. **A → node 1 → node 2 → node 3**
2. A → node 1 → node 2
3. A → node 1

 it is better to observe their functionality from the end: third node recieves it's finalization packet and flushes the connection.

![18](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/18.png)

Figure 18. The same is done with the connection in the second node (step 2).

![19](https://raw.githubusercontent.com/Flight3R/OnionRouting/master/readme-res/19.png)

Figure 19. Finally the first node recieves the special sequence and the entire tunnel is finalized.
